from parse_responses import *
import json
import matplotlib.pyplot as plt
import numpy as np

QUERIES = [
    'adventure',
    'children',
    'crime',
    'family',
    'friends',
    'history',
    'love',
    'prison',
    'school',
    'student',
    'war',
]

plt.style.use('seaborn-whitegrid')
# plt.rcParams['font.family'] = 'serif'
# plt.rcParams['font.serif'] = 'Ubuntu'
# plt.rcParams['font.monospace'] = 'Ubuntu Mono'
# plt.rcParams['font.size'] = 10
# plt.rcParams['axes.labelsize'] = 10
# plt.rcParams['axes.labelweight'] = 'bold'
# plt.rcParams['axes.titlesize'] = 10
# plt.rcParams['xtick.labelsize'] = 8
# plt.rcParams['ytick.labelsize'] = 8
# plt.rcParams['legend.fontsize'] = 10
# plt.rcParams['figure.titlesize'] = 12


def load_relevats() -> dict:
    """
    Loads the relevant documents for each query.
    """
    solr_relevants = parse_responses()
    rf_relevants = parse_responses(dir=RF_DIR)

    keys = set(list(solr_relevants.keys()) + list(rf_relevants.keys()))
    relevants = dict()
    for k in keys:
        relevants[k] = list(
            set(solr_relevants.get(k, []) + rf_relevants.get(k, [])))
        relevants[k].sort()

    return relevants


def solr_query(query: str) -> list:
    """
    Loads solr query results for a given query.
    """
    with open(f'./query/solr/{query}.json', 'r', encoding='utf8') as f:
        data = json.load(f)
        docs = data['response']['docs']
        return list(map(lambda d: d['docID'], docs))


def rf_query(query: str) -> list:
    """
    Loads relevance feedback query results for a given query.
    """
    with open(f'./query/rf/{query}.json', 'r', encoding='utf8') as f:
        docs = json.load(f)
        return list(map(lambda d: d['docID'], docs))


def precision_at_k(results: list[int], relevants: list[int] | set, k: int) -> float:
    """
    Computes the precision at k for a given result set and a set of relevant documents.
    """
    top_k = results[:k]
    return len(set(top_k) & set(relevants)) / k


def recall_at_k(results: list[int], relevants: list[int] | set, k: int) -> float:
    """
    Computes the recall at k for a given result set and a set of relevant documents.
    """
    top_k = results[:k]
    return len(set(top_k) & set(relevants)) / len(relevants)


def plot_precision_recall(
    precision_at: list[float],
    recall_at: list[float],
    label : str = None,
    title: str = '',
    color: str = 'b-',
    figure: plt.Figure = None,
    show: bool = True,
    eps: float = 0.05,
) -> plt.Figure:
    """
    Plots the precision-recall curve, over current figure if given, or creates a new one.
    Args:
        `precision_at`: list of precision values at k
        `recall_at`: list of recall values at k
        `title`: title of the plot
        `color`: color of the plot
        `figure`: figure to plot on
        `show`: whether to show the plot or not
        `eps`: epsilon value for the plot limits borders
    Returns:
        The figure object
    """
    if figure is None:
        figure = plt.figure()
    plt.plot(
        recall_at,
        precision_at,
        color,
        label = label,
        marker='s',
        markersize=3,
        linestyle='-.',
        linewidth=1,
    )
    plt.xlim(-eps, 1 + eps)
    plt.ylim(-eps, 1 + eps)
    if label is None:
        plt.legend(['Solr (baseline)', 'Solr + Relevance Feedback'])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(title)
    if show:
        plt.show()
    return figure

def interpolate_precision_recall(
    precision_at: list[float],
    recall_at: list[float],
    k: int
) -> tuple[list[float], list[float]]:
    """
    Interpolates the precision-recall curve at k.
    """
    interpolated_precision_at = [max(precision_at)]
    interpolated_recall_at = [0] + recall_at[:]
    for i in range(k):
        interpolated_precision_at.append(max(precision_at[i:]))
    return interpolated_precision_at, interpolated_recall_at


