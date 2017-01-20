import sys
import random
import signal

#Timer handler, helper function

class TimedOutExc(Exception):
        pass

def handler(signum, frame):
    #print 'Signal handler called with signal', signum
    raise TimedOutExc()

        
class Manual_player:
	def __init__(self):
		pass
	def move(self, temp_board, temp_block, old_move, flag):
		print 'Enter your move: <format:row column> (you\'re playing with', flag + ")"	
		mvp = raw_input()
		mvp = mvp.split()
		return (int(mvp[0]), int(mvp[1]))
		

class Player30:
	
	def __init__(self):
                # Max Depth to recurse in the alpha-beta
		self.depth = 4
                self.flag = None

                self.flags = {'x': 'o',
                              'o': 'x'}

                self.blocked = {0: [1, 3, 4],
                                1: [0, 2, 4],
                                2: [1, 4, 5],
                                3: [0, 4, 6],
                                4: [],
                                5: [2, 4, 8],
                                6: [3, 4, 7],
                                7: [4, 6, 8],
                                8: [4, 5, 7],
                                }
                self.result = {}
                self.valid_moves = []

        # Returns Blocks i can place my move in
        def get_blocks_allowed(self, old_move, temp_block):

                for_corner = [0, 2, 3, 5, 6, 8]

                #List of permitted blocks, based on old move.
                blocks_allowed  = []

                if old_move[0] in for_corner and old_move[1] in for_corner:
                        ## we will have 3 representative blocks, to choose from

                        if old_move[0] % 3 == 0 and old_move[1] % 3 == 0:
                                ## top left 3 blocks are allowed
                                blocks_allowed = [0, 1, 3]
                        elif old_move[0] % 3 == 0 and old_move[1] in [2, 5, 8]:
                                ## top right 3 blocks are allowed
                                blocks_allowed = [1,2,5]
                        elif old_move[0] in [2,5, 8] and old_move[1] % 3 == 0:
                                ## bottom left 3 blocks are allowed
                                blocks_allowed  = [3,6,7]
                        elif old_move[0] in [2,5,8] and old_move[1] in [2,5,8]:
                                ### bottom right 3 blocks are allowed
                                blocks_allowed = [5,7,8]
                        else:
                                print "SOMETHING REALLY WEIRD HAPPENED!"
                                sys.exit(1)
                else:
                #### we will have only 1 block to choose from (or maybe NONE of them, which calls for a free move)
                        if old_move[0] % 3 == 0 and old_move[1] in [1,4,7]:
                                ## upper-center block
                                blocks_allowed = [1]

                        elif old_move[0] in [1,4,7] and old_move[1] % 3 == 0:
                                ## middle-left block
                                blocks_allowed = [3]

                        elif old_move[0] in [2,5,8] and old_move[1] in [1,4,7]:
                                ## lower-center block
                                blocks_allowed = [7]

                        elif old_move[0] in [1,4,7] and old_move[1] in [2,5,8]:
                                ## middle-right block
                                blocks_allowed = [5]
                        elif old_move[0] in [1,4,7] and old_move[1] in [1,4,7]:
                                blocks_allowed = [4]

                for i in reversed(blocks_allowed):
                    if temp_block[i] != '-':
                        blocks_allowed.remove(i)

                # Return Blocks Allowed
                return blocks_allowed

        # Evaluation / Heuristic Function
        def eval(self, temp_board, temp_block, len_blocks):

                # Completed 'X' or 'O' Blocks
                max_done_blocks, min_done_blocks = self.get_no_of_blocks(temp_block)
                # Blocks
                max3_block, min3_block = self.get_n_in_a_row_blocks(temp_block, 3)
                max1_block, min1_block = self.get_n_in_a_row_blocks(temp_block, 1)
                max2_block, min2_block = self.get_n_in_a_row_blocks(temp_block, 2)
                # Cells
                max3_cell, min3_cell = self.get_n_in_a_row_cells(temp_board, 3)
                max1_cell, min1_cell = self.get_n_in_a_row_cells(temp_board, 1)
                max2_cell, min2_cell = self.get_n_in_a_row_cells(temp_board, 2)
        
                #print self.flag 
                if self.flag == 'x':

                        heuristic = (max3_block * 10000) + \
                                     (max_done_blocks * 20 - min_done_blocks * 20) + \
                                     (max2_block * 60 - min2_block * 60) + \
                                     (max1_block * 15 - min1_block * 15) + \
                                     (max2_cell * 10 - min2_cell * 10) + \
                                     (max1_cell * 5 - min1_cell * 5) 

                if self.flag == 'o':

                        heuristic = (min3_block * 10000) + \
                                     (max_done_blocks * 20 - min_done_blocks * 20) + \
                                     (min2_block * 60 - max2_block * 60) + \
                                     (min1_block * 15 - max1_block * 15) + \
                                     (min2_cell * 10 - max2_cell * 10) + \
                                     (min1_cell * 5 - max1_cell * 5)

                return heuristic

        # ####################      MAX     ############################
        # MAX OF MIN-MAX
        def max_value(self, old_move, temp_board, temp_block, depth, alpha, beta):

