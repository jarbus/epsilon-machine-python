from collections import defaultdict, Counter
from typing import Dict, Sequence, List
from functools import partial, reduce
import sys
import os

from parse_tree_node import ParseTreeNode
from morph_processor import MorphProcessor
import random
from tqdm import tqdm

random.seed(0)

history = []
last_state = 0
for i in tqdm(range(100000)):
    if last_state == 0:
        history.append(random.choice([0, 1]))
    elif last_state == 1:
        history.append(random.choice([0, 0, 1]))
    last_state = history[-1]


root = ParseTreeNode(target_depth=4)

for j in tqdm(range(len(history) - 5)):
    s1, s2, s3, s4, s5 = history[j : j + 5]
    root[s1][s2][s3][s4][s5].value += 1

mp = MorphProcessor(D=5, K=2, L=1)
mp.process_morphs(root)
statefile = "example-state.txt"
root.generate_state_diagram(file=statefile)
eMfile = "example-em.txt"
mp.generate_eM_diagram(file=eMfile)
os.system(f"sxiv {statefile[:-3]+'png'}")
os.system(f"sxiv {eMfile[:-3]+'png'}")


"""
We can check if trees are equal by checking if the probability of
their leaves are equal. This is because the bottom must add up to the top?

Subtree reconstruction:
    Given: Word Distributions P(s^D), D=1,2,3...
    Steps:
        1. Form depth-D parse tree
        2. Calculate node-to-node transition probabilities
        3. Causal states: Find morphs P(s{->L} | s{<-K}) as subtrees
        4. Label tree nodes with morph (causal state) names
        5. Extract state-to-state transitions from parse tree
        6. Assemble into eM, M = {S, {T^s, s in A}}

        Algorithm parameters D, L, K
"""
