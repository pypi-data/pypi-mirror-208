from typing import Union

from SPARQLBurger.SPARQLSyntaxTerms import Triple
from rdflib.plugins.stores.sparqlstore import _node_to_sparql
from rdflib.term import Node


def _to_sparql_node(value: Union[str, Node] = None) -> str:
    if isinstance(value, Node):
        return _node_to_sparql(value)
    return value


def to_triple(subject: Node = None, predicate: Node = None, object: Node = None):
    return Triple(
        subject=_to_sparql_node(subject),
        predicate=_to_sparql_node(predicate),
        object=_to_sparql_node(object),
    )
