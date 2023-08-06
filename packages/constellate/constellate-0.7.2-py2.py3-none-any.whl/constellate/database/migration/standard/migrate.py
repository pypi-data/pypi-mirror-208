import itertools
import logging
import socket
from functools import partial, reduce
from pathlib import Path
from typing import List, Iterable, Callable, Dict, Optional, Tuple, Any

import attr
import networkx as nx
import pendulum
import psutil
import sqlalchemy.schema
import stackeddag.graphviz as sg
from networkx import DiGraph, topological_sort
from sqlalchemy import select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Awaitable, AsyncGenerator, AsyncIterator

from constellate.cryptography.digest.hexadecimal import hexadecimal
from constellate.database.migration.metadata import read_sql_migration_metadata
from constellate.database.migration.migrationcontext import (
    MigrationContext,
    MigrationStepFile,
    ConnectionContext,
)
from constellate.database.migration.tablecontext import TableContext
from constellate.database.migration.constant import ScriptType, MigrationKind, Mark, MigrationAction
from constellate.database.migration.standard.table import (
    MigrationR,
    MigrationVersionR,
    MigrationActivityR,
    MigrationLockR,
)
from constellate.database.sqlalchemy.execution.execute import (
    execute_scalars_all_iterable,
    execute_scalars_one_or_none,
    execute_discard_result,
)
from constellate.database.sqlalchemy.expression.schema.setsearchpath import SetSearchPathSchema
from constellate.datatype.enum.enum import has_flag
from constellate.storage.filesystem.tmpfs.rambacked import mkf_tmpfs


async def _setup_migration_tables(
    session: AsyncSession = None,
    table_context: TableContext = None,
    logger: logging.Logger = None,
) -> None:
    logger.debug("Creating missing migration internal tables.")
    # Create missing tables
    for table in [
        table_context.version,
        table_context.migration,
        table_context.activity,
        table_context.lock,
    ]:
        await session.execute(sqlalchemy.schema.CreateTable(table.__table__, if_not_exists=True))


async def _mark_migrated(
    session: AsyncSession = None,
    migration: MigrationR = None,
    logger: logging.Logger = None,
    table_context: TableContext = None,
    track_migration: bool = True,
) -> None:
    activity = table_context.activity(
        migration_hash=migration.migration_hash,
        migration_id=migration.migration_id,
        action=migration.action,
        username=psutil.Process().username(),  # src: https://stackoverflow.com/a/65224170/219728
        hostname=socket.gethostname(),
        created_at=migration.applied_at,
        kind=migration.kind,
    )
    session.add(activity)
    if track_migration:
        if migration.action == MigrationAction.UPGRADE:
            session.add(migration)
        elif migration.action == MigrationAction.DOWNGRADE:

            @execute_discard_result(stmt=True)
            async def _delete_migration(
                migration_hash: str = None, *args, **kwargs
            ) -> Optional[MigrationR]:
                return delete(table_context.migration).where(
                    table_context.migration.migration_hash == migration_hash
                )

            await _delete_migration(migration_hash=migration.migration_hash)
        else:
            raise NotImplementedError()

    logger.debug(
        f"Completed migration step file {migration}. Migration activity recorded in {table_context.activity.__tablename__} as: {activity}"
    )


async def _read_applied_migrations(
    session: AsyncSession = None, table_context: TableContext = None
) -> List[MigrationStepFile]:
    @execute_scalars_all_iterable
    async def _read_migrations(*args, **kwargs) -> List[MigrationR]:
        return select(table_context.migration).order_by(table_context.migration.applied_at.asc())

    pairs = {}

    def _to_migration_step_file(m: MigrationR) -> MigrationStepFile:
        parent = None if m.parent_hash is None else pairs.get(m.parent_hash)
        sf = MigrationStepFile(kind=m.kind, file=Path(m.migration_id), parent=parent)
        pairs[m.migration_hash] = sf
        return sf

    return [_to_migration_step_file(m) for m in await _read_migrations(session=session)]


async def _read_available_migrations(
    migration_context: MigrationContext = None,
) -> List[MigrationStepFile]:
    return list(
        itertools.chain.from_iterable([step.step_files for step in migration_context.steps])
    )


