''' Author: Donald Nikkessen

This file contains a version of the A* algorithm as based on
the page https://en.wikipedia.org/wiki/A*_search_algorithm.

It implements the manhattan distance as the heuristic function.
By applying the rules in the function node_neighbors the algorithm
produces lines that follow the design specifications for the board.

The external library openpyxl is used to read the xlsx file.
'''

def search(start, goal, c_board):
    ''' Returns the shortest path given the current board state.

    Inputs:
        start, goal: the nodes to be connected
        c_board: an instance of the circuit_board class
    Returns:
        A list containing an ordered path for a line.
    '''
    closed_set = set()
    open_set = set()
    open_set.add(start)
    came_from = {}
    g_score = {start : 0}
    f_score = {start : manhattan(start, goal)}

    while open_set != set():
        fscores = {}
        for key, value in f_score.items():
            if key in open_set:
                fscores[key] = value
        current = min(fscores, key=fscores.get)
        if current == goal:
            return reconstruct_path(came_from, current)

        open_set.remove(current)
        closed_set.add(current)

        for neighbor in node_neighbors(c_board, current):
            if neighbor in closed_set:
                continue

            if neighbor not in open_set:
                open_set.add(neighbor)

            tent_gscore = g_score[current] + manhattan(current, neighbor)
            if tent_gscore >= g_score.get(neighbor, 1000):
                continue

            came_from[neighbor] = current
            g_score[neighbor] = tent_gscore
            f_score[neighbor] = g_score[neighbor] + manhattan(neighbor, goal)

    return False

def reconstruct_path(came_from, current):
    ''' Reconstruct the path taken in a_star.

    Inputs:
        came_from: dict of steps taken
        current: the end point of the path
    Returns:
        A list containing an ordered path for a line.
    '''
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    return total_path

def manhattan(start, end):
    ''' Returns the manhattan distance between two nodes.'''
    return sum(abs(e - s) for s,e in zip(start,end))

def node_neighbors(c_board, node):
    ''' Find all vacant neighbors of the current node.

    Inputs:
        c_board: an instance of the circuit_board class
        node: the current node
    Returns:
        A list containing vacant neighbors.
    '''
    board = c_board.board
    (bz,bx,by) = c_board.dimensions
    (nz,nx,ny) = node
    neighbors = []

    # Check for all six directions if they are vacant and on the board
    if node[0] < bz - 1 and board[nz + 1][nx][ny] == '__':
        neighbors.append( (node[0] + 1, node[1], node[2]) )
    if node[0] > 0 and node[0] < bz and board[nz - 1][nx][ny] == '__':
        neighbors.append( (node[0] - 1, node[1], node[2]) )
    if node[1] < bx - 1 and board[nz][nx + 1][ny] == '__':
        neighbors.append( (node[0], node[1] + 1, node[2]) )
    if node[1] > 0 and node[1] < bx and board[nz][nx - 1][ny] == '__':
        neighbors.append( (node[0], node[1] - 1, node[2]) )
    if node[2] < by - 1 and board[nz][nx][ny + 1] == '__':
        neighbors.append( (node[0], node[1], node[2] + 1) )
    if node[2] > 0 and node[2] < by and board[nz][nx][ny - 1] == '__':
        neighbors.append( (node[0], node[1], node[2] - 1) )

    # Do not cross any connectors of gates that have pending connections.
    for node in neighbors:
        if node in c_board.needs_connections:
            if not check_free_connector(c_board, node):
                neighbors.remove(node)
    return neighbors

def check_free_connector(c_board, connector_node):
    ''' Returns True if the gates neighbouring this connector do not require
        more connections.
    '''
    for gate in c_board.neighbor_of[connector_node]:
        if c_board.needs_connections[gate] == 0:
            return True
    return False
