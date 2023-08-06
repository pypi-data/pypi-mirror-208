import os
import pandas as pd
from collections import namedtuple
from typing import Tuple, Dict, Set, Union, NamedTuple
from itertools import repeat
from multiprocessing import Pool

from pymantra.database.generator import Neo4jGenerator
from pymantra.database.base import Neo4jBaseConnector
from pymantra.database.verifier import Verifier
from pymantra.statics import (
    Edge,
    NODE_TYPES, EDGE_TYPES,
    NODE_ATTRIBUTES, EDGE_ATTRIBUTES,
    NODE_FILES, EDGE_FILES,
    EDGE_TYPE_NAMES, NODE_TYPES_BY_EDGE
)
from tqdm import tqdm


ResourceData = namedtuple(
    "ResourceData", "nodes edges node_attrs edge_attrs"
)


def edge_to_str(edge: Edge) -> str:
    return f"{edge.source}=>{edge.target}"


def process_reaction(
    reac_data: Dict[str, str],
    substrate_edges: Dict[Edge, Dict[str, str]],
    product_edges: Dict[Edge, Dict[str, str]]
):
    """
    Extracting relations from a single reaction

    Parameters
    ----------
    reac_data: Dict[str, str]
        Reaction data with three required keys:
        * substrates_unified: single string containing substrates separated by
          ','
        * products_unified: single string containing substrates separated by
          ','
        * abbreviation: name of the reaction

    substrate_edges: Dict[Edge, Dict[str, str]]
        Dictionary in which extracted substrate edges are stored

    product_edges: Dict[Edge, Dict[str, str]]
        Dictionary in which extracted product edges are stored
    """
    substrates = reac_data['substrates_unified']
    products = reac_data['products_unified']
    reaction = reac_data['abbreviation']
    # NOTE: substrates and products are strings, except for the case of
    #       empty cells since these are np.nan (float)
    if isinstance(substrates, str):
        for substrate in substrates.split(','):
            substrate = substrate.strip()
            src_type = NODE_TYPES_BY_EDGE[EDGE_TYPE_NAMES['substrate']][0]
            tgt_type = NODE_TYPES_BY_EDGE[EDGE_TYPE_NAMES['substrate']][1]
            substrate_edges[Edge(substrate, reaction)] = {
                'edge_type': EDGE_TYPE_NAMES['substrate'],
                'src_type': src_type,
                'tgt_type': tgt_type
            }
    if isinstance(products, str):
        for product in products.split(','):
            product = product.strip()
            product_edges[Edge(reaction, product)] = {
                'edge_type': EDGE_TYPE_NAMES['product'],
                'src_type': NODE_TYPES_BY_EDGE[EDGE_TYPE_NAMES['product']][0],
                'tgt_type': NODE_TYPES_BY_EDGE[EDGE_TYPE_NAMES['product']][1]
            }