def _find_missing_migrations(
    applied_migrations: List[MigrationStepFile] = None,
    available_migrations: List[MigrationStepFile] = None,
    migration_context: MigrationContext = None,
    logger: logging.Logger = None,
) -> Iterable[MigrationStepFile]:
    @attr.s(kw_only=True, auto_attribs=True)
    class _MigrationPlan:
        applied: bool
        graph: nx.DiGraph
        migrations: List[MigrationStepFile]
        validations: Dict[str, bool]

    applied_plan = _MigrationPlan(
        applied=True, graph=nx.DiGraph(), migrations=applied_migrations, validations=None
    )
    available_plan = _MigrationPlan(
        applied=False, graph=nx.DiGraph(), migrations=available_migrations, validations=None
    )

    def _build_plan_from_migrations(plan: _MigrationPlan) -> None:
        g = plan.graph
        for m in plan.migrations:
            # Add node
            g.add_node(
                m.file.name,
                m=m,
                label=m.file.name,  # label: required by sg.fromDotFile(...) to display node names
            )
            # Add edge
            if m.parent is not None:
                g.add_edge(m.file.name, m.parent.file.name)

    def _validate_graph(graph: DiGraph) -> Dict:
        is_empty = nx.is_empty(graph)
        is_dag = nx.is_directed_acyclic_graph(graph)
        is_linear = not is_empty and is_dag and nx.is_branching(graph)
        return {"non_empty": not is_empty, "directed_acyclic_graph": is_dag, "linear": is_linear}

    def _render_plan(plan: _MigrationPlan) -> str:
        header = f"{migration_context.action.value.capitalize()} migration plan {'applied' if plan.applied else 'to be applied'}:"
        migration_path = " -> ".join(map(lambda m: m.file.name, plan.migrations))
        migration_path2 = ""
        with mkf_tmpfs() as f:
            try:
                if not nx.is_empty(plan.graph):
                    nx.drawing.nx_agraph.write_dot(plan.graph, f)
                    graphiz = f.read_text()
                    ascii = sg.fromDotFile(f)
                    migration_path2 = f"ASCII:\n{ascii}\n\nGraphiz:\n{graphiz}"
                else:
                    migration_path2 = "Migraton plan empty. Nothing to migrate."
            except BaseException as e:
                migration_path2 = f"ERROR: no Graphiz plan rendered. {e}"

            migration_path = f"(START) {migration_path} -> (END)"
            return f"{header}\n{migration_path}\n{migration_path2}"

    # Build available migration plan
    _build_plan_from_migrations(plan=available_plan)
    available_plan.validations = _validate_graph(graph=available_plan.graph)
    if not all(available_plan.validations.values()):
        plan = _render_plan(plan=available_plan)
        raise ValueError(f"Migration plan is invalid: {available_plan.validations}. {plan}")

    # Build applied migration plan
    _build_plan_from_migrations(plan=applied_plan)
    applied_plan.validations = _validate_graph(graph=applied_plan.graph)

    # Build delta migration plan
    applied_graph = applied_plan.graph.copy()
    available_graph = available_plan.graph.copy()

    applied_inside_available_graph = set(applied_graph.nodes).intersection(
        set(available_graph.nodes)
    )
    unapplied_inside_available_graph = set(available_graph.nodes).difference(
        applied_inside_available_graph
    )
    current_source_migration_incompleted = len(unapplied_inside_available_graph) > 0

    applied_outside_available_graph = set(applied_graph.nodes).difference(
        applied_inside_available_graph
    )
    multi_source_migration_found = len(applied_outside_available_graph) > 0

    if multi_source_migration_found:
        # Modify applied graph as if there was a single migration source
        applied_graph.remove_nodes_from(applied_outside_available_graph)

        if migration_context.dry.skip_migration_continuity_check:
            logger.warning(
                f"Available migration files and applied migration files have no common migration files. "
                f"Likely running a migration from another directory than the last migration run"
            )
    else:
        # Case: current source migration files may or may not be applied relative to already applied migration files
        pass

    applied_graph.add_nodes_from(available_plan.graph)
    # difference(G,H)'s G and H requires same set of nodes
    delta_graph = nx.algorithms.difference(available_plan.graph, applied_graph)

    if migration_context.action == MigrationAction.UPGRADE:
        # Reverse graph edge:
        # - Input lists successor migration script FIRST and then the ancestor of said script second
        delta_graph = delta_graph.reverse(copy=False)
    elif migration_context.action == MigrationAction.DOWNGRADE:
        delta_graph = delta_graph
    else:
        raise NotImplementedError()

    # Unfroze delta graph
    delta_graph = delta_graph.copy()

    # Find (if present) the migration files common to the applied set of files and yet to be applied set of files
    applied_subgraph = applied_graph.edge_subgraph(applied_graph.edges)
    delta_subgraph = delta_graph.edge_subgraph(delta_graph.edges)
    common_graph = nx.operators.intersection_all([applied_subgraph, delta_subgraph])
    total_common_nodes = len(common_graph.nodes)
    if total_common_nodes > 1:
        raise ValueError(
            f"Applied graph and delta graph can have at most 1 common file. Found: {list(common_graph.nodes)}"
        )
    elif total_common_nodes == 1:
        # This is the 2nd or more migration
        common_file = list(common_graph.nodes)[0]
    else:
        # This is the 1st migration
        common_file = None

    if common_file is not None:
        # Common file f was already applied (from previous migration run)
        # Remove edge (f-1, f) from list of migration to perform
        edges = delta_graph.out_edges(nbunch=common_file, data=False, default=None)
        for index, edge in enumerate(list(edges)):
            if index > 0:
                raise ValueError(
                    f"At most 1 common file between migration files applied and yet to be applied must exist. Found: {edges}"
                )
            delta_graph.remove_edge(*edge)

    # Remove migration files not linked to another (ie files already migrated)
    files = [
        f
        for f in list(delta_graph.nodes)
        if len(list(delta_graph.predecessors(f))) == 0 and len(list(delta_graph.successors(f))) == 0
    ]
    delta_graph.remove_nodes_from(files)

    validations = _validate_graph(graph=delta_graph)
    delta_plan = _MigrationPlan(
        applied=False,
        graph=delta_graph,
        migrations=list(topological_sort(delta_graph)),
        validations=validations,
    )

    # Replace each migration file with its MigrationStepFile equivalent
    pairs = {sf.file.name: sf for sf in available_migrations}
    delta_plan.migrations = [pairs.get(file_name) for file_name in delta_plan.migrations]

    logger.info(_render_plan(plan=delta_plan))
    return delta_plan.migrations


