import importlib
import itertools
from collections import ChainMap
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import List, Union, Type, Any, Dict, Tuple

from constellate.database.migration.constant import (
    DEFAULT_CONTEXT_STEP_FILE_NAME,
    INVALID_MIGRATION_SCRIPT_FILE_NAMES,
    DEFAULT_POST_APPLY_FILE_NAMES,
    MigrationKind,
    Mark,
    MigrationAction,
    INVALID_MIGRATION_DIRECTORY_NAMES,
)
from constellate.database.migration.metadata import read_sql_migration_metadata
from constellate.database.migration.migrationcontext import (
    MigrationContext,
    MigrationStepContext,
    MigrationStepFile,
)
from constellate.resource.resource import get_folder


def _collect_migration_files(
    migration_dir: Path = None,
    suffixes: List[str] = ["*.sql", "*.py"],
    invalid_files_names: List[str] = None,
    post_apply_files_names: List[str] = None,
    action: MigrationAction = None,
) -> List[Path]:
    def sort_alphabetically(files: List[Path] = None) -> List[Path]:
        return sorted(files, key=lambda f: str(f))

    def _keep_migration_file(infix: str, whitelist_files_names: List[str], file: Path) -> bool:
        discard_non_migration_file = lambda name: str(name).endswith(file.name)
        accept_special_migration_file = lambda name: str(name) == file.name

        invalidated = any(map(discard_non_migration_file, invalid_files_names))
        specialized = len(whitelist_files_names) > 0 and any(
            map(accept_special_migration_file, whitelist_files_names)
        )
        acceptable = infix in file.name
        return not invalidated and (specialized or acceptable)

    def _place_post_update_file_last(files: List[Path] = None) -> List[Path]:
        post_files = list(filter(lambda f: f.name in post_apply_files_names, files))
        if len(post_files) > 1:
            raise ValueError(
                f"Up to 1 post update file named {post_apply_files_names} can exist across all migration step. Usually placed in the last migration step folder to be executed"
            )

        post_file = next(iter(post_files), None)
        if post_file is not None:
            files.remove(post_file)
            files.append(post_file)
        return files

    infix = (
        {MigrationAction.UPGRADE: "up", MigrationAction.DOWNGRADE: "down"}
        .get(action, "unknown")
        .lower()
    )
    files = [list(Path(migration_dir).glob(suffix)) for suffix in suffixes]
    files = filter(
        partial(_keep_migration_file, f".{infix}.", post_apply_files_names),
        itertools.chain.from_iterable(files),
    )
    files = list(sort_alphabetically(files=files))
    return _place_post_update_file_last(files=files)


