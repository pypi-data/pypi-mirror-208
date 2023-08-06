from typing import Union, Tuple, List
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm


def completeness(
    df: pd.DataFrame, column: str,
    return_mask: bool = False
) -> Union[float, Tuple[float, pd.Series]]:
    mask = ~((df[column].isna()) | (df[column] == 'None'))
    comp = np.nansum(mask) / df.shape[0]
    if return_mask:
        return mask, comp
    return comp


def joint_completeness(
    df: pd.DataFrame, column: str,
    mask: pd.Series, return_mask: bool = False
) -> Union[float, Tuple[float, pd.Series]]:
    mask = (~(df[column].isna() | df[column] == '')) | mask
    comp = np.nansum(mask) / df.shape[0]
    if return_mask:
        return mask, comp
    return comp


def evaluate_completeness(
    df: pd.DataFrame, columns: List[str]
) -> pd.DataFrame:
    best_score = 0
    best_idx = None
    best_mask = None
    order = []
    n = len(columns)
    for i in tqdm(range(n)):
        if i == 0:
            for j, column in enumerate(columns):
                tmp_mask, tmp_score = completeness(df, column, True)
                if tmp_score > best_score:
                    best_score = tmp_score
                    best_mask = tmp_mask
                    best_idx = j
            order.append({'Completeness': best_score,
                          'database': columns[best_idx]})
            del columns[best_idx]
            best_score = 0
        else:
            for j, column in enumerate(columns):
                tmp_mask, tmp_score = joint_completeness(
                    df, column, best_mask, True
                )
                if tmp_score > best_score:
                    best_score = tmp_score
                    best_mask = tmp_mask
                    best_idx = j
            sum_comp = sum([order[z]['Completeness'] for z in range(i)])
            order.append(
                {'Completeness': best_score - sum_comp,
                 'database': columns[best_idx]}
            )
            del columns[best_idx]
            best_score = 0
    return pd.DataFrame(order)


def plot_completeness(
    comp: pd.DataFrame = None, df: pd.DataFrame = None,
    ax: plt.axis = None
) -> plt.axis:
    if comp is None:
        if df is None:
            raise ValueError("")
        comp = evaluate_completeness(df, list(df.columns))
    if ax is None:
        _, ax = plt.subplots(figsize=(16, 9))
    sns.barplot(
        x="database", y="Completeness", data=comp, ax=ax, color="tab:blue"
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    return ax


def plot_db_statistics(stats: dict, ax: plt.axis = None, xlabel: str = None):
    if ax is None:
        _, ax = plt.subplots(figsize=(16, 9))
    xticks = np.arange(1, len(stats) + 1)
    ax.bar(xticks, stats.values())
    ax.set_xticks(xticks)
    ax.set_xticklabels(stats.keys())
    if xlabel:
        ax.set_xlabel(xlabel)
    ax.set_ylabel("Count")
    return ax


if __name__ == "__main__":
    import os
    import pathlib
    from pymantra.database.generate_neo4j_db import report_nodes
    from pymantra.database.query import NetworkGenerator
    from pymantra.database import read_env

    read_env(pathlib.Path(__file__).parent.parent.parent.absolute() / ".env")
    AUTH = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))

    # statistics of name mapping
    metabolites = pd.read_csv("reference_tables/metabolites.csv", index_col=0)
    id_cols = [
        'KEGG', 'pubchem', 'CHEBI', 'hmdb_id', 'iupac', 'foodb_id',
        'chemspider_id', 'drugbank_id', 'pdb_id', 'bigg_id', 'vmh_id',
        'uniprot', 'ensembl', 'ncbi', 'reactome_id'
    ]
    fig, axes = plt.subplots(figsize=(21, 9), ncols=2)
    evaluation = evaluate_completeness(metabolites, id_cols.copy())
    plot_ax = plot_completeness(evaluation, ax=axes[0])
    plt.xticks(rotation=90)

    indiv_comp = pd.DataFrame(
        [{'database': db, 'Completeness': completeness(metabolites, db)}
         for db in id_cols]
    )
    sns.barplot(
        x='database', y='Completeness', data=indiv_comp, ax=axes[1],
        color="tab:blue"
    )
    plt.xticks(rotation=90)

    plt.tight_layout()
    plt.savefig("reference_tables/metabolite_evaluation.pdf")
    plt.close(fig)

    # statistics of node/edge numbers
    connection = NetworkGenerator("bolt://127.0.0.1:7687", AUTH)
    node_counts, edge_counts = report_nodes(connection, True)

    fig, axes = plt.subplots(figsize=(21, 9), ncols=2)
    node_ax = plot_db_statistics(node_counts, axes[0], "Node Type")
    edge_ax = plot_db_statistics(edge_counts, axes[1], "Edge Type")

    plt.tight_layout()
    plt.savefig("reference_tables/counts_statistics.pdf")
    plt.close(fig)
