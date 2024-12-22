from typing import Any, List, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.axes import Axes

from symb_regression.core.tree import Node
from symb_regression.operators.definitions import SymbolicConfig


def plot_evolution_metrics(metrics_history: List[Any], ax=None) -> None:
    """Plot metrics related to the evolution process."""
    generations = [m.generation for m in metrics_history]
    max_gen = max(generations)
    best_fitness = [m.best_fitness for m in metrics_history]
    best_gen = generations[np.argmax(best_fitness)]
    # quarter_gens = [int(max_gen * x) for x in [0, 0.25, 0.5, 0.75, 1.0]]

    # fig = plt.figure(figsize=(15, 10))

    # 1. Fitness Evolution (top left)
    # plt = plt.subplot(221)
    if ax is None:
        ax = plt.gca()

    avg_fitness = [m.avg_fitness for m in metrics_history]
    worst_fitness = [m.worst_fitness for m in metrics_history]

    ax.plot(generations, best_fitness, "g-", label="Best", linewidth=2)
    ax.plot(generations, avg_fitness, "b-", label="Average", alpha=0.7)
    ax.plot(generations, worst_fitness, "r-", label="Worst", alpha=0.5)
    ax.axvline(x=best_gen, color="green", linestyle="--", alpha=0.5)

    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness (1 / (1 + MSE))")
    ax.set_title("Fitness Evolution")
    ax.legend()
    ax.grid(True)

    """# 2. Population Diversity (top right)
    ax2 = plt.subplot(222)
    diversity = [m.population_diversity for m in metrics_history]
    ax2.plot(generations, diversity, "b-", linewidth=2)
    for gen in quarter_gens:
        ax2.axvline(x=gen, color="gray", linestyle="--", alpha=0.3)
    ax2.axvline(x=best_gen, color="green", linestyle="--", alpha=0.5)

    ax2.set_xlabel("Generation")
    ax2.set_ylabel("Diversity Ratio")
    ax2.set_title("Population Diversity")
    ax2.grid(True)

    # 3. Tree Complexity (bottom left)
    ax3 = plt.subplot(223)
    avg_size = [m.avg_tree_size for m in metrics_history]
    min_size = [m.min_tree_size for m in metrics_history]
    max_size = [m.max_tree_size for m in metrics_history]

    ax3.plot(generations, avg_size, "b-", label="Average", linewidth=2)
    ax3.fill_between(generations, min_size, max_size, alpha=0.2, color="blue")
    ax3.axvline(x=best_gen, color="green", linestyle="--", alpha=0.5)

    ax3.set_xlabel("Generation")
    ax3.set_ylabel("Tree Size (nodes)")
    ax3.set_title("Expression Complexity")
    ax3.grid(True)

    # 4. Operator Distribution (bottom right)
    ax4 = plt.subplot(224)
    final_ops = metrics_history[-1].operator_distribution
    plot_operator_distribution(ax4, final_ops)

    # Add summary text
    summary_text = (
        f"Best solution at gen {best_gen} ({best_gen/max_gen*100:.1f}%)\n"
        f"Final fitness: {max(best_fitness):.6f}\n"
        f"Final diversity: {diversity[-1]:.2f}"
    )
    fig.text(
        0.02,
        0.02,
        summary_text,
        fontsize=10,
        bbox=dict(facecolor="white", alpha=0.8),
    )"""

    # plt.tight_layout()
    # plt.show()


def plot_operator_distribution(ax: Axes, operator_dist: dict) -> None:
    """Plot operator distribution on given axes."""
    ops = list(operator_dist.keys())
    frequencies = list(operator_dist.values())

    # Sort and filter operators
    sorted_indices = np.argsort(frequencies)[::-1]
    top_n = 6
    if len(ops) > top_n:
        top_ops = [ops[i] for i in sorted_indices[:top_n]]
        top_freqs = [frequencies[i] for i in sorted_indices[:top_n]]
        other_freq = sum(frequencies[i] for i in sorted_indices[top_n:])

        ops = top_ops + ["Others"]
        frequencies = top_freqs + [other_freq]
    else:
        ops = [ops[i] for i in sorted_indices]
        frequencies = [frequencies[i] for i in sorted_indices]

    # Create color scheme
    colors = plt.cm.Set3(np.linspace(0, 1, len(ops)))  # type: ignore
    if "Others" in ops:
        colors[-1] = (0.7, 0.7, 0.7, 1.0)

    # Create bar plot
    bars = ax.barh(range(len(ops)), frequencies, color=colors)
    ax.set_yticks(range(len(ops)))
    ax.set_yticklabels(ops)

    # Add percentage labels
    total = sum(frequencies)
    for bar in bars:
        width = bar.get_width()
        percentage = (width / total) * 100
        if percentage >= 5:
            ax.text(
                width,
                bar.get_y() + bar.get_height() / 2,
                f"{percentage:.1f}%",
                ha="left",
                va="center",
                fontsize=8,
            )

    ax.set_xlabel("Frequency")
    ax.set_title("Most Used Operators")


