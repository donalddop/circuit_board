''' Author: Donald Nikkessen

This file contains the class circuit_board which models a board with a
configuration of gates and connections. It can then try to make all the
connections using the A* algorithm and print out a text file containing
the manufacturing specification.

'''

import numpy as np
import random
from operator import itemgetter

import read_board
import a_star

class circuit_board:
    ''' Construct a board given a set of gates, gate connections
    and dimensions.

    Constructing each board as a class allows easy setup for different
    combinations of gates and connections.

    Inputs:
    gates: A dict containing gates and their coordinates
    connections: A list of gate pairs that need to be connected
    dimensions: the dimensions for the board

    Board consists of :
    dimensions: Organized as (z,x,y)
    gates: The gates dict from the input
    connections: List of gate connections
    free_connectors: Set of vacant gate connectors
    needs_connections: Dict of total connections each gate needs,
        this helps the program decide if connectors can be crossed.
    neighbor_of: Dict mapping nodes neighbouring gates to those gates
    '''
    def __init__(self, gates, connections, dimensions):

        # Init basic input
        self.dimensions = dimensions
        self.gates = gates
        self.connections = connections

        # Make the board and fill in gates.
        self.board = self.reset_board()

    def reset_board(self):
        board = np.full(self.dimensions, '__')
        self.board = board
        for gate, loc in self.gates.items():
            self.set_node(loc, 'GA')

        # Count the number of connections required by each gate
        self.needs_connections = self.gate_connectors(self.connections)

        # Make a dict mapping nodes to a list of neighbouring gates
        self.neighbor_of = {}
        for gate, loc in self.gates.items():
            for neighbor in a_star.node_neighbors(self, loc):
                if neighbor in self.neighbor_of:
                    self.neighbor_of[neighbor].append(gate)
                else:
                    self.neighbor_of[neighbor] = [gate]

        # Keep track of all free connectors to gates
        self.free_connectors = set()
        for gate, loc in self.gates.items():
            for neighbor in a_star.node_neighbors(self, loc):
                self.free_connectors.add(neighbor)

        return board

    def set_node(self, loc, val):
        ''' Sets a node to the desired value. '''
        self.board[ loc[0] ][ loc[1] ][ loc[2] ] = val

    def delete_connection(self, i, name):
        ''' Clears a connection from the board. '''
        self.needs_connections[self.connections[i][0]] += 1
        self.needs_connections[self.connections[i][1]] += 1
        self.board = np.where(self.board == name, '__', self.board)

    def gate_connectors(self, connections):
        ''' Counts all connections to each gate.
            returns:
                counts: Dict mapping a gate to a count.
        '''
        counts = {}
        for (n1, n2) in connections:
            if n1 in counts:
                counts[n1] += 1
            else:
                counts[n1] = 1
            if n2 in counts:
                counts[n2] += 1
            else:
                counts[n2] = 1
        return counts

    def connect_gates(self, gates):
        ''' Find the shortest path for a pair of gates.
            input:
                gates: tuple of gates to be connected
            returns:
                best: the shortest available path
        '''
        best = []
        n1 = a_star.node_neighbors(self, self.gates[gates[0]])
        n2 = a_star.node_neighbors(self, self.gates[gates[1]])
        for neighbor_1 in n1:
            for neighbor_2 in n2:
                path = a_star.search(neighbor_1, neighbor_2, self)
                if path != False and best == []:
                    best = path
                    continue
                if path != False and len(path) < len(best):
                    best = path
        return best

    def complete_board(self):
        ''' Connect all gates according to the connection scheme. '''
        # Sort connections by distance
        indexes = list(range(len(self.connections)))
        distances = [len(self.connect_gates(c)) for c in self.connections]
        dist_idx = zip(indexes, distances)
        ordering = [item[0] for item in sorted(dist_idx, key=itemgetter(1))]
        visited = [ordering]

        # Initialization
        iter = 0
        max_iters = 1000
        best_solution = ordering
        v_opt = 2
        best_score = 0
        required_connections = len(self.connections)
        completed_previously = 0
        wire_names = ["%02d" % x for x in range(1,len(self.connections) + 1)]
        completed_wires = []

        while required_connections - len(completed_wires) > 0:
            # Fill in using current ordering
            for i in ordering:
                if i in completed_wires:
                    continue
                path = self.connect_gates(self.connections[i])
                if len(path) > 0:
                    completed_wires.append(i)
                    self.needs_connections[self.connections[i][0]] -= 1
                    self.needs_connections[self.connections[i][1]] -= 1
                name = wire_names[i]
                for node in path:
                    self.set_node(node, name)
            # Save improvements to best score
            if len(completed_wires) > best_score:
                best_score = len(completed_wires)
                best_solution = self.board
                print("New best score: ", best_score)

            # Algorithm has converged
            if len(completed_wires) == completed_previously:
                # Stop after max iterations
                if iter == max_iters:
                    break
                # Initialize next solution attempt
                # Delete n connections
                to_delete = random.sample(completed_wires, v_opt)
                for j in to_delete:
                    self.delete_connection(j, wire_names[j])
                    completed_wires.remove(j)
                # Shuffle the connection ordering
                ordering = random.sample(ordering, len(ordering))
                iter += 1
            completed_previously = len(completed_wires)

        # Return best solution
        self.board = best_solution
        print(best_score, ' out of ', required_connections)

    def output_solution(self, new_file):
        ''' Output the solution for the board to a text files
            input(str) new_file: the title for the new file
        '''
        f = open(new_file, 'w')
        z = 1
        for layer in self.board:
            layer_line = '### Layer ' + str(z) + ' ###\n'
            f.write(layer_line)
            for row in layer:
                line = " ".join(item for item in row) + '\n'
                f.write(line)
            z += 1
        f.close()

if __name__ == "__main__":
    gates1, connections1 = read_board.process_file('circuit_board_1.xlsx')
    board_1 = circuit_board( gates1, connections1[0], (7,18,13) )
    board_1.complete_board()
    board_1.output_solution('board1_list1.txt')

    board_2 = circuit_board( gates1, connections1[1], (7,18,13) )
    board_2.complete_board()
    board_2.output_solution('board1_list2.txt')

    board_3 = circuit_board( gates1, connections1[2], (7,18,13) )
    board_3.complete_board()
    board_3.output_solution('board1_list3.txt')

    gates2, connections2 = read_board.process_file('circuit_board_2.xlsx')

    board_4 = circuit_board( gates2, connections2[0], (7,18,17) )
    board_4.complete_board()
    board_4.output_solution('board2_list1.txt')

    board_5 = circuit_board( gates2, connections2[1], (7,18,17) )
    board_5.complete_board()
    board_5.output_solution('board2_list2.txt')

    board_6 = circuit_board( gates2, connections2[2], (7,18,17) )
    board_6.complete_board()
    board_6.output_solution('board2_list3.txt')
