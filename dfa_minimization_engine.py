import argparse, pathlib
from dfa_parser_engine import reading

sigma = []
delta = {}
states = {}


def flatten(t):
    return [item for sublist in t for item in sublist]


def myhill_nerode(security_arg=None):
    matrix = {key:
                  {insideKey: True if (((states[insideKey] == "S/F" or states[insideKey] == "F") and (states[key] == "S" or states[key] == "I"))
                                      or ((states[key] == "S/F" or states[key] == "F") and (states[insideKey] == "S" or states[insideKey] == "I")))
                                       and key != insideKey else False for insideKey in states}
              for key in states}
    appearances = {tuple([key1, key2]): False for key1 in states for key2 in states}

    iterate_states = []
    for firstState in states:
        for secondState in states:
            if matrix[firstState][secondState] is not True and firstState != secondState \
                    and appearances[tuple([firstState, secondState])] is not True:
                iterate_states.append([firstState, secondState])
                appearances[tuple([firstState, secondState])] = appearances[tuple([secondState, firstState])] = True

    iterations_overflow = 0
    oldMatrix = {}
    while oldMatrix != matrix and (iterations_overflow != security_arg or security_arg is None):
        oldMatrix = matrix
        for current in iterate_states:
            for symbol in sigma:
                firstToGo = None
                secondToGo = None

                for firstState in delta[current[0]]:
                    firstToGo = None
                    for transitionSymbol in delta[current[0]][firstState]:
                        if transitionSymbol == symbol:
                            firstToGo = firstState

                for secondState in delta[current[1]]:
                    secondToGo = None
                    for transitionSymbol in delta[current[1]][secondState]:
                        if transitionSymbol == symbol:
                            secondToGo = secondState

                if firstToGo is not None and secondToGo is not None:
                    if matrix[firstToGo][secondToGo] is True:
                        matrix[current[0]][current[1]] = matrix[current[1]][current[0]] = True
                        break

    iterate_states = list(filter(lambda current : matrix[current[0]][current[1]] is False, iterate_states))

    # Source: https://stackoverflow.com/a/4842897
    combined_states = []
    while len(iterate_states) > 0:
        first, *rest = iterate_states
        first = set(first)
        lf = -1
        while len(first) > lf:
            lf = len(first)
            rest2 = []
            for r in rest:
                if len(first.intersection(set(r))) > 0:
                    first |= set(r)
                else:
                    rest2.append(r)
            rest = rest2
        combined_states.append(first)
        iterate_states = rest

    new_states = {}
    for state in combined_states:
        marking = "I"
        for small_state in state:
            if states[small_state] == "S" and marking != "F" and marking != "S/F":
                marking = "S"
            elif states[small_state] == "S" and marking == "F":
                marking = "S/F"
            elif states[small_state] == "F" and marking != "S" and marking != "S/F":
                marking = "F"
            elif states[small_state] == "S/F":
                marking = "S/F"
        new_states[tuple(state)] = marking

    for state in states:
        if state not in flatten(list(new_states.keys())):
            new_states[state] = states[state]

    map_state_to_composed = {}
    for state in combined_states:
        for small_state in state:
            map_state_to_composed[small_state] = tuple(state)

    for state in states:
        if state not in flatten(list(new_states.keys())):
            map_state_to_composed[state] = state

    return {'states': new_states, 'mapComposed': map_state_to_composed}


def showCompositeState(state):
    if len(state) > 1 and type(state) is tuple:
        string = "(" + ", ".join([i for i in state]) + ")"
    else:
        string = state
    return string


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Given a specific file which represents the config file of a DFA output a minimized DFA.')
    parser.add_argument('file', type=pathlib.Path)
    parser.add_argument('-s', '--security', nargs='?', type=int)
    args = parser.parse_args()

    try:
        reading(sigma, delta, states, args.file)
        result = myhill_nerode(args.security)
        transitions = list(dict.fromkeys([
            f"{result['mapComposed'][from_state]}, {symbol}, {result['mapComposed'][where_state]}\n"
            for from_state in delta
            for where_state in delta[from_state]
            for symbol in delta[from_state][where_state]
        ]))

        f = open("dfa_minimized_config", "w")
        f.write("Sigma:\n")
        for i in sigma:
            f.write(f"{i}\n")
        f.write("End\n\n")
        f.write("States:\n")
        for states in result['states']:
            shown = showCompositeState(states)
            if result['states'][states] == "I":
                f.write(f"{shown}\n")
            elif result['states'][states] == "S/F":
                f.write(f"{shown}, S, F\n")
            elif result['states'][states] == "F":
                f.write(f"{shown}, F\n")
            elif result['states'][states] == "S":
                f.write(f"{shown}, S\n")
        f.write("End\n\n")
        f.write("Transitions:\n")
        for transition in transitions:
            f.write(transition)
        f.write("End")
        f.close()
    except Exception as exception:
        print(exception.args)