#                print "Depth"
#                print depth
#                print "--------"
                # Find all possible actions for the given 'board' state
                blocks_allowed  = self.get_blocks_allowed(old_move, temp_block)
                # Cells I can play in 
                cells = get_empty_out_of(temp_board, blocks_allowed, temp_block)

                # CUTOFF
                if depth > self.depth:
#                        print "Max Depth Reached"
                        # Utility for pseudo terminal node
                        return self.eval(temp_board, temp_block, len(blocks_allowed))

                value = -float('inf')
                
                for i in cells:
                        
                        if(depth == 1):
                                pass
#                                print "Yes!"
                        # New State with the following move or action
                        # Better Way ?
                        board = []
                        for k in temp_board[:]:
                                board.append(list(k))
                        block = list(temp_block)
                        update_lists(board, block, tuple(i), self.flag)
                        # Pass Current_Move, modified Board, Block, Inc Depth, Alpha, beta
                        _min = self.min_value(tuple(i), board, block, depth + 1, alpha, beta)
                        if _min >= value:
                                value = _min
                                if depth == 1:
                                        #self.valid_moves = cells[:]
                                        v = str(value)
                                        if self.result.get(v):
                                                self.result[v].append(tuple(i))
                                        else:
                                                #print self.result
                                                self.result[v] = [tuple(i)]
                        if value >= beta:
                                #print value
                                #print beta
                                #print "Pruned"
                                return value
                        
                        if value >= alpha:
                                alpha = value

                return value

        # ####################      MIN     ##############################
        # MIN OF MIN-MAX
        def min_value(self, old_move, temp_board, temp_block, depth, alpha, beta):
                # CUTOFF
#                print "Depth"
#                print depth
#                print "--------"

                # Find all possible actions for the given 'board' state
                blocks_allowed  = self.get_blocks_allowed(old_move, temp_block)
                # Cells I can play in 
                cells = get_empty_out_of(temp_board, blocks_allowed, temp_block)

                if depth > self.depth:
