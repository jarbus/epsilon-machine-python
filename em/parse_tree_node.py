from collections import defaultdict, Counter
from typing import Dict, Sequence, List
from functools import partial
import plantuml
import sys


class ParseTreeNode:
    """Node of a parse tree.

    Arguments:
        depth: Level of depth in a tree. For roots, depth=0.
        target_depth: Denoted as D in Crutchfield's lectures.
        The maximum depth of the parse tree.

    Example usage:
        >>> root = ParseTreeNode(target_depth=3)
        >>> root[1][2][3].value += 1
        >>> root[1][2][3].value
        1
        >>> root[1][2][2].value += 1
        >>> root.update_probabilities()
        >>> root[1][2].prob
        1.0
        >>> root[1][2][3].prob
        0.5
        """

    def __init__(self, target_depth: int, depth: int = 0):
        self.prob = None
        self.leaf_count = None
        self.depth = depth
        self.target_depth = target_depth
        self.is_leaf = depth == target_depth
        self.state = None
        self.value = 0
        self.id = "[*]"
        self.state = None
        self.morph = "unassigned"
        if self.is_leaf:
            self.branches = None
        else:
            self.branches = defaultdict(
                partial(ParseTreeNode, depth=depth + 1, target_depth=target_depth)
            )

    def count(self) -> int:
        if self.is_leaf:
            self.leaf_count = self.value
        else:
            for branch in self.branches:
                self.leaf_count = sum((l.count() for l in self.branches.values()))
        return self.leaf_count

    def update_probabilities(self, count=True) -> None:
        """Updates ParseTreeNode.prob with the local probability of transitioning to it from a parent.
        Args:
            count: Calls ParseTreeNode.count() to update the count ofleaf nodes accessible from each node.
        """
        # leaves get updated from parents
        if self.is_leaf:
            return
        # update counts for all child nodes
        if count:
            self.count()
        for key, branch in self.branches.items():
            # No need to call count for child nodes, as they are already updated with calling
            # node's count() call
            branch.update_probabilities(count=False)
            branch.prob = round(branch.leaf_count / self.leaf_count, 2)

    def generate_state_diagram(self, file="default-state-diagram.txt"):
        """Outputs a png file relaying the state diagram, starting from
        the node the function was called from"""
        self.update_probabilities()
        with open(file, "w") as f:
            f.write("@startuml\n")
            f.write("hide empty description\n")
            print(self, file=f)
            f.write("@enduml")

        puml = plantuml.PlantUML("http://www.plantuml.com/plantuml/img/")
        puml.processes_file(file)

    def __str__(self):
        if self.is_leaf:
            return (
                f"{self.id} : State {self.state}\n{self.id} : Count {self.leaf_count}\n"
            )

        branch_strings = []
        child_strings = []
        for key, branch in self.branches.items():
            branch_strings.append(f"{self.id} --> {branch.id} : {branch.prob}")
            child_strings.append(str(branch))
        if self.id != "[*]":
            branch_strings.append(
                f"{self.id} : State {self.state}\n{self.id} : Count {self.leaf_count}\n{self.id} : Morph {self.morph}\n"
            )
        return "" + "\n".join(branch_strings) + "\n" + "".join(child_strings) + "\n"

    def __setitem__(self, key, item):
        if self.is_leaf:
            self.value = item
        else:
            self.branches[key].id = (
                self.id + "_" + str(key) if self.id != "[*]" else str(key)
            )
            self.branches[key].state = key
            self.branches[key] = item

    def __getitem__(self, key):
        if self.is_leaf:
            return self
        else:
            self.branches[key].id = (
                self.id + "_" + str(key) if self.id != "[*]" else str(key)
            )
            self.branches[key].state = key
            return self.branches[key]

    def __eq__(self, other):
        if other.state != self.state or other.prob != self.prob:
            return false
        for key, item in self.branches.items():
            if key not in other.branches or other.branches[key] != self.branches[key]:
                return false
        return True