async def _build_migration_plan(
    session: AsyncSession = None,
    migration_context: MigrationContext = None,
    table_context: TableContext = None,
    logger: logging.Logger = None,
) -> AsyncGenerator[Tuple[MigrationR, MigrationStepFile], None]:
    step_files = _find_missing_migrations(
        applied_migrations=await _read_applied_migrations(
            session=session, table_context=table_context
        ),
        available_migrations=await _read_available_migrations(migration_context=migration_context),
        migration_context=migration_context,
        logger=logger,
    )

    hexadecimal_sha256 = partial(hexadecimal, family="sha256")

    def to_migration(sf: MigrationStepFile = None) -> MigrationR:
        return MigrationR(
            migration_hash=hexadecimal_sha256(value=sf.file.read_text(encoding="utf-8")),
            migration_id=sf.file.name,
            kind=sf.kind or migration_context.kind or MigrationKind.UNKNOWN,
            applied_at=None,  # date set when migration file is being executed
            action=migration_context.action,
            parent_hash=None,
        )

    @execute_scalars_one_or_none(stmt=True)
    async def _read_migration(migration_id: str = None, *args, **kwargs) -> Optional[MigrationR]:
        return select(table_context.migration).where(
            table_context.migration.migration_id == migration_id
        )

    last_pm = None
    for index, sf in enumerate(step_files):
        psf = sf.parent
        pm = (
            (
                last_pm
                or (await _read_migration(session=session, migration_id=psf.file.name))
                or to_migration(sf=psf)
            )
            if psf is not None
            else None
        )
        m = (await _read_migration(session=session, migration_id=sf.file.name)) or to_migration(
            sf=sf
        )
        m.parent_hash = pm.migration_hash if pm is not None else None
        last_pm = m
        yield (m, sf)


