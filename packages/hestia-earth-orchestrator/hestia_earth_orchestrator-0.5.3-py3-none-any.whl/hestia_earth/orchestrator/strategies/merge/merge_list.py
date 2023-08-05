import pydash
from hestia_earth.schema import UNIQUENESS_FIELDS
from hestia_earth.utils.tools import flatten

from hestia_earth.orchestrator.utils import _non_empty_list, update_node_version
from .merge_node import merge as merge_node

_BLANK_NODE_MATCH_PROPERTIES = list(set(flatten([flatten(fields.values()) for fields in UNIQUENESS_FIELDS.values()])))


def _matching_properties(model: dict, node_type: str):
    return UNIQUENESS_FIELDS.get(node_type, {}).get(model.get('key'), _BLANK_NODE_MATCH_PROPERTIES)


def _match_list_el(source: list, dest: list, key: str):
    src_values = _non_empty_list([x.get(key) for x in source])
    dest_values = _non_empty_list([x.get(key) for x in dest])
    return sorted(src_values) == sorted(dest_values)


def _match_el(source: dict, dest: dict, same_methodModel: bool, model: dict, node_type: str):
    def match(key: str):
        keys = key.split('.')
        src_value = pydash.objects.get(source, key)
        dest_value = pydash.objects.get(dest, key)
        is_list = len(keys) == 2 and (
            isinstance(pydash.objects.get(source, keys[0]), list) or
            isinstance(pydash.objects.get(dest, keys[0]), list)
        )
        return _match_list_el(
            pydash.objects.get(source, keys[0], []),
            pydash.objects.get(dest, keys[0], []),
            keys[1]
        ) if is_list else (dest_value is None or src_value == dest_value)

    properties = _matching_properties(model, node_type)
    return all([match(key) for key in properties + (['methodModel'] if same_methodModel else [])])


def _find_match_el_index(values: list, el: str, same_methodModel: bool, model: dict, node_type: str):
    return next((i for i in range(len(values)) if _match_el(values[i], el, same_methodModel, model, node_type)), None)


def merge(source: list, dest: list, version: str, model: dict = {}, merge_args: dict = {}, node_type: str = ''):
    source = source if source is not None else []

    # only merge node if it has the same `methodModel`
    same_methodModel = merge_args.get('sameMethodModel', False)
    # only merge if the
    skip_same_term = merge_args.get('skipSameTerm', False)

    for el in _non_empty_list(dest):
        source_index = _find_match_el_index(source, el, same_methodModel, model, node_type)
        if source_index is None:
            source.append(update_node_version(version, el))
        elif not skip_same_term:
            source[source_index] = merge_node(source[source_index], el, version, model, merge_args)
    return source
