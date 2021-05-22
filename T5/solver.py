import sys
import time as t
import numpy as np


# Parse input file
def dimacs(path):
    formula = {'n_props': 0, 'n_closures': 0, 'closures': []}
    with open(path, 'r') as file:
        n_closures = 0
        for line in file:
            info = line.strip('\n').split()
            if info and (info[0] == 'p'):
                n_closures = int(info[3])
                formula['n_props'] = int(info[2])
                formula['n_closures'] = n_closures
            elif n_closures:
                formula['closures'].append([int(n) for n in info[:-1]])
                n_closures -= 1
    return formula


# Brute force solver
def exhaustive(formula):
    start = t.time()
    # TODO: Generate combinations with generator
    solving = True
    result = 0
    while solving:
        # TODO: Generate combinations with generator
        valuation = 0
        result = evaluate(valuation, formula)
        solving = False
    return result, t.time() - start


# DPLL solver
def improved(formula):
    pass


# Evaluate formula with specific valuation
def evaluate(values, formula):
    # TODO: Eval each combination with function that iterates over formula['closures']
    evaluating = True
    while evaluating:
        checking = True
        while checking:
            checking = False
        if 1:
            evaluating = False
    return 1

# Execute solver
if __name__ == '__main__':
    try:
        processed = dimacs(sys.argv[1])
        sat, exec_time = exhaustive(processed)
        print(sat, exec_time)
        print('Finished!')
    except IndexError:
        print('You need to specify the path to a file containing the CNF '
              'formula!')
    except FileNotFoundError:
        print('Invalid path to file!')
