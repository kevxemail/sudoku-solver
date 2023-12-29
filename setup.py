from math import sqrt
def print_board(N, subblock_width, subblock_height, forward_dict): # Method to print the state as the actual board instead of just a string
    result = ""
    colCount = 0
    rowCount = 0
    for i in range(N*N):
        spaces = (N - len(forward_dict[i]))//2 # Get a good amount of spaces, we want each cell to have N spaces possible to visibly see the options in the forward_dict
        result += " " * (spaces)
        result += forward_dict[i]
        result += " " * (spaces)
        if (2 * spaces + len(forward_dict[i]) < (N+1)):
            result += " " * (N - (2 * spaces + len(forward_dict[i]))+1)
        colCount += 1
        if (colCount) % subblock_width == 0: # Blank space because we've had enough on this row to help carve out the subblock
            result += " || " 
        if colCount == N: # New line since we've completed a row
            result += "\n"
            colCount = 0
            rowCount += 1
        if rowCount == subblock_height: # Add a blank row since we've filled enough rows for all of them to be a subblock
            result += "\n"
            rowCount = 0
    return result

def get_subblock_dimensions(N): # Helper method for get_information to get the subblock width and height, N is how many rows/columns there are for NxN board
    root = sqrt(N)
    if root % 1 == 0: return [int(root), int(root)] # If it's a perfect square just return the root for both dimensions
    else: # The width is the smallest FACTOR of N GREATER than the square root, and height is the smallest FACTOR of N LESS than the square root
        less = int(sqrt(N)) # If it's not a perfect square, doing int will round down. ex: sqrt(12) = 3.46, int(3.46) = 3
        greater = int(sqrt(N)) + 1
        while (N % greater != 0):
            greater += 1 # Increment greater until we find something that divides the board
        while (N % less != 0):
            less -= 1 # Decrement less until we find something that divides the board
        return [greater, less] # Greater = width, less = height

def get_information(state): # Returns N, subblock_width, subblock_height, and symbol set
    N = int(sqrt(len(state))) # A sudoku board is NxN spaces, so N = sqrt(NxN)
    subblock_width, subblock_height = get_subblock_dimensions(N) # Helper method to get the dimensions

    charVal = 65 # In ASCII, uppercase A starts at 65
    symbols = list()
    for i in range(N):
        if (i > 8):
            symbols.append(chr(charVal)) # chr() converts from integer to the string representation of the character
            charVal += 1
        else:
            symbols.append(str(i+1)) # Starts at 1 so +1
    return [N, subblock_width, subblock_height, symbols] # Return all the information

