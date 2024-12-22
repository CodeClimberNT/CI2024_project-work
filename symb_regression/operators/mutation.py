import random
from typing import Dict, Optional

from symb_regression.config.settings import MutationConfig, MutationType, TreeConfig
from symb_regression.core.tree import Node
from symb_regression.operators.definitions import (
    BINARY_OPS,
    UNARY_OPS,
)


def mutate(
    node: Node,
    mutation_prob: float,
    max_depth: int,
    n_variables: int,
    unary_weights: Dict[str, float],
    binary_weights: Dict[str, float],
    config: MutationConfig = MutationConfig(),
) -> Node:
    if random.random() < mutation_prob:
        mutation_type = random.choices(
            list(config.MUTATION_WEIGHTS.keys()),
            weights=list(config.MUTATION_WEIGHTS.values()),
        )[0]

        if mutation_type == MutationType.SUBTREE:
            return create_random_tree(
                random.randint(
                    config.SUBTREE_DEPTH_RANGE[0], config.SUBTREE_DEPTH_RANGE[1]
                ),
                max_depth,
                n_variables,
                unary_weights,
                binary_weights,
            )

        elif mutation_type == MutationType.OPERATOR:
            if node.op in UNARY_OPS:
                node.op = random.choices(
                    list(unary_weights.keys()),
                    weights=list(unary_weights.values()),
                )[0]
            elif node.op in BINARY_OPS:
                node.op = random.choices(
                    list(binary_weights.keys()),
                    weights=list(binary_weights.values()),
                )[0]

        elif mutation_type == MutationType.OPERATOR:
            if node.value is not None:
                step = (
                    abs(node.value) * config.VALUE_STEP_FACTOR
                    if node.value != 0
                    else config.VALUE_STEP_FACTOR
                )
                node.value += random.gauss(0, step)

        elif mutation_type == MutationType.SIMPLIFY:
            if node.op == "*":
                if (node.left and node.left.value == 0) or (
                    node.right and node.right.value == 0
                ):
                    return Node(value=0)
                if node.left and node.left.value == 1:
                    return node.right.copy() if node.right else node
                if node.right and node.right.value == 1:
                    return node.left.copy() if node.left else node

    # Recursively mutate children with reduced probability
    if node.left:
        node.left = mutate(
            node.left,
            mutation_prob * config.VARIABLE_PROBABILITY,
            max_depth,
            n_variables,
            unary_weights,
            binary_weights,
        )
    if node.right:
        node.right = mutate(
            node.right,
            mutation_prob * config.VARIABLE_PROBABILITY,
            max_depth,
            n_variables,
            unary_weights,
            binary_weights,
        )

    return node


def create_random_tree(
    depth: int,
    max_depth: int,
    n_variables: int,
    unary_weights: Optional[Dict[str, float]] = None,
    binary_weights: Optional[Dict[str, float]] = None,
    config: TreeConfig = TreeConfig(),
) -> Node:
    from symb_regression.operators.definitions import get_var_name

    # Use default weights if none provided
    if unary_weights is None:
        unary_weights = {op: 1.0 / len(UNARY_OPS) for op in UNARY_OPS}
    if binary_weights is None:
        binary_weights = {op: 1.0 / len(BINARY_OPS) for op in BINARY_OPS}

    # Force at least one variable in the expression at root level
    if depth == 0:
        # Binary operator with at least one variable
        op = random.choices(
            list(binary_weights.keys()),
            weights=list(binary_weights.values()),
            k=1,
        )[0]
        node = Node(op=op)

        # Force one child to be a variable
        var_idx: int = random.randint(0, n_variables)
        if random.random() < config.ROOT_VARIABLE_SIDE_PROBABILITY:
            node.left = Node(op=get_var_name(var_idx))
            node.right = create_random_tree(
                depth + 1, max_depth, n_variables, unary_weights, binary_weights
            )
        else:
            node.left = create_random_tree(
                depth + 1, max_depth, n_variables, unary_weights, binary_weights
            )
            node.right = Node(op=get_var_name(var_idx))
        return node

    # At maximum depth, prefer variables over constants
    if depth >= max_depth:
        if random.random() < config.VARIABLE_PROBABILITY:
            var_idx = random.randint(1, n_variables)
            return Node(op=get_var_name(var_idx))
        else:
            return Node(value=random.uniform(-5, 5))

    # For intermediate depths
    if random.random() < config.OPERATOR_PROBABILITY:
        if random.random() < config.UNARY_OPERATOR_PROBABILITY:
            op = random.choices(
                list(unary_weights.keys()),
                weights=list(unary_weights.values()),
                k=1,
            )[0]
            node = Node(op=op)
            node.left = create_random_tree(
                depth + 1, max_depth, n_variables, unary_weights, binary_weights
            )
        else:
            op = random.choices(
                list(binary_weights.keys()),
                weights=list(binary_weights.values()),
                k=1,
            )[0]
            node = Node(op=op)
            node.left = create_random_tree(
                depth + 1, max_depth, n_variables, unary_weights, binary_weights
            )
            node.right = create_random_tree(
                depth + 1, max_depth, n_variables, unary_weights, binary_weights
            )
        return node
    else:
        if random.random() < config.VARIABLE_PROBABILITY:
            var_idx = random.randint(1, n_variables)
            return Node(op=get_var_name(var_idx))
        else:
            return Node(
                value=random.uniform(
                    config.CONSTANT_RANGE[0],
                    config.CONSTANT_RANGE[1],
                )
            )