if __name__ == "__main__":
    RELEVANTS = load_relevats()
    K = 20
    avg_interpolated_solr_precision_at = np.zeros(K+1)
    avg_interpolated_rf_precision_at = np.zeros(K+1)
    recall_levels = [i/K for i in range(K+1)]

    for q in QUERIES:
        solr_results = solr_query(q)
        rf_results = rf_query(q)

        solr_precision_at = []
        solr_recall_at = []
        rf_precision_at = []
        rf_recall_at = []

        for k in range(1, K + 1):
            solr_precision_at.append(precision_at_k(solr_results, RELEVANTS[q], k))
            solr_recall_at.append(recall_at_k(solr_results, RELEVANTS[q], k))
            rf_precision_at.append(precision_at_k(rf_results, RELEVANTS[q], k))
            rf_recall_at.append(recall_at_k(rf_results, RELEVANTS[q], k))

        # Decomment following lines for plotting single query precision-recall curves

        # fig = plot_precision_recall(
        #     solr_precision_at,
        #     solr_recall_at,
        #     show=False,
        #     color='r-'
        # )
        # plot_precision_recall(
        #     rf_precision_at,
        #     rf_recall_at,
        #     figure=fig,
        #     title=f'Precision-Recall for q="{q}"'
        # )

        # Interpolate precision-recall curves

        interpolated_solr_precision_at, interpolated_solr_recall_at = interpolate_precision_recall(
            solr_precision_at,
            solr_recall_at, 
            K
        )
        interpolated_rf_precision_at, interpolated_rf_recall_at = interpolate_precision_recall(
            rf_precision_at,
            rf_recall_at,
            K
        )
        
        # Decomment following lines for plotting single query interpolated precision-recall curves

        # fig = plot_precision_recall(
        #     interpolated_solr_precision_at,
        #     interpolated_solr_recall_at,
        #     show=False,
        #     color='r-'
        # )

        # plot_precision_recall(
        #     interpolated_rf_precision_at,
        #     interpolated_rf_recall_at,
        #     figure=fig,
        #     title=f'Interpolated Precision-Recall for q="{q}"'
        # )

        # Update avg interpolated precision at for each recall levels
        for i, level in zip(range(len(avg_interpolated_solr_precision_at)), recall_levels):
            avg_interpolated_solr_precision_at[i] += np.interp(level, interpolated_solr_recall_at, interpolated_solr_precision_at)
            avg_interpolated_rf_precision_at[i] += np.interp(level, interpolated_rf_recall_at, interpolated_rf_precision_at)

    # Compute avg for each avg_interpolated element
    avg_interpolated_solr_precision_at /= len(QUERIES)
    avg_interpolated_rf_precision_at /= len(QUERIES)

    # Plot avg interpolated precision at for K queries
    fig = plot_precision_recall(
        avg_interpolated_solr_precision_at,
        recall_levels,
        label = "Solr (baseline)",
        show = False,
        color='r-',
        eps = 0
    )

    plot_precision_recall(
        avg_interpolated_rf_precision_at,
        recall_levels,
        label = "Solr + Relevance Feedback",
        figure = fig,
        title = f"Avg interpolated precision for {len(QUERIES)} queries",
        eps = 0,
        show = False
    )

    # Add y = x function to plot
    plt.plot(
        [0,1],
        [0,1],
        "k",
        marker='s',
        markersize=3,
        linestyle='--',
        linewidth=1,
        label = "y = x"
    )
    plt.legend()
    plt.show()
    
    # Compute MAP
    
    # print("MAP of solr system: ", np.mean(avg_interpolated_solr_precision_at))
    # print("MAP of solr with rf system: ", np.mean(avg_interpolated_rf_precision_at))

    # Plot MAP Comparison
    plt.bar(
        ["Solr (baseline)", "Solr + Relevance Feedback"],
        [np.mean(avg_interpolated_solr_precision_at), np.mean(avg_interpolated_rf_precision_at)],
        width = 0.4
    )
    plt.xlabel("Systems")
    plt.ylabel("MAP")
    plt.title("MAP Comparison")
    plt.show()