async def _execute_sql_file(
    sf: MigrationStepFile = None,
    migration_context: MigrationContext = None,
    connection_context: ConnectionContext = None,
    user_context: Any = None,
    session: AsyncSession = None,
    logger: logging.Logger = None,
) -> None:
    if migration_context.dry.skip_executing_script:
        logger.debug(f"Skipped {migration_context.action.value.capitalize()}: {sf.file}")
        return

    _, _, statements = read_sql_migration_metadata(file=sf.file, directive_names=[])
    for stmt in statements:
        msg = f"{migration_context.action.value.capitalize()} SQL on {sf.schema if sf.schema is not None else 'default'} schema:\n{stmt}"
        try:
            logger.debug(msg)
            if sf.schema is not None:
                await session.execute(
                    SetSearchPathSchema(names=sf.schema, ignore_unsupported_database_types="sqlite")
                )
            await session.execute(text(stmt))
        except BaseException as e:
            msg += f"\nERROR:\n{e}"
            raise RuntimeError(msg) from e


async def _execute_python_file(
    sf: MigrationStepFile = None,
    migration_context: MigrationContext = None,
    connection_context: ConnectionContext = None,
    user_context: Any = None,
    session: AsyncSession = None,
    logger: logging.Logger = None,
) -> None:
    if migration_context.dry.skip_executing_script:
        logger.debug(f"Skipped {migration_context.action.value.capitalize()}: {sf.file}")
        return

    pairs = {MigrationAction.UPGRADE: "upgrade", MigrationAction.DOWNGRADE: "downgrade"}
    fn_name = pairs.get(migration_context.action, None)
    if fn_name is None:
        raise NotImplementedError(
            f"Missing python function for {migration_context.action}. Valid function names per action are: {pairs}"
        )

    fn = getattr(sf.py_module, fn_name)
    if fn is None:
        raise ValueError(
            f"Python function {fn_name} for action {migration_context.action} missing in file {sf.file}"
        )

    await session.flush()
    msg = f"{migration_context.action.value.capitalize()} with python file on {sf.schema if sf.schema is not None else 'default'} schema:"
    if sf.schema is not None:
        await session.execute(
            SetSearchPathSchema(names=sf.schema, ignore_unsupported_database_types="sqlite")
        )
    await fn(connection_context=connection_context, user_context=user_context, logger=logger)


async def _execute_unknown_file(sf: MigrationStepFile = None, **kwargs) -> None:
    raise NotImplementedError(f"{sf.file} is not a supported migration file")


async def _execute_migration_plan(
    session: AsyncSession = None,
    migration_context: MigrationContext = None,
    table_context: TableContext = None,
    user_context: Any = None,
    migrations: AsyncIterator[Tuple[MigrationR, MigrationStepFile]] = None,
    logger: logging.Logger = None,
) -> None:
    fn_impl = {ScriptType.PYTHON: _execute_python_file, ScriptType.SQL: _execute_sql_file}

    try:
        for migration, sf in migrations:
            migration.applied_at = pendulum.now(tz="utc")
            fn = fn_impl.get(sf.type, _execute_unknown_file)
            await fn(
                session=session,
                migration_context=migration_context,
                connection_context=migration_context.connection_context,
                user_context=user_context,
                sf=sf,
                logger=logger,
            )
            await _mark_migrated(
                session=session,
                migration=migration,
                track_migration=has_flag(sf.mark_behaviour, Mark.MARK_MIGRATION),
                table_context=table_context,
                logger=logger,
            )

            populated_up_to_file = migration_context.dry.table_populated_up_to_file
            if sf.file.name == populated_up_to_file:
                break

    except BaseException as e:
        logger.error(f"{migration_context.action.value.capitalize()} plan failed.", exc_info=1)
        raise e