#                        print "Max Depth Reached"
                        # Utility Value for this pseudo terminal node
                        return self.eval(temp_board, temp_block, len(blocks_allowed))

                value = float('inf')

                for i in cells:

                        # New State with the following move or action
                        # Better Way ?
                        board = []
                        for k in temp_board[:]:
                                board.append(list(k))
                        block = list(temp_block)
                        # Opposite Flag
                        update_lists(board, block, i, self.flags[self.flag])
                        # Pass Current_Move, modified Board, Block, Inc Depth, Alpha, beta
                        _max = self.max_value(i, board, block, depth + 1, alpha, beta)
                        if _max <= value:
                                value = _max

                        if value <= alpha:
                                return value

                        if value <= beta:
                                beta = value

                return value

        ###################### ALPHA-BETA ###############################        
        def alpha_beta_search(self, old_move, temp_board, temp_block, depth):
                alpha = -float('inf')
                beta = float('inf')
                value = self.max_value(old_move, temp_board, temp_block, depth+1, alpha, beta)
                try:
                        #print "Found the Value-Actions Pair"
                        #print self.result
                        #print " -------------------------- "
                        perfect_actions = self.result[str(value)]
                        #print "Valid Moves"
                        #print self.valid_moves
                        #print "Value"
                        #print value
                        #print "Actions"
                        #print self.result[str(value)]
                        #if perfect_actions in self.valid_moves:
                        return perfect_actions[random.randrange(len(perfect_actions))]
                except:
                        print "Something went wrong!"
                        #return random ?

	def move(self, temp_board, temp_block, old_move, flag):

                # Are we 'x' or 'o'
		self.flag = flag
	        self.result = {}
	
                blocks_allowed = self.get_blocks_allowed(old_move, temp_block)
                cells = get_empty_out_of(temp_board, blocks_allowed,temp_block)
               
                if old_move[0] == -1 and old_move[1] == -1:
                        return cells[random.randrange(len(cells))]
                """
                new_cells = []
                corner_cells = []
                for j in blocks_allowed:
                        flag = 0
                        #Iterate over possible blocks and get empty cells
                        id1 = j/3
                        id2 = j%3
                        for _i in range(id1*3, id1*3+3):
                                for _j in range(id2*3, id2*3+3):
                                        if temp_board[_i][_j] == '-':
                                                new_cells.append((_i, _j))
                                        else:
                                                flag = 1
                        if not flag:
                                # Empty
                                # Choose a corner cell
                                for i in new_cells:
                                        if i[0] % 3 == 0 and i[1] % 3 == 0:
                                                return i
                                              #  corner_cells.append(i)        
                                        elif i[0] % 3 == 0 and i[1] in [2, 5, 8]:
                                                return i
                                              # corner_cells.append(i)
                                        elif i[0] in [2,5, 8] and i[1] % 3 == 0:
                                                return i
                                          #      corner_cells.append(i)
                                        elif i[0] in [2,5,8] and i[1] in [2,5,8]:
                                                return i
                                                corner_cells.append(i)
                """
                # *** Alpha-Beta ***
                _move = self.alpha_beta_search(old_move, temp_board, temp_block, 0)
