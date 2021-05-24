import sys
import itertools
import time as t
from pqdict import maxpq


# Represents a proposition
class Prop:
    _id = 1

    def __init__(self):
        self.domain = (0, 1)  # Truth values
        self.value = None  # Prop value
        self.id = Prop._id  # Prop id
        self.unit = 0  # Unit propagation metric
        self.polarity = 0  # Polarity metric
        Prop._id += 1

    # Expand props that are unitary first, and use correct polarity
    @property
    def priority(self):
        id_order = 1 - (self.id / Prop._id)
        if self.polarity > 0:  # Start with predominant type (+/-)
            self.domain = (1, 0)
        else:
            self.domain = (0, 1)
        return 2 * self.unit + 1 * id_order

    def __str__(self):
        return f'P: {self.id}, Value: {self.value}\n'


# Represents the CNF formula
class Formula:
    def __init__(self, formula):
        self.formula = formula
        self.props = []
        for p in range(1, formula['n_props'] + 1):  # Props
            self.props.append(Prop())
        self.queue = maxpq()  # Priority Queue
        for prop in self.props:
            self.queue.additem(prop.id, prop.priority)
        self.count = 0

    # Evaluate formula with complete valuation
    def eval(self):
        n_closure = 0
        result = 0
        evaluating = True
        while evaluating:
            closure = self.formula['closures'][n_closure]
            n_prop = 0
            checking = True
            while checking:
                prop = closure[n_prop]
                if (prop > 0) and self.props[prop - 1].value:
                    checking = False
                elif (prop < 0) and not self.props[- prop - 1].value:
                    checking = False
                else:
                    n_prop += 1
                    if n_prop == len(closure):
                        checking = False
                        evaluating = False
            n_closure += 1
            if evaluating and (n_closure == self.formula['n_closures']):
                result = 1
                evaluating = False
        return result

    # Evaluate formula with currently assigned propositions
    def partial_eval(self):
        n_closure = 0
        evaluating = True
        early_solution = True
        unit_set = set()
        polar_set = set()
        while evaluating:
            closure = self.formula['closures'][n_closure]
            n_prop = 0
            checking = True
            unassigned = 0
            current_unassigned = 0
            while checking:  # Current closure
                prop = closure[n_prop]
                if (prop > 0) and self.props[prop - 1].value is None:
                    unassigned += 1
                    current_unassigned = prop
                elif (prop < 0) and self.props[- prop - 1].value is None:
                    unassigned += 1
                    current_unassigned = prop
                elif (prop > 0) and self.props[prop - 1].value:
                    checking = False
                elif (prop < 0) and not self.props[- prop - 1].value:
                    checking = False
                if checking:
                    n_prop += 1
                    if n_prop == len(closure):  # Closure is currently unsat
                        checking = False
                        early_solution = False
                        if not unassigned:  # Prune impossible closures
                            return - 1
                        elif unassigned == 1:  # Unit propagation
                            if - current_unassigned in unit_set:
                                return - 1
                            index = current_unassigned - 1
                            if current_unassigned < 0:
                                index = - current_unassigned - 1
                            unit_prop = self.props[index]
                            if current_unassigned not in unit_set:
                                unit_set.add(current_unassigned)
                                unit_prop.unit = 1
                            else:
                                unit_prop.unit += 1
                            self.queue.updateitem(
                                unit_prop.id, unit_prop.priority)
                        for p in closure:  # Polar literals
                            index = p - 1
                            if p < 0:
                                index = - p - 1
                            polar_prop = self.props[index]
                            if polar_prop.value is None:
                                pole = 1
                                if p < 0:
                                    pole = - 1
                                if (p in polar_set) or (- p in polar_set):
                                    polar_prop.polarity += pole
                                else:
                                    polar_prop.polarity += pole
                                    polar_set.add(p)
                                self.queue.updateitem(
                                    polar_prop.id, polar_prop.priority)
            n_closure += 1
            if n_closure == self.formula['n_closures']:
                if early_solution:  # Early solution without assigning all props
                    return 1
                evaluating = False
        return 0  # Keep expanding, lack of information

    # Evaluate current prop values
    def is_solution(self):
        self.count += 1
        return self.eval()

    # Choose next prop to expand
    def choose_prop(self):
        prop_id, _ = self.queue.popitem()
        chosen_prop = self.props[prop_id - 1]
        chosen_prop.unit = 0
        chosen_prop.polarity = 0
        return chosen_prop

    # Solve the SAT problem
    def is_solvable(self):
        prop = self.choose_prop()  # Next prop
        for value in prop.domain:  # Try with 0,1
            prop.value = value  # Assign value
            if self.queue:  # Partial evaluation
                self.count += 1
                partial_result = self.partial_eval()
                if partial_result == 1:  # Early solution
                    return True
                elif not partial_result:  # Keep expanding
                    if self.is_solvable():
                        return True
            elif self.is_solution():  # Complete evaluation
                return True
            prop.value = None  # Remove value
        self.queue[prop.id] = prop.priority
        return False


# Generate combinations for brute force approach
def get_combinations(n):
    return itertools.product([0, 1], repeat=n)


# Evaluate formula with specific valuation
def evaluate(values, formula):
    n_closure = 0
    result = 0
    evaluating = True
    while evaluating:
        closure = formula['closures'][n_closure]
        n_prop = 0
        checking = True
        while checking:
            prop = closure[n_prop]
            if (prop > 0) and values[prop - 1]:
                checking = False
            elif (prop < 0) and not values[- prop - 1]:
                checking = False
            else:
                n_prop += 1
                if n_prop == len(closure):
                    checking = False
                    evaluating = False
        n_closure += 1
        if evaluating and (n_closure == formula['n_closures']):
            result = 1
            evaluating = False
    return result


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
    result = 0
    generator = get_combinations(formula['n_props'])
    for combination in generator:
        result = evaluate(combination, formula)
        if result:
            return result, t.time() - start
    return result, t.time() - start


# Custom DPLL-based solver
def improved(formula):
    start = t.time()
    result = 0
    state = Formula(formula)
    if state.is_solvable():
        result = 1
    return result, t.time() - start


# Execute solver
if __name__ == '__main__':
    try:
        processed = dimacs(sys.argv[1])
        if int(sys.argv[2]):
            sat, exec_time = improved(processed)
        else:
            sat, exec_time = exhaustive(processed)
        print(f'\nSAT: {bool(sat)}\nExecution Time: {round(exec_time, 6)} '
              f'seconds')
    except IndexError:
        if len(sys.argv) < 2:
            print('\nYou need to specify the path to a file containing the CNF '
                  'formula!')
        else:
            print('\nYou need to specify the solving method: '
                  '[0] -> Exhaustive, [1] -> DPLL')
    except FileNotFoundError:
        print('Invalid path to file!')