def plot_prediction_analysis(
    expression: Node,
    x: np.ndarray,
    y: np.ndarray,
    title: str = "Expression Evaluation",
    ax=None,
    config: SymbolicConfig = SymbolicConfig.create(),
) -> Tuple[np.float64, np.float64]:
    """
    Evaluate a symbolic expression against dataset and visualize results.

    Args:
        expression: The symbolic expression to evaluate
        x: Input data
        y: True output data
        title: Title for the plot

    Returns:
        Tuple containing (mse, r2_score)
    """
    # Calculate predictions
    y_pred = expression.evaluate(x, config)

    # Calculate metrics
    mse = np.mean((y - y_pred) ** 2).astype(np.float64)
    r2 = 1 - (np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)).astype(
        np.float64
    )

    # Create figure
    # fig, (plt, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    if ax is None:
        ax = plt.gca()

    # Plot predicted vs actual
    ax.scatter(y, y_pred, alpha=0.5, label="Predictions")

    # Plot perfect prediction line
    min_val = np.min((np.min(y), np.min(y_pred)))
    max_val = np.max((np.max(y), np.max(y_pred)))
    ax.plot(
        [min_val, max_val],
        [min_val, max_val],
        "r--",
        label="Perfect Prediction",
    )

    ax.set_xlabel("True Values")
    ax.set_ylabel("Predicted Values")
    ax.set_title("Predicted vs True Values")
    ax.grid(True)
    ax.legend()

    # Add metrics text
    metrics_text = f"MSE: {mse:.6f}\nR²: {r2:.6f}"
    ax.text(
        4.05,
        1.50,
        metrics_text,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    """# Plot residuals
    residuals = y - y_pred
    ax2.scatter(y_pred, residuals, alpha=0.5)
    ax2.axhline(y=0, color="r", linestyle="--")
    ax2.set_xlabel("Predicted Values")
    ax2.set_ylabel("Residuals")
    ax2.set_title("Residual Plot")
    ax2.grid(True)

    # Add residuals statistics
    resid_stats = (
        f"Mean: {np.mean(residuals):.6f}\n"
        f"Std: {np.std(residuals):.6f}\n"
        f"Max: {np.max(np.abs(residuals)):.6f}"
    )
    ax2.text(
        0.05,
        0.95,
        resid_stats,
        transform=ax2.transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )"""

    # ax.suptitle(title)
    # plt.tight_layout()
    # plt.show()

    return mse, r2


def plot_variable_importance(
    expression: Node,
    x: np.ndarray,
    y: np.ndarray,
    n_samples: int = 1000,
    config: SymbolicConfig = SymbolicConfig.create(),
) -> None:
    """
    Analyze and visualize the importance of each variable.

    Args:
        expression: The symbolic expression to analyze
        x: Input data
        y: True output data
        n_samples: Number of samples for sensitivity analysis
    """
    n_vars = x.shape[1] if x.ndim > 1 else 1
    base_pred = expression.evaluate(x, config)
    sensitivities = []

    # Perform sensitivity analysis
    for i in range(n_vars):
        x_perturbed = x.copy()
        if x.ndim > 1:
            std = np.std(x[:, i])
            x_perturbed[:, i] += np.random.normal(0, std, size=len(x))
        else:
            std = np.std(x)
            x_perturbed += np.random.normal(0, std, size=len(x))

        perturbed_pred = expression.evaluate(x_perturbed, config)
        sensitivity = np.mean(np.abs(perturbed_pred - base_pred))
        sensitivities.append(sensitivity)

    # Plot variable importance
    plt.figure(figsize=(10, 5))
    var_names = [f"x{i}" for i in range(n_vars)]
    plt.bar(var_names, sensitivities)
    plt.title("Variable Importance Analysis")
    plt.xlabel("Variables")
    plt.ylabel("Sensitivity")
    plt.grid(True, alpha=0.3)

    # Add percentage labels
    total = sum(sensitivities)
    for i, v in enumerate(sensitivities):
        plt.text(i, v, f"{(v/total)*100:.1f}%", ha="center", va="bottom")

    plt.tight_layout()
    plt.show()


def visualize_expression_behavior(
    expression: Node,
    x: np.ndarray,
    y: np.ndarray,
    variable_idx: int = 0,
    n_points: int = 100,
    config: SymbolicConfig = SymbolicConfig.create(),
) -> None:
    """
    Visualize how the expression behaves across the range of a specific variable.

    Args:
        expression: The symbolic expression to analyze
        x: Input data
        y: True output data
        variable_idx: Index of the variable to analyze
        n_points: Number of points for visualization
    """
    if x.ndim > 1:
        x_var = x[:, variable_idx]
    else:
        x_var = x

    # Create range of values for the selected variable
    x_range = np.linspace(np.min(x_var), np.max(x_var), n_points)

    # Create input data for prediction
    if x.ndim > 1:
        x_pred = np.tile(np.mean(x, axis=0), (n_points, 1))
        x_pred[:, variable_idx] = x_range
    else:
        x_pred = x_range

    # Calculate predictions
    y_pred = expression.evaluate(x_pred, config)

    # Plot
    plt.figure(figsize=(12, 6))

    # Plot actual data points
    plt.scatter(x_var, y, alpha=0.5, label="Actual Data", color="blue")

    # Plot expression behavior
    plt.plot(x_range, y_pred, "r-", label="Expression", linewidth=2)

    plt.xlabel(f"Variable x{variable_idx}")
    plt.ylabel("Output")
    plt.title(f"Expression Behavior vs Variable x{variable_idx}")
    plt.legend()
    plt.grid(True)

    # Add expression text
    plt.text(
        0.02,
        0.98,
        f"Expression: {expression}",
        transform=plt.gca().transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    plt.tight_layout()
    plt.show()


def plot_expression_tree(root_node):
    import matplotlib.pyplot as plt

    G = nx.DiGraph()
    nodes_list = []

    def collect_nodes(node, parent_id=None):
        current_id = id(node)
        nodes_list.append(node)

        if parent_id is not None:
            G.add_edge(parent_id, current_id)

        if node.left:
            collect_nodes(node.left, current_id)
        if node.right:
            collect_nodes(node.right, current_id)

    collect_nodes(root_node)

    def hierarchical_layout(
        graph, root=None, width=4.0, vert_gap=1.0, vert_loc=0, xcenter=0.5
    ):
        pos = {}  # dictionary to store node positions

        def _hierarchy_pos(
            G, root, width, vert_gap, vert_loc, xcenter, pos, parent=None, parsed=[]
        ):
            if root not in parsed:
                parsed.append(root)
                neighbors = list(G.neighbors(root))
                if not neighbors:  # leaf node
                    pos[root] = (xcenter, vert_loc)
                else:
                    dx = width / len(neighbors)
                    nextx = xcenter - width / 2 - dx / 2
                    for neighbor in neighbors:
                        nextx += dx
                        pos = _hierarchy_pos(
                            G,
                            neighbor,
                            width=dx,
                            vert_gap=vert_gap,
                            vert_loc=vert_loc - vert_gap,
                            xcenter=nextx,
                            pos=pos,
                            parent=root,
                            parsed=parsed,
                        )
                pos[root] = (xcenter, vert_loc)
            return pos

        return _hierarchy_pos(graph, root, width, vert_gap, vert_loc, xcenter, pos)

    root_id = id(root_node)
    pos = hierarchical_layout(G, root=root_id)

    # Draw nodes and edges
    nx.draw(
        G,
        pos,
        with_labels=False,
        node_size=500,
        node_color="#ADD8E6",
        edge_color="#708090",
        alpha=0.9,
    )

    # Add labels
    labels = {}
    for n in nodes_list:
        if n.op is not None:
            labels[id(n)] = n.op
        elif n.value is not None:
            labels[id(n)] = str(n.value)
        else:
            labels[id(n)] = "None"

    nx.draw_networkx_labels(
        G, pos, labels, font_size=10, font_color="#4B0082", font_weight="bold"
    )
    plt.title("Expression Tree", fontsize=16, fontweight="bold")
    plt.show()