#                while(1):
#                        pass
                # Return decided move
		return _move 
                #cells[random.randrange(len(cells))]

        def get_no_of_blocks(self, block_stat):
                """
                        Get number of blocks finished (max, min)
                """
                max_block = 0
                min_block = 0

                for i in block_stat:
                        if i == '-':
                                continue
                        elif i == 'x':
                                max_block += 1
                        else:
                                min_block += 1

                return max_block, min_block

        def find_values(self, r, temp_block, useful, n, blockage):

                value = 0
                if n == 1:

                        if blockage == 2:
                                value = 1.5
                                return value

                        elif blockage == 1:
                                value = 0.5
                                return value

                        for _k in useful:
                                found1 = 0
                                # Center Element
                                if _k == 4:
                                        value += 1
                                        continue

                                for _j in self.blocked[_k]:
                                        if temp_block[_j] == '-':
                                                # Found Unblocked - Useful 1
                                                # Add Heuristics for more unblocked ?
                                                found1 = 1
                                                break
                                if found1:
                                        # Found with potential
                                        value = 1

                # If it's 2, check for 3rd block to be empty
                if n == 2:
                        # row as set
                        srow = set(r)
                        # Useful as set
                        suseful = set(useful)
                        missing = list(srow - suseful)[0]
                        if temp_block[missing] == '-':
                                # Only if there's a '-' 
                                # it makes sense for two in a row
                                value += 1

                if n == 3:
                        value += 1
 
                return value

        def get_n_in_a_row_blocks(self, temp_block, n):
                """
                        Number of 2 in a row blocks
                """
                max = 0
                min = 0
                # Check for horizontal rows
                for i in xrange(0, 9, 3):
                        temp1 = 0
                        temp2 = 0
                        useful_x = []
                        useful_o = []
                        row = []
                        # X blocks O
                        blockage_o = 0
                        # O blocks X
                        blockage_x = 0
                        for j in xrange(i, i + 3):
                                row.append(j)
                                if temp_block[j] == 'x':
                                        temp1 += 1
                                        blockage_x += 1
                                        useful_x.append(j)
                                elif temp_block[j] == 'o':
                                        temp2 += 1
                                        blockage_o += 1
                                        useful_o.append(j)
                        
                        # For 'X'
                        if temp1 == n:
                                max += self.find_values(row, temp_block, useful_x, n, blockage_o)

                        # For 'O'
                        if temp2 == n:
                                min += self.find_values(row, temp_block, useful_o, n, blockage_x)

                # Check for Vertical
                for i in xrange(3):
                        temp1 = 0
                        temp2 = 0
                        useful_x = []
                        useful_o = []
                        row = []
                        # X blocks O
                        blockage_o = 0
                        # O blocks X
                        blockage_x = 0
                        for j in xrange(i, 9, 3):
                                row.append(j)
                                if temp_block[j] == 'x':
                                        temp1 += 1
                                        blockage_x += 1
                                        useful_x.append(j)
                                elif temp_block[j] == 'o':
                                        temp2 += 1
                                        blockage_o += 1
                                        useful_o.append(j)

                        if temp1 == n:
                                max += self.find_values(row, temp_block, useful_x, n, blockage_o)
                        if temp2 == n:
                                min += self.find_values(row, temp_block, useful_o, n, blockage_x)

                # Check for diagonals
                # Diagonal 1

                temp1 = 0
                temp2 = 0
                row = [0, 4, 8]
                for i in row:
                        if temp_block[i] == 'x':
                                temp1 += 1
                                blockage_x += 1
                                useful_x.append(i)
                        elif temp_block[i] == 'o':
                                temp2 += 1
                                blockage_o += 1
                                useful_o.append(i)

                if temp1 == n:
                        max += self.find_values(row, temp_block, useful_x, n, blockage_o)
                if temp2 == n:
                        min += self.find_values(row, temp_block, useful_o, n, blockage_x)

                # Diagonal 2

                temp1 = 0
                temp2 = 0
                row = [2, 4, 6]
                for i in row:
                        if temp_block[i] == 'x':
                                temp1 += 1
                                blockage_x += 1
                                useful_x.append(i)
                        elif temp_block[i] == 'o':
                                temp2 += 1
                                blockage_o += 1
                                useful_o.append(i)

                if temp1 == n:
                        max += self.find_values(row, temp_block, useful_x, n, blockage_o)
                if temp2 == n:
                        min += self.find_values(row, temp_block, useful_o, n, blockage_x)

                return max, min

        def get_n_in_a_row_cells(self, board, n):
                max = 0
                min = 0
                for i in xrange(9):
                        temp1, temp2 = self.get_n_in_a_row_blocks(board[i], n)
                        max += temp1
                        min += temp2
                return max, min

