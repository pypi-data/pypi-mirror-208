from typing import Tuple, Any, Dict

from jsonmerge import merge as json_merge
from jsonschema import validate as json_validate
from sqlalchemy import select
from sqlalchemy.orm.attributes import set_attribute, get_attribute
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_json import NestedMutableDict


def _extract_model_params(defaults, **kwargs):
    # src: Copy from sqlalchemy_get_or_create python package with no modification.
    # sqlalchemy_get_or_create package is now removed as it is SQLAlchemy 1.x compatible only
    defaults = defaults or {}
    ret = {}
    ret.update(kwargs)
    ret.update(defaults)
    return ret


def _without_sa_instance_state(object) -> Dict:
    defaults = _defaults(object)
    defaults.pop("_sa_instance_state", None)
    return defaults


def _defaults(object) -> Dict:
    defaults = dict(object.__dict__)
    return defaults


def duplicate_object(object, **kwargs):
    defaults = _without_sa_instance_state(object)
    params = _extract_model_params(defaults, **kwargs)
    value = type(object)(**params)
    return value


class JSONMergeException(Exception):
    pass


class JSONValidationException(Exception):
    pass


def json_fields_operation(
    object: object = None,
    defaults: Dict = None,
    json: Dict = None,
    validate: bool = True,
    merge: bool = True,
):
    o_defaults = _without_sa_instance_state(object)

    for k, v in defaults.items():
        o_v = o_defaults.get(k, None)

        if o_v is None and v is None:
            continue

        if v is None:
            continue

        if not isinstance(v, NestedMutableDict):
            continue

        merge_k = json.get(k, {}).get("merge", None)
        schema_k = json.get(k, {}).get("schema", None)

        if merge and merge_k is None:
            raise NotImplementedError(f"Merge has 'merging' schema missing for key {k}:{json}")
        else:
            params = list(filter(lambda x: x is not None, [o_v or {}, v] + [merge_k]))
            if len(params) > 2:
                # params: v, v2, optional merge_strategy
                try:
                    o_v = json_merge(*params)
                except BaseException as e:
                    raise JSONMergeException(f"key: {k}. Merge params: {params}") from e

        if validate and schema_k is None:
            raise NotImplementedError(
                f"Validate has 'validation' schema missing for key {k}:{json}"
            )
        else:
            # Validate json object or throw exception
            try:
                json_validate(instance=o_v, schema=schema_k)
            except BaseException as e:
                raise JSONValidationException(
                    f"key:{k}.\njson:{o_v}.\nschema:{schema_k}\nError:{str(e)}"
                ) from e

        setattr(object, k, o_v)


async def _create_object_from_params(
    session: AsyncSession = None,
    model: object = None,
    lookup: Dict = None,
    params: Dict = None,
    lock: bool = False,
):
    # src: Copy from sqlalchemy_get_or_create python package with modification
    # to support AsyncSession
    obj = model(**params)
    session.add(obj)
    try:
        async with session.begin_nested() as savepoint:
            await session.flush()
    except IntegrityError as e:
        await session.rollback()
        query = select(model).filter_by(**lookup)
        if lock:
            query = query.with_for_update()
        try:
            obj = (await session.execute(query)).scalars().one()
        except NoResultFound:
            raise
        else:
            return obj, False
    else:
        return obj, True


async def _get_or_create(session, model, defaults=None, **kwargs):
    # src: Copy from sqlalchemy_get_or_create python package with modification
    # to support AsyncSession
    try:
        query = select(model).filter_by(**kwargs)
        return (await session.execute(query)).scalars().one(), False
    except NoResultFound:
        params = _extract_model_params(defaults, **kwargs)
        return await _create_object_from_params(
            session=session, model=model, lookup=kwargs, params=params
        )


async def _update_or_create_object_json(
    session: AsyncSession = None,
    model: object = None,
    defaults: Dict = None,
    json: Dict = {},
    **kwargs,
) -> Tuple[Any, bool]:
    # src: Copied from sqlalchemy_get_or_create package with modification to
    # support json merging + json validation + AsyncSession

    obj = None
    created = False
    defaults = defaults or {}

    try:
        query = select(model).with_for_update().filter_by(**kwargs)
        obj = (await session.execute(query)).scalars().one()
    except NoResultFound:
        pass

    if obj is None:
        params = _extract_model_params(defaults, **kwargs)
        obj = model(**params)

        # Validate only json field in new object
        json_fields_operation(object=obj, defaults=defaults, json=json, validate=True, merge=False)

        session.add(obj)
        await session.flush()
        return obj, True
    else:
        # Merge+Validate json fields in non new object
        json_fields_operation(object=obj, defaults=defaults, json=json, validate=True, merge=True)

        # Merge non json fields in non new object
        for k, v in defaults.items():
            if not isinstance(v, NestedMutableDict):
                if v != get_attribute(obj, k):
                    set_attribute(obj, k, v)

        session.add(obj)
        await session.flush()
        return obj, False


async def get_or_create_object(
    session: AsyncSession = None, model: object = None, object: object = None, **kwargs
) -> Tuple[Any, bool]:
    if object is not None:
        defaults = _without_sa_instance_state(object)
    else:
        defaults = {}
    return await _get_or_create(session, model, defaults=defaults, **kwargs)


async def update_or_create_object_json(
    session: AsyncSession = None,
    model: object = None,
    object: object = None,
    json: Dict = {},
    **kwargs,
) -> Tuple[Any, bool]:
    defaults = _without_sa_instance_state(object)
    return await _update_or_create_object_json(
        session=session, model=model, defaults=defaults, json=json, **kwargs
    )