_LOCK_ID = 1


async def _lock(session: AsyncSession, table_context: TableContext = None) -> None:
    # Every application will try to insert a lock with id 1. At most one will succeed
    # when trying to commit the transaction.
    lock = table_context.lock(id=_LOCK_ID)
    session.add(lock)
    await session.flush()


async def _unlock(session: AsyncSession, table_context: TableContext = None) -> None:
    @execute_scalars_one_or_none(stmt=True)
    async def _read_lock(id: int = None, *args, **kwargs) -> Optional[MigrationLockR]:
        return select(table_context.lock).where(table_context.lock.id == id)

    @execute_discard_result(stmt=True)
    async def _delete_lock(id: int = None, *args, **kwargs) -> Optional[MigrationLockR]:
        return delete(table_context.lock).where(table_context.lock.id == id)

    lock = await _read_lock(session=session, id=_LOCK_ID)
    if lock is not None:
        await _delete_lock(session=session, id=_LOCK_ID)
        await session.flush()


_schema_version: int = 0


async def _migrate_library_schema(
    session: AsyncSession,
    table_context: TableContext = None,
) -> None:
    # Add migration table schema version
    @execute_scalars_one_or_none(stmt=True)
    async def _read_current_version(*args, **kwargs):
        return select(table_context.version).limit(1)

    @execute_scalars_one_or_none(stmt=True)
    async def _delete_current_version(*args, version: int = None, **kwargs):
        return delete(table_context.version).where(table_context.version.version == version)

    current_version = await _read_current_version(session=session)
    next_version = table_context.version(version=_schema_version, created_at=pendulum.now(tz="utc"))
    if current_version is None:
        session.add(next_version)
    elif current_version.version < _schema_version:
        await _delete_current_version(version=current_version)
        session.add(next_version)


async def _migrate_user_schema(
    session: AsyncSession,
    migration_context: MigrationContext = None,
    user_context: Any = None,
    table_context: TableContext = None,
    logger: logging.Logger = None,
) -> None:
    migrations = [
        m
        async for m in _build_migration_plan(
            session=session,
            migration_context=migration_context,
            table_context=table_context,
            logger=logger,
        )
    ]
    await _execute_migration_plan(
        session=session,
        migration_context=migration_context,
        table_context=table_context,
        user_context=user_context,
        migrations=migrations,
        logger=logger,
    )


_TABLE_CONTEXT = TableContext(
    migration=MigrationR,
    activity=MigrationActivityR,
    version=MigrationVersionR,
    lock=MigrationLockR,
)


async def migrate(
    migration_context: MigrationContext = None,
    user_context: Any = None,
    fn_create_session: Callable[[MigrationContext], Awaitable[AsyncSession]] = None,
    logger: logging.Logger = None,
    table_context: TableContext = _TABLE_CONTEXT,
) -> bool:
    def _migration_files_found(migration_context: MigrationContext = None) -> bool:
        return (
            reduce(lambda total, mcs: total + len(mcs.step_files), migration_context.steps, 0) > 0
        )

    if not _migration_files_found(migration_context=migration_context):
        logger.warning(f"No files to migrate in migration context: {migration_context}.")
        return

    # Setup library migrations when missing
    async with fn_create_session(migration_context=migration_context) as session:
        await _setup_migration_tables(
            session=session,
            logger=logger,
            table_context=table_context,
        )

    # Run library migration scripts
    async with fn_create_session(migration_context=migration_context) as session:
        try:
            await _lock(session=session, table_context=table_context)
            await _migrate_library_schema(session=session, table_context=table_context)
        except BaseException as e:
            raise e
        finally:
            await _unlock(session=session, table_context=table_context)

    # Run user migration scripts
    async with fn_create_session(migration_context=migration_context) as session:
        try:
            migration_context.connection_context.session = session
            await _lock(session=session, table_context=table_context)
            await _migrate_user_schema(
                session=session,
                migration_context=migration_context,
                table_context=table_context,
                user_context=user_context,
                logger=logger,
            )
        except BaseException as e:
            raise e
        finally:
            await _unlock(session=session, table_context=table_context)