class Player2:
	
	def __init__(self):
		pass
	def move(self,temp_board,temp_block,old_move,flag):
		for_corner = [0,2,3,5,6,8]

		#List of permitted blocks, based on old move.
		blocks_allowed  = []

		if old_move[0] in for_corner and old_move[1] in for_corner:
			## we will have 3 representative blocks, to choose from

			if old_move[0] % 3 == 0 and old_move[1] % 3 == 0:
				## top left 3 blocks are allowed
				blocks_allowed = [0, 1, 3]
			elif old_move[0] % 3 == 0 and old_move[1] in [2, 5, 8]:
				## top right 3 blocks are allowed
				blocks_allowed = [1,2,5]
			elif old_move[0] in [2,5, 8] and old_move[1] % 3 == 0:
				## bottom left 3 blocks are allowed
				blocks_allowed  = [3,6,7]
			elif old_move[0] in [2,5,8] and old_move[1] in [2,5,8]:
				### bottom right 3 blocks are allowed
				blocks_allowed = [5,7,8]
			else:
				print "SOMETHING REALLY WEIRD HAPPENED!"
				sys.exit(1)
		else:
		#### we will have only 1 block to choose from (or maybe NONE of them, which calls for a free move)
			if old_move[0] % 3 == 0 and old_move[1] in [1,4,7]:
				## upper-center block
				blocks_allowed = [1]
	
			elif old_move[0] in [1,4,7] and old_move[1] % 3 == 0:
				## middle-left block
				blocks_allowed = [3]
		
			elif old_move[0] in [2,5,8] and old_move[1] in [1,4,7]:
				## lower-center block
				blocks_allowed = [7]

			elif old_move[0] in [1,4,7] and old_move[1] in [2,5,8]:
				## middle-right block
				blocks_allowed = [5]
			elif old_move[0] in [1,4,7] and old_move[1] in [1,4,7]:
				blocks_allowed = [4]
                
                for i in reversed(blocks_allowed):
                    if temp_block[i] != '-':
                        blocks_allowed.remove(i)

	# We get all the empty cells in allowed blocks. If they're all full, we get all the empty cells in the entire board.
		cells = get_empty_out_of(temp_board,blocks_allowed,temp_block)
		return cells[random.randrange(len(cells))]

#Initializes the game
def get_init_board_and_blockstatus():
	board = []
	for i in range(9):
		row = ['-']*9
		board.append(row)
	
	block_stat = ['-']*9
	return board, block_stat

# Checks if player has messed with the board. Don't mess with the board that is passed to your move function. 
def verification_fails_board(board_game, temp_board_state):
	return board_game == temp_board_state	

# Checks if player has messed with the block. Don't mess with the block array that is passed to your move function. 
def verification_fails_block(block_stat, temp_block_stat):
	return block_stat == temp_block_stat	

#Gets empty cells from the list of possible blocks. Hence gets valid moves. 
def get_empty_out_of(gameb, blal,block_stat):
	cells = []  # it will be list of tuples
	#Iterate over possible blocks and get empty cells
	for idb in blal:
		id1 = idb/3
		id2 = idb%3
		for i in range(id1*3,id1*3+3):
			for j in range(id2*3,id2*3+3):
				if gameb[i][j] == '-':
					cells.append((i,j))
	
        # If all the possible blocks are full, you can move anywhere
	if cells == []:
		for i in range(9):
			for j in range(9):
                                no = (i/3)*3
                                no += (j/3)
				if gameb[i][j] == '-' and block_stat[no] == '-':
					cells.append((i,j))
	return cells
		
