from math import sqrt
from setup import print_board, get_subblock_dimensions, get_information
import sys
from collections import deque
from time import perf_counter

def generate_constraints_sets(N, subblock_width, subblock_height): # Helper method to generate_constraint_dictionaries. Generate the constraint sets before setting indices to dictionaries
    board = [[col + row * N for col in range(N)] for row in range(N)] # Initialize a 2D matrix representing the board with indexes 1 to N*N-1 
    constraint_sets = list()
    for row in range(N):
        rowSet = set()
        colSet = set()
        for col in range(N): 
            rowSet.add(board[row][col]) # Symbols in each row can't repeat so add to constraints
            colSet.add(board[col][row]) # Symbols in each col can't repeat so add constraints
        constraint_sets.append(rowSet)
        constraint_sets.append(colSet)
    # Hard part, traverse subblock to subblock to create constraint sets
    start_height = 0
    start_width = 0
    while (start_height < N): # Once the height exceeds N, we've processed the whole board
        blockSet = set()
        for row in range(start_height, start_height+subblock_height):
            for col in range(start_width, start_width+subblock_width):
                blockSet.add(board[row][col])
        constraint_sets.append(blockSet)
        start_width += subblock_width # Shift the start to the right, for the next block
        if start_width == N: # Once we've processed an entire row of subblocks, do the same for the next row
            start_width = 0
            start_height += subblock_height
    return constraint_sets

def generate_constraint_dictionary(N, subblock_width, subblock_height): # Generates a dictionary for each index based on what other indexes are restricted based on the current one
    constraint_sets = generate_constraints_sets(N, subblock_width, subblock_height)
    constraint_dict = dict()
    for i in range(N*N):
        neighbors = set() # Neighbors = same row, same column, or same subblock
        for currSet in constraint_sets:
            if i in currSet:
                neighbors = neighbors.union(currSet) # Add all the elements to the neighbors set
        neighbors.remove(i) # This index is not a neighbor to itself
        constraint_dict[i] = neighbors # Set the index's dictionary to point to its neighbors
    return [constraint_dict, constraint_sets]

def generate_forward_looking_dictionary(state, symbols):
    forward_dict = dict()
    for i in range(len(state)):
        if state[i] == ".":
            forward_dict[i] = "".join(symbols) # Store all the symbols since right now all are possible
        else:
            forward_dict[i] = str(state[i])
    return forward_dict

def forward_looking(forward_dict, constraint_dict, constraint_sets, symbols): # Actually do the forward looking
    to_forward = deque()
    for i in range(len(forward_dict)): # Get all the indexes we can forward look off of
        if len(forward_dict[i]) == 1: # Solved value
            to_forward.append(i) # Append index of the solved value 
    checked = set()
    while len(to_forward) > 0: # This terminates once we're done with forward looking
        index = to_forward.popleft()
        checked.add(index) # Don't want to append the same index over again
        curr_symbol = forward_dict[index]
        for neighbor in constraint_dict[index]:
            if curr_symbol in forward_dict[neighbor]: # Remove from the neighbor's possibilities since in sudoku u can't repeat values for neighbors
                forward_dict[neighbor] = forward_dict[neighbor].replace(curr_symbol, "") # Remove that character from the neighbor's possibilities
                if (len(forward_dict[neighbor]) == 1): # We've solved that position, if only one possibility left do forward looking on that position as well
                    if (neighbor not in to_forward and neighbor not in checked): # Again, don't want to check the same index multiple times
                                to_forward.append(neighbor)
                if (len(forward_dict[neighbor]) < 1): # Bad choice has been made with backtracking if we removed ALL possibilities
                        return None    
    return forward_dict

def constraint_propagation(forward_dict, constraint_dict, constraint_sets, symbols): # Do constraint propagation, where each row, column, and block must have at least one of each symbol
    changed = set()
    for constraint_set in constraint_sets: # Iterate through all the constraint sets
        symbol_indices = dict()
        for symbol in symbols: # Keep track of where we found the indices for a particular symbol
            symbol_indices[symbol] = list()
        for index in constraint_set: # Go through each index of the constraint set to count up the symbols
            for symbol in forward_dict[index]:
                symbol_indices[symbol].append(index)
        for key in symbol_indices:
            currlist = symbol_indices[key]
            if len(currlist) == 0:
                return None, None
            index = currlist[0]
            if len(currlist) == 1 and len(forward_dict[index]) > 1: # We found something to shorten
                forward_dict[index] = key
                changed.add(index)
    return [forward_dict, deque(changed)]

