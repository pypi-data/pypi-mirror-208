from unittest.mock import patch
import pydash

from hestia_earth.orchestrator.strategies.merge.merge_list import merge

class_path = 'hestia_earth.orchestrator.strategies.merge.merge_list'
version = '1'


@patch(f"{class_path}.update_node_version", side_effect=lambda _v, n: n)
def test_merge_new_node(*args):
    old_node = {
        'term': {'@id': 'old-term'},
        'value': 1
    }
    new_node = {
        'term': {'@id': 'new-term'},
        'value': 2
    }
    result = merge([old_node], [new_node], version)
    assert result == [old_node, new_node]


@patch(f"{class_path}.merge_node", side_effect=lambda a, b, *args: pydash.objects.merge({}, a, b))
@patch(f"{class_path}.update_node_version", side_effect=lambda _v, n: n)
def test_merge_existing_node(*args):
    term = {'@id': 'term'}

    node_type = 'Site'
    model = {'key': 'measurements'}

    # with different value => should merge
    old_node = {
        'term': term,
        'value': 1
    }
    new_node = {
        'term': term,
        'value': 2
    }
    result = merge([old_node], [new_node], version, model=model, node_type=node_type)
    assert len(result) == 1

    # with different depths => should not merge
    result = merge([{
        **old_node,
        'depthUpper': 100
    }], [{
        **new_node,
        'depthUpper': 50
    }], version, model=model, node_type=node_type)
    assert len(result) == 2

    node_type = 'Cycle'
    model = {'key': 'emissions'}

    # with same inputs => should merge
    result = merge([{
        **old_node,
        'inputs': [{'@id': 'input-1'}]
    }], [{
        **new_node,
        'inputs': [{'@id': 'input-1'}]
    }], version, model=model, node_type=node_type)
    assert len(result) == 1

    # with different inputs => should not merge
    result = merge([{
        **old_node,
        'inputs': [{'@id': 'input-1'}]
    }], [{
        **new_node,
        'inputs': [{'@id': 'input-2'}]
    }], version, model=model, node_type=node_type)
    assert len(result) == 2

    result = merge([{
        **old_node,
        'inputs': [{'@id': 'input-1'}]
    }], [{
        **new_node,
        'inputs': [{'@id': 'input-1'}, {'@id': 'input-2'}]
    }], version, model=model, node_type=node_type)
    assert len(result) == 2


@patch(f"{class_path}.merge_node", side_effect=lambda a, b, *args: pydash.objects.merge({}, a, b))
@patch(f"{class_path}.update_node_version", side_effect=lambda _v, n: n)
def test_merge_existing_node_skip_same_term(*args):
    term = {'@id': 'term'}
    node_type = 'Site'
    model = {'key': 'measurements'}

    old_node = {
        'term': term,
        'value': 1
    }
    new_node = {
        'term': term,
        'value': 2
    }
    result = merge([old_node], [new_node], version, model, {'skipSameTerm': True}, node_type)
    assert len(result) == 1
    assert result[0]['value'] == 1