def extract_relations(
    input_folder: str, output_folder: str, verbose: bool = True,
    force_overwrite: bool = True
):
    """
    Extraction relationships between reactions and metabolites from the
    reactions table

    Parameters
    ----------
    input_folder: str
        Path to the input folder, which needs to contain a .csv file named
        'vmh_reactome_reactions.csv'

    output_folder: str
        Path to the folder in which the extracted relations will be stored as
        'reaction_metabolite_relations.csv'

    verbose: bool, default True
        Whether to do extensive printing

    force_overwrite: bool, default True
        If False :py:meth:`~extract_relations` checks whether the extraction
        output file is already present in the given output folder. Otherwise,
        an existing file will be overwritten.

    """
    sout_file = os.path.join(output_folder, 'substrate_relations.csv')
    pout_file = os.path.join(output_folder, 'product_relations.csv')
    if not force_overwrite:
        if os.path.isfile(sout_file):
            print(f"{sout_file} already exists, skipping relation "
                  "extraction...")
            return
        elif os.path.isfile(pout_file):
            print(f"{pout_file} already exists, skipping relation "
                  "extraction...")
            return
    in_file = os.path.join(input_folder, "reactions.csv")
    if not os.path.isfile(in_file):
        raise FileNotFoundError(f"{in_file} not found")
    reactions = pd.read_csv(in_file, dtype=str).to_dict(orient="records")
    # edges:
    # * substrates
    # * products
    substrates: Dict[Edge, Dict[str, str]] = {}
    products: Dict[Edge, Dict[str, str]] = {}
    for reaction in tqdm(reactions, desc="Scanning reactions"):
        process_reaction(reaction, substrates, products)
    if verbose:
        print(f"{len(substrates) + len(products)} relations identified")
    # * reaction_organism => already formatted in "*reaction_organisms.csv"
    # * reaction_gene => already formatted in "*reaction_catalyst.csv"
    # * gene_organism => already formatted in "*catalyst_organism.csv" and
    #   "*human_catalysts.csv"
    attrs = ['edge_type']
    for out_file, edge_data in zip(
        [sout_file, pout_file], [substrates, products]
    ):
        print(f"Writing extracted substrates to {out_file}\n")
        with open(out_file, 'w') as file:
            file.write("enrichment,tgt")
            for attr in attrs:
                file.write(f",{attr}")
            file.write("\n")
            for edge, data in edge_data.items():
                file.write(f"{edge.source},{edge.target}")
                for attr in attrs:
                    file.write(f",{data[attr]}")
                file.write("\n")


def read_node_data(
    filepath: str, node_type: str,
    nodes: Dict[str, Set[str]], node_attrs: Dict[str, Dict[str, str]],
    sep: str
):
    """
    Reading node data for a specific node type from an in-format table.
    The table needs to contain all header names given in
    utils.NODE_ATTRIBUTES[node_type].values()

    Parameters
    ----------
    filepath: str
        Path to the file containing the node data

    node_type: str
        Node type, needs to be one of the names in utils.NODE_TYPES

    nodes: Dict[str, Set[str]]
        Dictionary storing nodes by node type. The function will not overwrite
        the node sets but add to them.

    node_attrs: Dict[str, Dict[str, str]]
        Dictionary storing nodes by node type. The function will overwrite
        attributes if a node is already present as a dictionary key. Existing
        nodes will not be removed.

    sep: str
        Separator of the .csv. Typically, ',', but given here to allow for
        alternatives.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Node file {filepath} not found")
    node_data = pd.read_csv(filepath, sep=sep).to_dict(orient="records")
    for data in tqdm(node_data, desc=f"{node_type} extraction"):
        # NOTE: this is set by the file structure convention
        node_name = data[NODE_ATTRIBUTES[node_type]['nodeLabel']]
        nodes[node_type].add(node_name)
        node_attrs[node_name] = {attr_name: data[attr] for attr_name, attr in
                                 NODE_ATTRIBUTES[node_type].items()}


def read_edge_data(
    filepath: str, edge_type: str,
    edges: Dict[str, Set[Edge]], edge_attrs: Dict[Edge, Dict[str, str]],
    sep: str
):
    """
    Reading node data for a specific node type from an in-format table.
    The table needs to contain all header names given in
    utils.EDGE_ATTRIBUTES[edge_type].values()

    Parameters
    ----------
    filepath: str
        Path to the file containing the edge data

    edge_type: str
        Edge type, needs to be one of the names in utils.EDGE_TYPES

    edges: Dict[str, Set[Edge]]
        Dictionary storing edges by edge type. The function will not overwrite
        the edge sets but add to them.

    edge_attrs: Dict[Edge, Dict[str, str]]
        Dictionary storing edges by edge type. The function will overwrite
        attributes if a node is already present as a dictionary key. Existing
        edges will not be removed.

    sep: str
        Separator of the .csv. Typically, ',', but given here to allow for
        alternatives.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Edge file {filepath} not found")
    # NOTE: edge tables have no index column!
    edge_data = pd.read_csv(filepath, sep=sep).to_dict(orient="records")
    for data in tqdm(edge_data, desc=f"{edge_type} extraction"):
        edge = Edge(data[EDGE_ATTRIBUTES[edge_type]['enrichment']],
                    data[EDGE_ATTRIBUTES[edge_type]['tgt']])
        edges[edge_type].add(edge)
        edge_attrs[edge] = {
            attr_name: data[attr] for attr_name, attr
            in EDGE_ATTRIBUTES[edge_type].items()
            if attr_name != 'enrichment' and attr_name != 'tgt'
        }