# Note that even if someone has won a block, it is not abandoned. But then, there's no point winning it again!
# Returns True if move is valid
def check_valid_move(game_board,block_stat, current_move, old_move):

	# first we need to check whether current_move is tuple of not
	# old_move is guaranteed to be correct
	if type(current_move) is not tuple:
		return False
	
	if len(current_move) != 2:
		return False

	a = current_move[0]
	b = current_move[1]	

	if type(a) is not int or type(b) is not int:
		return False
	if a < 0 or a > 8 or b < 0 or b > 8:
		return False

	#Special case at start of game, any move is okay!
	if old_move[0] == -1 and old_move[1] == -1:
		return True


	for_corner = [0,2,3,5,6,8]

	#List of permitted blocks, based on old move.
	blocks_allowed  = []

	if old_move[0] in for_corner and old_move[1] in for_corner:
		## we will have 3 representative blocks, to choose from

		if old_move[0] % 3 == 0 and old_move[1] % 3 == 0:
			## top left 3 blocks are allowed
			blocks_allowed = [0,1,3]
		elif old_move[0] % 3 == 0 and old_move[1] in [2,5,8]:
			## top right 3 blocks are allowed
			blocks_allowed = [1,2,5]
		elif old_move[0] in [2,5,8] and old_move[1] % 3 == 0:
			## bottom left 3 blocks are allowed
			blocks_allowed  = [3,6,7]
		elif old_move[0] in [2,5,8] and old_move[1] in [2,5,8]:
			### bottom right 3 blocks are allowed
			blocks_allowed = [5,7,8]

		else:
			print "SOMETHING REALLY WEIRD HAPPENED!"
			sys.exit(1)

	else:
		#### we will have only 1 block to choose from (or maybe NONE of them, which calls for a free move)
		if old_move[0] % 3 == 0 and old_move[1] in [1,4,7]:
			## upper-center block
			blocks_allowed = [1]
	
		elif old_move[0] in [1,4,7] and old_move[1] % 3 == 0:
			## middle-left block
			blocks_allowed = [3]
		
		elif old_move[0] in [2,5,8] and old_move[1] in [1,4,7]:
			## lower-center block
			blocks_allowed = [7]

		elif old_move[0] in [1,4,7] and old_move[1] in [2,5,8]:
			## middle-right block
			blocks_allowed = [5]

		elif old_move[0] in [1,4,7] and old_move[1] in [1,4,7]:
			blocks_allowed = [4]

        #Check if the block is won, or completed. If so you cannot move there. 

        for i in reversed(blocks_allowed):
            if block_stat[i] != '-':
                blocks_allowed.remove(i)
        
        # We get all the empty cells in allowed blocks. If they're all full, we get all the empty cells in the entire board.
        cells = get_empty_out_of(game_board, blocks_allowed,block_stat)

	#Checks if you made a valid move. 
        if current_move in cells:
     	    return True
        else:
    	    return False

def update_lists(game_board, block_stat, move_ret, fl):
	#move_ret has the move to be made, so we modify the game_board, and then check if we need to modify block_stat
	game_board[move_ret[0]][move_ret[1]] = fl

	block_no = (move_ret[0]/3)*3 + move_ret[1]/3
	id1 = block_no/3
	id2 = block_no%3
	mg = 0
	mflg = 0
	if block_stat[block_no] == '-':
		if game_board[id1*3][id2*3] == game_board[id1*3+1][id2*3+1] and game_board[id1*3+1][id2*3+1] == game_board[id1*3+2][id2*3+2] and game_board[id1*3+1][id2*3+1] != '-':
			mflg=1
		if game_board[id1*3+2][id2*3] == game_board[id1*3+1][id2*3+1] and game_board[id1*3+1][id2*3+1] == game_board[id1*3][id2*3 + 2] and game_board[id1*3+1][id2*3+1] != '-':
			mflg=1
		
                if mflg != 1:
                    for i in range(id2*3,id2*3+3):
                        if game_board[id1*3][i]==game_board[id1*3+1][i] and game_board[id1*3+1][i] == game_board[id1*3+2][i] and game_board[id1*3][i] != '-':
                                mflg = 1
                                break

                ### row-wise
		if mflg != 1:
                    for i in range(id1*3,id1*3+3):
                        if game_board[i][id2*3]==game_board[i][id2*3+1] and game_board[i][id2*3+1] == game_board[i][id2*3+2] and game_board[i][id2*3] != '-':
                                mflg = 1
                                break

	
	if mflg == 1:
		block_stat[block_no] = fl
	
        #check for draw on the block.

        id1 = block_no/3
	id2 = block_no%3
        cells = []
	for i in range(id1*3,id1*3+3):
	    for j in range(id2*3,id2*3+3):
		if game_board[i][j] == '-':
		    cells.append((i,j))

        if cells == [] and mflg!=1:
            block_stat[block_no] = 'd' #Draw
        
        return