def migration_steps(
    migration_context: MigrationContext = None,
    migration_context_step_file_name: str = DEFAULT_CONTEXT_STEP_FILE_NAME,
) -> None:
    _by_name = lambda x: str(x)

    migration_dir = get_folder(
        root_pkg_name=migration_context.root_pkg_name.__package__,
        directory=migration_context.directory,
    )
    step_directories = [f for f in migration_dir.iterdir() if f.is_dir()]
    step_directories = sorted(step_directories, key=_by_name)

    def _keep_valid_migration_directories(f: Path) -> bool:
        return f.name not in INVALID_MIGRATION_DIRECTORY_NAMES

    step_directories = list(filter(_keep_valid_migration_directories, step_directories))

    steps = []
    previous_migration_files = []
    for step_directory in step_directories:
        step_context_file = next(
            iter([f for f in step_directory.glob(f"*{migration_context_step_file_name}")]), None
        )

        if step_context_file is None:
            raise NotImplementedError(
                f"Missing migration context step file: {migration_context_step_file_name}"
            )

        step_context = _load_module(file=step_context_file)
        kind = _read_property(step_context, "kind", (MigrationKind,), migration_context.kind)
        schema = _read_property(
            step_context, "schema", (str, type(List[str])), migration_context.schema
        )
        dir = _read_property(step_context, "migration_dir", (Path,), step_directory)

        invalid_files_names = list(
            set(INVALID_MIGRATION_SCRIPT_FILE_NAMES + [step_context_file.name])
        )
        migration_files = _collect_migration_files(
            migration_dir=dir,
            invalid_files_names=invalid_files_names,
            post_apply_files_names=DEFAULT_POST_APPLY_FILE_NAMES,
            action=migration_context.action,
        )

        def _read_file_metadata(file: Path) -> Tuple[Any, Dict]:
            metadata = {
                "schema": None,
                "kind": None,
                "transactional": None,
                "requires": [],
            }

            directive_names = list(metadata.keys())
            if file.name.endswith(".py"):
                pymodule = _load_module(file=file)
                directives = {d: getattr(pymodule, d, None) for d in directive_names}
            elif file.name.endswith(".sql"):
                pymodule = None
                directives, leading_comment, statements = read_sql_migration_metadata(
                    file=file, directive_names=directive_names
                )
            else:
                raise NotImplementedError()

            provided_metadata = {k: v for k, v in directives.items() if v is not None}
            return pymodule, dict(ChainMap(metadata, provided_metadata))

        def validate_metadata(metadata: Dict = None) -> None:
            depends = metadata.get("requires")
            if len(depends) > 1:
                raise NotImplementedError("Migration script can have up to 1 dependencies only")

        def build_step_files(
            migration_files: List[Path] = None, previous_migration_files: List[Path] = None
        ) -> List[MigrationStepFile]:
            step_files = {}
            previous_mf = None
            for index, mf in enumerate(migration_files):
                if mf.name in step_files:
                    raise ValueError(
                        f"2+ migration files share the same name {mf.name}. Only 1 must be specified"
                    )

                pymodule, metadata = _read_file_metadata(file=mf)
                validate_metadata(metadata=metadata)

                default_parent = (
                    previous_mf.name
                    if previous_mf is not None
                    else previous_migration_files[-1].name
                    if len(previous_migration_files) > 0
                    else None
                )
                parent = next(iter(metadata.get("requires")), default_parent)

                mark_behaviour = Mark.MARK_ACTIVITY
                if not mf.name in DEFAULT_POST_APPLY_FILE_NAMES:
                    mark_behaviour |= Mark.MARK_MIGRATION

                step_files[mf.name] = MigrationStepFile(
                    file=mf,
                    transactional=metadata.get("transactional"),
                    # Parent is converted into MigrationStepFile instance later at runtime
                    parent=parent,
                    kind=metadata.get("kind", None) or kind,
                    schema=metadata.get("schema", None) or schema,
                    py_module=pymodule,
                    mark_behaviour=mark_behaviour,
                )
                previous_mf = mf

            return list(step_files.values())

        steps.append(
            MigrationStepContext(
                **{
                    "kind": kind,
                    "schema": schema,
                    "step_files": build_step_files(
                        migration_files=migration_files,
                        previous_migration_files=previous_migration_files,
                    ),
                }
            )
        )

        previous_migration_files = migration_files

    _resolve_parent_migration_steps(steps=steps)
    migration_context.steps = steps


def _resolve_parent_migration_steps(steps: List[MigrationStepContext] = None):
    pairs = {}

    # Build list of resolved/unresolved files
    for step in steps:
        for step_file in step.step_files:
            # Mark each own file as resolved
            pairs[step_file.file.name] = step_file
            # Mark each parent as unresolved
            # if isinstance(step_file.parent, str):
            #     pairs[step_file.parent] = None

    # Resolve parents
    for index, step in enumerate(steps):
        for step_file in step.step_files:
            if step_file.parent is None:
                continue

            step_file.parent = pairs.get(step_file.parent, None)
            if step_file.parent is None and index > 0:
                raise ValueError(
                    f"{step_file.file.name} requires {step_file.parent} but it does not exists"
                )

    return None


def _load_module(file: Path = None) -> ModuleType:
    module_name = file.stem

    spec = importlib.util.spec_from_file_location(module_name, file)
    step_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(step_module)
    return step_module


def _read_property(
    obj: Union[object, Dict], key: str, types: Tuple[Type, ...], default: Any
) -> str:
    if isinstance(obj, Dict):
        value = obj.get(key, default)
    else:
        value = getattr(obj, key, default)
    if not isinstance(value, (type(None), *types)):
        raise ValueError()
    return value
