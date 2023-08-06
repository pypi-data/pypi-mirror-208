from typing import Union, Tuple, Dict
from .base import Neo4jBaseConnector
from pymantra.statics import (
    EDGE_TYPES, NODE_TYPES,
    EDGE_TYPE_NAMES,
    NODE_TYPES_BY_EDGE, forbidden_node_characters,
    EDGE_ATTRIBUTES
)
from .exceptions import IncorrectEdgeType, IncorrectNodeType


class Neo4jGenerator(Neo4jBaseConnector):
    """
    Utility class to populate a neo4j database
    """
    def __init__(
        self, uri: str, auth: Union[Tuple[str, str], None] = None, **kwargs
    ):
        """
        Parameters
        ----------
        uri: str
            URI to connect to. Usually something like 'bolt://127.0.0.7:7687'

        auth: 2-tuple, Optional
            User credentials for the database. First element is the username,
            second the corresponding password. For more details see the
            neo4j.GraphDatabase.driver API documentation

        kwargs:
            Keyword arguments to pass to neo4j.GraphDatabase.driver

        Raises
        ------
        ConnectionError
            If database is not reachable with the given parameters
        """
        super(Neo4jGenerator, self).__init__(uri, auth, **kwargs)
        for node_type in NODE_TYPES:
            # uniqueness constraint for node labels
            self.session.run(
                "CREATE CONSTRAINT constraint_name IF NOT EXISTS FOR "
                f"(n:{node_type}) REQUIRE n.nodeLabel IS UNIQUE"
            )

    def reset(self):
        """
        Wiping the entire database
        """
        self.session.run("MATCH (n) DETACH DELETE n")

    # ======= auxiliaries ======= #
    @staticmethod
    def _add_attributes_(statement, item_type, **attrs):
        if attrs:
            statement += " ON CREATE SET "
            for i, (attr, value) in enumerate(attrs.items()):
                statement += f"{item_type}.{attr} = {value}"
                if i == len(attrs) - 1:
                    statement += ";"
                else:
                    statement += ", "
        else:
            statement += ";"
        return statement

    @staticmethod
    def _match_node_query_(name, node_type, node_name):
        return f"MATCH ({name}:{node_type} {{nodeLabel: '{node_name}'}})"

    @staticmethod
    def _validate_node(name: str) -> str:
        return_name = name
        for char in forbidden_node_characters:
            return_name = return_name.replace(char, "")
        return return_name

    # ======= node insertion ======= #
    def add_node(
        self, name: str, node_type: str, node_attrs: Dict[str, any] = None,
        **attrs
    ):
        """
        Adding a node to the database

        Parameters
        ----------
        name: str
            nodeLabel of the node to add

        node_type: str
            Type of the node. Should be one of the types set in
            `utils.NODE_TYPES`

        node_attrs: Dict[str, any]
            Additional attributes as a dictionary. Used mutually exclusive
            with **attrs.

        attrs: optional
            Additional attributes as keyword arguments to be passed for the
            node. All attributes will appear as strings in the database
        """
        if node_type not in NODE_TYPES:
            raise IncorrectNodeType(
                f"Unkown node type {node_type}. "
                f"Valid node types are '{NODE_TYPES}'"
            )
        statement = f"MERGE (node:{node_type} " \
                    f"{{nodeLabel: '{self._validate_node(str(name))}'}})"
        if node_attrs is None:
            self._add_attributes_(statement, 'node', **attrs)
        else:
            self._add_attributes_(statement, 'node', **node_attrs)
        self.session.run(statement)

    def nodes_from_csv(
        self, file: str, node_type: str, node_attrs: Dict[str, str] = None
    ):
        """
        Efficiently adding a bulk of nodes from a csv file

        Parameters
        ----------
        file: str
            Path to the .csv file containing the node data. The file is
            assumed to have a header row.

        node_type: str
            Type of nodes to add. Must be one of the node types from
            :obj:`statics.NODE_TYPES`

        node_attrs: Dict[str, str], Optional
            Node arguments to add. Dict keys should be attributes names in the
            database, values represent the column name in the .csv file
        """
        if node_type not in NODE_TYPES:
            raise IncorrectNodeType(f"Unkown node type {node_type}. "
                                    f"Valid node types are '{NODE_TYPES}'")
        statement = f'LOAD CSV WITH HEADERS FROM "file:///{file}" AS row ' \
                    f'MERGE (n:{node_type}'
        if len(node_attrs) != 0:
            attr_statement = [
                f'{attr}: row.{column}' for attr, column in node_attrs.items()
            ]
            statement += f" {{{', '.join(attr_statement)}}})"
        else:
            statement += ")"
        self.session.run(statement)

    # ======= edge insertion functions ======= #
    def add_relation(
        self, relation: str, src: str, tgt: str,
        edge_attrs: Dict[str, any] = None, **attrs
    ):
        """
        Adding a relationship to the database

        Parameters
        ----------
        relation: str
            Type of relation to add. Must be one of the types specified in
            `utils.EDGE_TYPES`

        src: str
            nodeLabel of the relationship sources

        tgt: str
            nodeLabel of the relationship target

        edge_attrs: Dict[str, any]
            Additional attributes as a dictionary. Used mutually exclusive
            with **attrs.

        attrs: optional
            Additional attributes as keyword arguments to be passed for the
            node. All attributes will appear as strings in the database
        """
        if relation not in EDGE_TYPES:
            raise IncorrectEdgeType(f"Unknown edge type: {relation}. "
                                    f"Valid edge types are '{EDGE_TYPES}'")
        src_type, tgt_type = NODE_TYPES_BY_EDGE[relation]
        statement = \
            f"MATCH (enrichment:{str(src_type)}) " \
            f"MATCH (tgt:{str(tgt_type)}) "\
            f"WHERE enrichment.nodeLabel = '{self._validate_node(src)}' " \
            f"AND tgt.nodeLabel = '{self._validate_node(tgt)}' " \
            f"CREATE (enrichment)-[edge:{relation}]->(tgt)"
        if edge_attrs is None:
            self._add_attributes_(statement, 'edge', **attrs)
        else:
            self._add_attributes_(statement, 'edge', **edge_attrs)
        self.session.run(statement)

    def relations_from_csv(self, file: str, relation: str):
        """
        Efficiently adding a bulk of relations from a csv file

        Parameters
        ----------
        file: str
            Path to the .csv file containing the node data. The file is assumed
            to have a header row.

        relation: str
            Type of the relations to add. Must be one of the types specified
            in `utils.EDGE_TYPES`
        """
        if relation not in EDGE_TYPES:
            raise IncorrectEdgeType(f"Unknown edge type: {relation}. "
                                    f"Valid edge types are '{EDGE_TYPES}'")
        src_type, tgt_type = NODE_TYPES_BY_EDGE[relation]
        if relation == EDGE_TYPE_NAMES['substrate'] or \
                relation == EDGE_TYPE_NAMES['product']:
            src_col, tgt_col = "enrichment", "tgt"
        else:
            src_col = EDGE_ATTRIBUTES[relation]['enrichment']
            tgt_col = EDGE_ATTRIBUTES[relation]['tgt']
        statement = f'LOAD CSV WITH HEADERS FROM "file:///{file}" AS row ' \
                    f'MATCH (enrichment:{str(src_type)}) ' \
                    f'MATCH (tgt:{str(tgt_type)}) ' \
                    f'WHERE enrichment.nodeLabel = row.{src_col} AND ' \
                    f'tgt.nodeLabel = row.{tgt_col} ' \
                    f'CREATE (enrichment)-[edge:{relation}]->(tgt)'
        self.session.run(statement)
