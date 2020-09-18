from parse_tree_node import ParseTreeNode
from typing import Dict, Sequence, List
from collections import defaultdict
import plantuml


class MorphProcessor:
    """Labels each node in a tree with a morph """

    def __init__(self, D: int = 0, K: int = 0, L: int = 0):
        """Arguments:
            D: depth
            K: Past number of levels
            L: Future number of levels
        """
        self.morph_list = []
        self.D = D
        self.K = K
        self.L = L

    def process_morphs(self, root: ParseTreeNode):
        """Computes morphs in a tree and updates ParseTreeNode.morph with the morph number of that node"""

        root.update_probabilities()
        l_nodes = self._get_k_nodes(root)

        # Unfortunately, comparing morphs takes O(N^2) time
        # Didn't want to hack together a hash of
        # the probability distribution
        morphs = [l_nodes[0]]
        for potential_morph in l_nodes:
            new_morph = True
            for morph in morphs:
                if self._compare_l_morph(potential_morph, morph):
                    new_morph = False
                    break
            if new_morph:
                morphs.append(potential_morph)
        print(
            f"Out of {len(l_nodes)} morphs, found {len(morphs)} unique morphs: {[m.id for m in morphs]}"
        )
        self.morph_list = morphs

        self._update_morphs(root, morphs)
        self.transitions = self._compute_transitions()

    def generate_eM_diagram(self, file="default-em-diagram.txt"):
        with open(file, "w") as f:
            f.write("@startuml\n")
            f.write("hide empty description\n")
            for start, branches in self.transitions.items():
                for end, prob in branches.items():
                    print(f"({start}) --> ({end}) : {prob}\n", file=f)
            f.write("@enduml")

        puml = plantuml.PlantUML("http://www.plantuml.com/plantuml/img/")
        puml.processes_file(file)

        pass

    def _compute_transitions(self):
        transitions = defaultdict(lambda: defaultdict(float))
        for morph in self.morph_list:
            for key, branch in morph.branches.items():
                transitions[morph.state][branch.state] = branch.prob
        return transitions

    def _update_morphs(self, node: ParseTreeNode, morphs: List[ParseTreeNode], level=0):
        for i, morph in enumerate(morphs):
            if self._compare_l_morph(node, morph):
                node.morph = i
                break
        if not node.branches:
            return
        for branch in node.branches.values():
            self._update_morphs(branch, morphs, level=level + 1)

    # Compare level k nodes down to their lth level children
    def _compare_l_morph(self, node1: ParseTreeNode, node2: ParseTreeNode, level=0):
        """Returns true if two nodes share the same morph, else false"""

        # If bottom of morph, just compare states and probabilities
        if level == self.L:
            return node1.state == node2.state and node1.prob == node2.prob

        if level > 1 and (node1.prob != node2.prob) or (node1.state != node2.state):
            return False

        # xor, return false of one is leaf and other isn't
        if (
            node1.is_leaf
            or node2.is_leaf
            or node1.branches.keys() != node2.branches.keys()
        ):
            return False

        for key, branch in node1.branches.items():
            if not self._compare_l_morph(branch, node2.branches[key], level=level + 1):
                return False
        return True

    # Recursively retrieves all nodes at the K-th level down.
    def _get_k_nodes(self, node: ParseTreeNode, level=0) -> List[ParseTreeNode]:
        if level == self.K:
            return [node]
        k_nodes = []
        for branch in node.branches.values():
            nodes = self._get_k_nodes(branch, level=level + 1)
            for node in nodes:
                k_nodes.append(node)
        return k_nodes

    def __str__(self):
        return f"Morph Processor with {len(self.morph_list)} morphs"