def terminal_state_reached(game_board, block_stat):
	
        #Check if game is won!
        bs = block_stat
	## Row win
	if (bs[0] == bs[1] and bs[1] == bs[2] and bs[1]!='-' and bs[1]!='d') or (bs[3]!='d' and bs[3]!='-' and bs[3] == bs[4] and bs[4] == bs[5]) or (bs[6]!='d' and bs[6]!='-' and bs[6] == bs[7] and bs[7] == bs[8]):
		return True, 'W'
	## Col win
	elif (bs[0]!='d' and bs[0] == bs[3] and bs[3] == bs[6] and bs[0]!='-') or (bs[1]!='d'and bs[1] == bs[4] and bs[4] == bs[7] and bs[4]!='-') or (bs[2]!='d' and bs[2] == bs[5] and bs[5] == bs[8] and bs[5]!='-'):
		return True, 'W'
	## Diag win
	elif (bs[0] == bs[4] and bs[4] == bs[8] and bs[0]!='-' and bs[0]!='d') or (bs[2] == bs[4] and bs[4] == bs[6] and bs[2]!='-' and bs[2]!='d'):
		return True, 'W'
	else:
		smfl = 0
		for i in range(9):
			for j in range(9):
				if game_board[i][j] == '-' and block_stat[(i/3)*3+(j/3)] == '-':
					smfl = 1
					break
		if smfl == 1:
                        #Game is still on!
			return False, 'Continue'
		
		else:
                        #Changed scoring mechanism
                        # 1. If there is a tie, player with more boxes won, wins.
                        # 2. If no of boxes won is the same, player with more corner move, wins. 
                        point1 = 0
                        point2 = 0
                        for i in block_stat:
                            if i == 'x':
                                point1+=1
                            elif i=='o':
                                point2+=1
			if point1>point2:
				return True, 'P1'
			elif point2>point1:
				return True, 'P2'
			else:
                                point1 = 0
                                point2 = 0
                                for i in range(len(game_board)):
                                    for j in range(len(game_board[i])):
                                        if i%3!=1 and j%3!=1:
                                            if game_board[i][j] == 'x':
                                                point1+=1
                                            elif game_board[i][j]=='o':
                                                point2+=1
			        if point1>point2:
				    return True, 'P1'
			        elif point2>point1:
				    return True, 'P2'
                                else:
				    return True, 'D'	


def decide_winner_and_get_message(player,status, message):
	if player == 'P1' and status == 'L':
		return ('P2',message)
	elif player == 'P1' and status == 'W':
		return ('P1',message)
	elif player == 'P2' and status == 'L':
		return ('P1',message)
	elif player == 'P2' and status == 'W':
		return ('P2',message)
	else:
		return ('NO ONE','DRAW')
	return


def print_lists(gb, bs):
	print '=========== Game Board ==========='
	for i in range(9):
		if i > 0 and i % 3 == 0:
			print
		for j in range(9):
			if j > 0 and j % 3 == 0:
				print " " + gb[i][j],
			else:
				print gb[i][j],

		print
	print "=================================="

	print "=========== Block Status ========="
	for i in range(0, 9, 3):
		print bs[i] + " " + bs[i+1] + " " + bs[i+2] 
	print "=================================="
	print
	

