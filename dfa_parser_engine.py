import argparse, pathlib
from itertools import chain


def reading(sigma, delta, states, file_name):
    f = open(file_name)
    linie = f.readline()

    while linie:
        linie = linie[:(len(linie) - 1)]
        if linie[0] == "#":
            linie = f.readline()
            continue

        if linie == "Sigma:":
            linie = f.readline()
            while linie.lower() != "end\n" and linie.lower() != "end":
                if linie[0] == '#':
                    linie = f.readline()
                    continue

                sigmaLine = linie.strip().split("#")
                sigma.append(sigmaLine[0].strip())

                linie = f.readline()

        elif linie == "Transitions:":
            linie = f.readline()
            while linie.lower() != "end" and linie.lower() != "end\n":
                if linie[0] == "#":
                    linie = f.readline()
                    continue

                transitionLine = linie.strip("\n").split("#")
                transitionLine = transitionLine[0].split(",")
                transitionLine = list(map(lambda s: s.strip(), transitionLine))
                transitionLine = list(filter(lambda s: len(s) != 0, transitionLine))

                if len(transitionLine) != 3:
                    raise Exception(
                        f"[DFA] Invalid Syntax at line: {linie}, we need 3 states to complete the transitions")

                if transitionLine[0] not in delta.keys():
                    delta[transitionLine[0]] = {transitionLine[2]: [transitionLine[1]]}
                else:
                    if transitionLine[2] not in delta[transitionLine[0]].keys():
                        delta[transitionLine[0]][transitionLine[2]] = [transitionLine[1]]
                    else:
                        delta[transitionLine[0]][transitionLine[2]].append(transitionLine[1])

                linie = f.readline()

        elif linie == "States:":
            linie = f.readline()
            while linie.lower() != "end" and linie.lower() != "end\n":
                if linie[0] == '#':
                    linie = f.readline()
                    continue

                statesLine = linie.strip().split("#")
                statesLine = statesLine[0].split(",")

                if len(statesLine) == 2:
                    states[statesLine[0]] = "S" if statesLine[1].strip() == "S" else "F"
                elif len(statesLine) > 2:
                    states[statesLine[0]] = "S/F"
                else:
                    states[statesLine[0]] = "I"

                linie = f.readline()

        linie = f.readline()
    f.close()

sigma = []
delta = {}
states = {}
visited = {}
found = False

def validate_states():
    return True if list(states.values()).count("S") == 1 and list(states.values()).count("F") > 0 \
                   or list(states.values()).count("S/F") > 0 else False


def validate_transitions():
    if len(list(filter(lambda s: s not in list(states.keys()), delta.keys()))):
        return False

    for key in delta:
        if len(list(filter(lambda s: s not in list(states.keys()), delta[key].keys()))):
            return False
        if len(list(filter(lambda s: s not in sigma, list(chain(*list(delta[key].values())))))):
            return False
        if len(list(chain(*delta[key].values()))) != len(set(list(chain(*delta[key].values())))):
            return False

    return True


def validate_road(state):
    global found
    global visited

    visited[state] = True
    if states[state] == "S/F" or states[state] == "F":
        found = True
    else:
        for deltaState in delta[state]:
            if not visited[deltaState] and not found:
                validate_road(deltaState)
                visited[deltaState] = False
    return found


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Given a specific config file we need to parse the contents of it.')
    parser.add_argument('file', type=pathlib.Path)
    args = parser.parse_args()

    try:
        reading(sigma, delta, states, args.file)

        for state in states:
            visited[state] = False

        start_state = None
        for state in states:
            if states[state] == "S" or states[state] == "S/F":
                start_state = state

        if validate_states() and validate_transitions() and start_state is not None and validate_road(start_state):
            print("The received automata config is a valid DFA")
        else:
            print("The received automata config is NOT a valid DFA")
    except Exception as exception:
        print(exception.args)