def read_reaction_metabolite_relations(
    filepath: str, edges: Dict[str, Set[Edge]],
    edge_type: str, edge_attrs: Dict[Edge, Dict[str, str]],
    sep: str
):
    """
    Reading node data for a specific node type from an in-format table.
    The table needs to contain all header names given for substrates and
    products, in :obj:`utils.EDGE_ATTRIBUTES[].values()`

    Parameters
    ----------
    filepath: str
        Path to the file containing the reaction - metabolite relation data

    edge_type: str

    edges: Dict[str, Set[Edge]]
        Dictionary storing edges by edge type. The function will not overwrite
        the edge sets but add to them.

    edge_attrs: Dict[Edge, Dict[str, str]]
        Dictionary storing edges by edge type. The function will overwrite
        attributes if a node is already present as a dictionary key. Existing
        edges will not be removed.

    sep: str
        Separator of the .csv. Typically, ',', but given here to allow for
        alternatives.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Edge file {filepath} not found")
    if edge_type not in \
            {EDGE_TYPE_NAMES['substrate'], EDGE_TYPE_NAMES['product']}:
        raise ValueError(
            f"'edge_type' must be {EDGE_TYPE_NAMES['substrate']} or "
            f"{EDGE_TYPE_NAMES['PRODUCT']}"
        )
    # NOTE: edge tables have no index column!
    edge_data = pd.read_csv(filepath, sep=sep).to_dict(orient="records")
    for data in tqdm(edge_data, desc="reaction_metabolite extraction"):
        edge = Edge(data['enrichment'], data['tgt'])
        edges[data['edge_type']].add(edge)
        edge_attrs[edge] = {
            attr_name: edge_data[attr] for attr_name, attr
            in EDGE_ATTRIBUTES[data['edge_type']].items()
            if attr_name != 'enrichment' and attr_name != 'tgt'
        }


def load_data(
    resource_folder: str, file_type: str = "csv", sep: str = ",",
    extract_relations_from_nodes: bool = False, raw_folder: str = None,
    verbose: bool = True, force_overwrite_extraction: bool = True
) -> NamedTuple:
    """
    Parameters
    ----------
    resource_folder: str
        Path to the directory containing data tables

    file_type: str, Optional, default 'csv'
        File type in which data tables are stored. Needs to correspond with
        the file endings of all files to be scanned.

    sep: str, Optional, default ","
        String separating entries in a row. Should be changed accordingly
        when different input file types than the default (csv) are used

    extract_relations_from_nodes: bool, Optional, default False
        Whether edge information needs to be extracted from node data tables

    raw_folder: str, Optional
        Folder containing 'unformatted' data. Needs to be specified when
        'extract_relations_from_nodes' is True

    verbose: bool, Optional, default True
        Whether function should be verbose

    force_overwrite_extraction: bool, default True
        If False :py:meth:`~extract_relations` checks whether the extraction
        output file is already present in the given output folder. Otherwise,
        an existing file will be overwritten.

    Returns
    -------
    4-tuple (ResourceData, NamedTuple)
    1. [nodes] dict: node type (str) -> nodes (Set[str])
    2. [edges] dict: edge type (str) -> edges (Set[Tuple[str, str]])
    3. [node_attrs] dict: node name (str) -> node attributes (dict: attribute
       name (str) -> value (str))
    4. [edge_attrs] dict: edge (Tuple[str, str]) -> edge attributes
       (dict: attribute name (str) -> value (str))
    """
    if extract_relations_from_nodes:
        extract_relations(
            raw_folder, resource_folder, verbose=verbose,
            force_overwrite=force_overwrite_extraction
        )
    nodes = {node_type: set() for node_type in NODE_TYPES}
    node_attrs = {node_type: {} for node_type in NODE_TYPES}
    edges = {edge_type: set() for edge_type in EDGE_TYPES}
    edge_attrs = {edge_type: {} for edge_type in EDGE_TYPES}

    for name, file in tqdm(NODE_FILES.items(), desc="Node type extraction"):
        filepath = os.path.join(resource_folder, f"{file}.{file_type}")
        read_node_data(filepath, name, nodes, node_attrs, sep)
    for name, file in tqdm(EDGE_FILES.items(), desc="Edge type extraction"):
        # TODO: parallelize the read_* functions
        filepath = os.path.join(resource_folder, f"{file}.{file_type}")
        if name in {EDGE_TYPE_NAMES['substrate'], EDGE_TYPE_NAMES['product']}:
            # NOTE: this is NOT substrates only, but all metabolite<->reaction
            #       relationships.
            # This requires the order of EDGE_TYPE_LIST to stay the same!
            read_reaction_metabolite_relations(filepath, edges, name,
                                               edge_attrs, sep)
        else:
            read_edge_data(filepath, name, edges, edge_attrs, sep)

    return ResourceData(nodes, edges, node_attrs, edge_attrs)


def report_nodes(connector: Neo4jBaseConnector, return_: bool = False):
    """
    Reporting number of nodes and edges in the database

    Parameters
    ----------
    connector: Neo4jGenerator
        :obj:`Neo4jBaseConnector` object with an active database connection

    return_: bool, False
        If true data is returned, else just printed
    """
    node_counts = {
        label: connector.session.run(
            f"MATCH (n: {label}) RETURN count(n) as count"
        ).value()[0]
        for label in NODE_TYPES
    }
    edge_counts = {
        label: connector.session.run(
            f"MATCH ()-[r:{label}]->() RETURN count(r) as count"
        ).value()[0]
        for label in EDGE_TYPES
    }
    print("Node Counts:")
    for node_type, count in node_counts.items():
        print(f"* {node_type}: {count}")
    print("\n=======\n")
    print("Edge Counts:")
    for edge_type, count in edge_counts.items():
        print(f"* {edge_type}: {count}")
    if return_:
        return node_counts, edge_counts


def _parallel_node_dump(connection, node, node_type, node_attrs):
    with Neo4jGenerator(*connection) as generator:
        generator.add_node(node, node_type, node_attrs)


def _parallel_edge_dump(connection, edge, edge_type, edge_attrs):
    with Neo4jGenerator(*connection) as generator:
        generator.add_relation(edge_type, edge.source, edge.target,
                               edgeLabel=edge_to_str(edge), **edge_attrs)


def data_to_db(
    uri: str, auth: Union[Tuple[str, str], None], data: ResourceData,
    verbose: bool = True, reset_at_start: bool = False, verify: bool = True,
    n_threads: int = 1
):
    """
    Feeding data previously loaded into a ResourceData object into a
    neo4j database

    Parameters
    ----------
    uri: str
        database uri

    auth: Tuple[str, str]
        Optional database credentials int the form of (user, password).
        If database is not secured pass None.

    data: ResourceData (NamedTuple)
        Data to dump into the database

    verbose: bool, Optional, default True
        Whether function should be verbose

    reset_at_start: bool, Optional, default False
        If True the database will be emptied before data is added

    verify: bool, Optional, default True
        Whether to verify the correctness of the database using
        the requirements defined in the `Verifier` class

    n_threads: int, default 1
        Number of threads to use when dumping data
    """
    with Neo4jGenerator(uri, auth) as generator:
        if reset_at_start:
            if verbose:
                print("\n=== Wiping database ===\n")
            generator.reset()
    if n_threads == 1:
        with Neo4jGenerator(uri, auth) as generator:
            if verbose:
                print("\n=== Dumping node data ===\n")
            for node_type, node_set in tqdm(data.nodes.items(),
                                            desc="Node dumping"):
                for node in tqdm(node_set, desc=f"{node_type} nodes"):
                    generator.add_node(
                        node, node_type, **data.node_attrs[node]
                    )
            if verbose:
                print("\n=== Dumping edge data ===\n")
            for edge_type, edge_set in tqdm(data.edges.items(),
                                            desc="Edge dumping"):
                if n_threads == 1:
                    for edge in tqdm(edge_set, desc=f"{edge_type} edges"):
                        generator.add_relation(
                            edge_type, edge.source, edge.target,
                            edgeLabel=edge_to_str(edge),
                            **data.edge_attrs[edge]
                        )
    else:
        if verbose:
            print("\n=== Dumping node data ===\n")
        for node_type, node_set in data.nodes.items():
            node_list = list(node_set)
            attrs = [data.node_attrs[node] for node in node_list]
            pool = Pool(n_threads)
            pool.starmap(
                _parallel_node_dump,
                zip(repeat((uri, auth)), node_list, repeat(node_type), attrs)
            )
        if verbose:
            print("\n=== Dumping edge data ===\n")
        for edge_type, edge_set in data.edges.items():
            edge_list = list(edge_set)
            attrs = [data.edge_attrs[edge] for edge in edge_list]
            pool = Pool(n_threads)
            pool.starmap(
                _parallel_edge_dump,
                zip(repeat((uri, auth)), edge_list, repeat(edge_type), attrs)
            )
    if verbose:
        print("\n# ======= Final database Statistics ======= #\n")
        with Neo4jGenerator(uri, auth) as generator:
            report_nodes(generator)
    if verify:
        print("\n============ Verifying database Correctness ============")
        with Verifier(uri, auth) as verifier:
            _ = verifier.verify_correctness()


def data_from_files(
    uri: str, auth: Union[Tuple[str, str], None],
    folder: str, node_files: Dict[str, str],
    edge_files: Dict[str, str], reset_at_start: bool = False,
    verbose: bool = True, verify: bool = True
):
    """
        Feeding data from .csv files into a neo4j database

        Parameters
        ----------
        uri: str
            database uri

        auth: Tuple[str, str]
            Optional database credentials int the form of (user, password).
            If database is not secured pass None.

        folder: str
            Folder path in which source files are located

        node_files: Dict[str, str]
            Dictionary specifying the file name (value) for each node type
            (key)

        edge_files: Dict[str, str]
            Dictionary specifying the file name (value) for each edge type
            (key)

        verbose: bool, Optional, default True
            Whether function should be verbose

        reset_at_start: bool, Optional, default False
            If True the database will be emptied before data is added

        verify: bool, Optional, default True
            Whether to verify the correctness of the database using
            the requirements defined in the `Verifier` class
        """
    with Neo4jGenerator(uri, auth) as generator:
        if reset_at_start:
            if verbose:
                print("\n=== Wiping database ===\n")
            generator.reset()
        if verbose:
            print("\n=== Adding nodes ===\n")

        progress = tqdm(node_files.items(), desc="Nodes")
        for node_type, node_file in progress:
            progress.set_description(f"Nodes - {node_type}")
            generator.nodes_from_csv(
                f"{node_file}.csv", node_type,
                NODE_ATTRIBUTES.get(node_type, {})
            )
        progress.set_description("Nodes")

        progress = tqdm(edge_files.items(), desc="Edges")
        for edge_type, edge_file in progress:
            progress.set_description(f"Edges - {edge_type}")
            generator.relations_from_csv(
                f"{os.path.join(edge_file)}.csv",
                edge_type
            )
        progress.set_description("Edges")

    if verbose:
        print("\n# ======= Final database Statistics ======= #\n")
        with Neo4jGenerator(uri, auth) as generator:
            report_nodes(generator)
    if verify:
        print("\n============ Verifying database Correctness ============")
        with Verifier(uri, auth) as verifier:
            _ = verifier.verify_correctness()


if __name__ == "__main__":
    import argparse
    import pickle

    parser = argparse.ArgumentParser()
    # reference location
    parser.add_argument(
        "-r", "--reference", type=str, metavar="reference folder",
        default=None,
        help="Location of the folder holding the data to load into the "
             "database. Must be specified unless --load-pickle is given"
    )
    # port (currently only local supported)
    parser.add_argument(
        "-p", "--port", type=str, metavar="port", default=None,
        help="Port of the database bolt (bolt://127.0.0.1:<port>). "
             "Currently only localhost is supported"
    )
    # username
    parser.add_argument(
        "-u", "--user", type=str, metavar="user", default=None,
        help="Username to log into the database"
    )
    # password
    parser.add_argument(
        "-k", "--password", type=str, metavar="password", default=None,
        help="Password for the user set with -u/--u to log into the database"
    )
    # raw_folder => if passed: extract_relations_from_nodes=True
    parser.add_argument(
        "-f", "--raw-folder", type=str, metavar="raw data folder",
        default=None,
        help="Folder containing raw (i.e. relation not yet extracted) data. "
             "If specified relation data for reactions "
             "with metabolites will be extracted from reactions.csv"
    )
    # saving to pickle
    parser.add_argument(
        '-s', '--save-pickle', type=str, default=None,
        help="File location for a pickle file, if resource data should be "
             "saved directly."
    )
    # loading from pickle
    parser.add_argument(
        '-l', '--load-pickle', type=str, default=None,
        help="File location for a pickle file, if resource data should be "
             "loaded directly."
    )
    # NOTE: the nomenclature for the following parameters is a bit
    #       misleading inside the code since args.no_wipe = True means wiping
    #       WILL happen, whereas args.no_wipe = False means NO wiping. This is
    #       due to argparse's store_false action. For usage, however, passing
    #       --no-wipe will lead to the database not being wiped.
    # wiping database (aka reset_at_start)
    parser.add_argument(
        '--no-wipe', action="store_false",
        help="Not wiping the database before adding the data. "
             "Should only be set if data is to be added without removing "
             "previously existing data."
    )
    # database verification
    parser.add_argument(
        '-v', '--no-verification', action="store_false",
        help="Do not run database verification after populating it. This "
             "should only be set if you either know your database is correct "
             "or if you want to experiment with features/settings, as the "
             "functions of `NetworkGenerator` might not work as expected."
    )
    # overwriting metabolite-reaction relations extraction
    parser.add_argument(
        '-o', '--no-overwrite-extraction', action="store_false",
        help="Do not overwrite the extracted metabolite-reaction file."
    )
    # number of threads to use
    parser.add_argument(
        '-t', '--threads', type=int, default=1,
        help="Setting the number of threads to use. Default is 1 thread."
    )
    # first load into python/process then populate
    parser.add_argument(
        '--use-loaded', type=bool, default=False,
        help="Flag to indicate that data should be dumped from python object "
             "instead of directly from files"
    )

    args = parser.parse_args()

    print("# ============ Populating database ============ #\n")
    if args.use_loaded or args.raw_folder:
        if args.load_pickle:
            print("Loading pickled data...")
            resources = pickle.load(open(args.load_pickle, "rb"))
        else:
            if args.raw_folder:
                print("Extracting from raw data...")
                resources = load_data(
                    args.reference, extract_relations_from_nodes=True,
                    force_overwrite_extraction=args.no_overwrite_extraction,
                    raw_folder=args.raw_folder
                )
            else:
                print("Loading from formatted data...")
                resources = load_data(args.reference)
        if not args.use_loaded:
            if not args.reference:
                raise ValueError("")
            print(f"Saving .csv data to {args.reference}")
            # TODO
        if args.save_pickle:
            print(f"Saving pickled data to {args.save_pickle}")
            pickle.dump(resources, open(args.save_pickle, "wb"))

        print("\n=== Resource data loaded successfully ===")

    uri = f"bolt://127.0.0.1:{args.port}"
    if args.user or args.password:
        auth = (args.user, args.password)
        msg = f"\n=== Connecting to database at {uri} WITH credentials ==="
    else:
        auth = None
        msg = f"\n=== Connecting to database at {uri} WITHOUT credentials ==="
    if args.use_loaded:
        print(msg)
        data_to_db(
            uri, auth,
            resources, reset_at_start=args.no_wipe,
            n_threads=args.threads,
            verify=args.no_verification
        )
    else:
        data_from_files(
            uri, auth, args.reference,
            NODE_FILES, EDGE_FILES,
            reset_at_start=args.no_wipe,
            verify=args.no_verification
        )