def simulate(obj1,obj2):
	
	# Game board is a 9x9 list, block_stat is a 1D list of 9 elements
	game_board, block_stat = get_init_board_and_blockstatus()

	pl1 = obj1 
	pl2 = obj2

	### basically, player with flag 'x' will start the game
	pl1_fl = 'x'
	pl2_fl = 'o'

	old_move = (-1, -1) # For the first move

	WINNER = ''
	MESSAGE = ''

        #Make your move in 6 seconds!
	TIMEALLOWED = 6

	print_lists(game_board, block_stat)

	while(1):

		# Player1 will move
		
		temp_board_state = game_board[:]
		temp_block_stat = block_stat[:]
	
		signal.signal(signal.SIGALRM, handler)
		signal.alarm(TIMEALLOWED)
		# Player1 to complete in TIMEALLOWED secs. 
		try:
			ret_move_pl1 = pl1.move(temp_board_state, temp_block_stat, old_move, pl1_fl)
		except TimedOutExc as e:
			WINNER, MESSAGE = decide_winner_and_get_message('P1', 'L',   'TIMED OUT')
			break
		signal.alarm(0)
	
                #Checking if list hasn't been modified! Note: Do not make changes in the lists passed in move function!
		if not (verification_fails_board(game_board, temp_board_state) and verification_fails_block(block_stat, temp_block_stat)):
			#Player1 loses - he modified something
			WINNER, MESSAGE = decide_winner_and_get_message('P1', 'L',   'MODIFIED CONTENTS OF LISTS')
			break
		
		# Check if the move made is valid
		if not check_valid_move(game_board, block_stat,ret_move_pl1, old_move):
			## player1 loses - he made the wrong move.
			WINNER, MESSAGE = decide_winner_and_get_message('P1', 'L',   'MADE AN INVALID MOVE')
			break


		print "Player 1 made the move:", ret_move_pl1, 'with', pl1_fl

                #So if the move is valid, we update the 'game_board' and 'block_stat' lists with move of pl1
                update_lists(game_board, block_stat, ret_move_pl1, pl1_fl)

		# Checking if the last move resulted in a terminal state
		gamestatus, mesg =  terminal_state_reached(game_board, block_stat)
		if gamestatus == True:
			print_lists(game_board, block_stat)
			WINNER, MESSAGE = decide_winner_and_get_message('P1', mesg,  'COMPLETE')	
			break

		
		old_move = ret_move_pl1
		print_lists(game_board, block_stat)

                # Now player2 plays

                temp_board_state = game_board[:]
                temp_block_stat = block_stat[:]


		signal.signal(signal.SIGALRM, handler)
		signal.alarm(TIMEALLOWED)
		try:
                	ret_move_pl2 = pl2.move(temp_board_state, temp_block_stat, old_move, pl2_fl)
		except TimedOutExc as e:
			WINNER, MESSAGE = decide_winner_and_get_message('P2', 'L',   'TIMED OUT')
			break
		signal.alarm(0)

                if not (verification_fails_board(game_board, temp_board_state) and verification_fails_block(block_stat, temp_block_stat)):
			WINNER, MESSAGE = decide_winner_and_get_message('P2', 'L',   'MODIFIED CONTENTS OF LISTS')
			break
			
                if not check_valid_move(game_board, block_stat,ret_move_pl2, old_move):
			WINNER, MESSAGE = decide_winner_and_get_message('P2', 'L',   'MADE AN INVALID MOVE')
			break


		print "Player 2 made the move:", ret_move_pl2, 'with', pl2_fl
                
                update_lists(game_board, block_stat, ret_move_pl2, pl2_fl)

		gamestatus, mesg =  terminal_state_reached(game_board, block_stat)
                if gamestatus == True:
			print_lists(game_board, block_stat)
                        WINNER, MESSAGE = decide_winner_and_get_message('P2', mesg,  'COMPLETE' )
                        break
		old_move = ret_move_pl2
		print_lists(game_board, block_stat)
	
	print WINNER + " won!"
	print MESSAGE

if __name__ == '__main__':
	## get game playing objects

	if len(sys.argv) != 2:
		print 'Usage: python simulator.py <option>'
		print '<option> can be 1 => Random player vs. Random player'
		print '                2 => Human vs. Random Player'
		print '                3 => Human vs. Human'
		sys.exit(1)
 
	obj1 = ''
	obj2 = ''
	option = sys.argv[1]	
	if option == '1':
		obj1 = Player30()
	        obj2 = Player30()

	elif option == '2':
		obj1 = Player30()
		obj2 = Manual_player()

	elif option == '3':
		obj1 = Manual_player()
		obj2 = Manual_player()
        
        # Deciding player1 / player2 after a coin toss
        # However, in the tournament, each player will get a chance to go 1st. 
        num = random.uniform(0,1)
        if num > 0.5:
	        simulate(obj2, obj1)
                print "Player30 is P2"
	else:
        	simulate(obj1, obj2)
                print "Player30 is P1"        