def csp_backtracking_with_forward_looking(forward_dict, constraint_dict, constraint_sets, symbols):
    if (goal_test(forward_dict)): 
        return dict_to_str(forward_dict) # Convert it back to a string
    var = get_most_constrained_index(forward_dict) # The one with the least possible options that isn't solved (1 option = solved)
    sorted_values = get_sorted_values(forward_dict, var) # Just gets the possible values at that specific index
    for val in sorted_values:
        new_board = forward_dict.copy() # MUST copy for backtracking on a dictionary, otherwise changes will persist
        new_board[var] = val
        checked_board = forward_looking(new_board, constraint_dict,  constraint_sets, symbols) # Do forward_looking, it will detect if something is wrong by returning None
        if checked_board is not None: # Make sure we didn't make a bad decision during forward_looking
            checked_board, changed = constraint_propagation(checked_board, constraint_dict, constraint_sets, symbols) # Do constraint propagation
            """
            Note: I don't do a loop of forward_looking/constraint propagation because I kept getting None values. Not sure why but I think it's because
            if we're going down an incorrect path it'll just return None, mess up the next iteration, and terminate the backtracking with an error. I could try to work around it
            but i've spent too much time on this and my code is fast enough.
            """

            if checked_board != None: # Don't return None if this board is None, just skip otherwise the whole backtrack system will return None falsely
                result = csp_backtracking_with_forward_looking(checked_board, constraint_dict, constraint_sets, symbols)
                if result is not None: # Only return None down here because we've exhausted all options
                    return result
    return None

def get_most_constrained_index(forward_dict): # Get the index of the next position to be processed, represented by a .
    smallest = 1000
    smallest_index = -1
    for key in forward_dict: # Get the index with least possibilities that isn't solved
        if len(forward_dict[key]) > 1: 
            if len(forward_dict[key]) < smallest:
                smallest = len(forward_dict[key])
                smallest_index = key
    return smallest_index

def get_sorted_values(forward_dict, var): # Access the neighbors by finding the current index (var)'s key in the dictionary, these aren't allowed
    return list(forward_dict[var])

def goal_test(forward_dict): # See if the length of each value of the dictionary is 1, meaning it's solved
    for key in forward_dict:
        if len(forward_dict[key]) != 1:
            return False
    return True

def dict_to_str(forward_dict): # Convert a dictionary to a string when we find the answer
    result = ""
    for key in forward_dict:
        result += forward_dict[key]
    return result


def solve_sudoku(state):
    N, subblock_width, subblock_height, symbols = get_information(state) # Get the initial information
    constraint_dict, constraint_sets = generate_constraint_dictionary(N, subblock_width,subblock_height) # Set the constraint dictionary and set list
    forward_dict = generate_forward_looking_dictionary(state, symbols) # Dictionary of values we will use as our main "state" where each it's key: index, value: possible values

    checked_dict = forward_looking(forward_dict, constraint_dict, constraint_sets, symbols) # First do forward_looking

    again_dict, changed = constraint_propagation(checked_dict, constraint_dict, constraint_sets, symbols)
    while len(changed) != 0: # Keep doing a cycle of constraint propagation and forward_looking until we don't have anything else to change for now, meaning we start to backtrack
        again_dict = forward_looking(forward_dict, constraint_dict, constraint_sets, symbols)
        again_dict, changed = constraint_propagation(checked_dict, constraint_dict, constraint_sets, symbols)

    return csp_backtracking_with_forward_looking(again_dict, constraint_dict, constraint_sets, symbols) # Start to backtrack

def main():
    with open(sys.argv[1]) as f:
        line_list = [line.strip() for line in f]
    start = perf_counter()
    for i in range(len(line_list)):
        sudoku = line_list[i]
        solved = solve_sudoku(sudoku)
        print(solved)
    end = perf_counter()
    print("Total time:", end-start)
    # print(solve_sudoku(line_list[3]))

if __name__ == "__main__":
    main()