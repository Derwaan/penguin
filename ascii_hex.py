"""
Class used to create the ASCII hexagonal board.
"""
class Hex:

    def __init__(self, nb_cols, fst_col_size):
        self.nb_cols = nb_cols
        self.fst_col_size = fst_col_size
        dim = self.get_size(nb_cols, fst_col_size)
        self.M = self.create_matrix(dim)

    def get_size(self, nb_cols, fst_col_size):
        dim = (4 * fst_col_size + 1, 2 + 7 * nb_cols)
        return dim

    def create_matrix(self, dim):
        return [ [ ' ' for j in range(dim[1]) ] for i in range(dim[0]) ] 

    def draw_hexagon(self, i, j):
        pos = self.get_hex_top_left(i, j)
        for k in range(5):
            self.M[pos[0]][pos[1] + 2 + k] = '_'
            self.M[pos[0] + 4][pos[1] + 2 + k] = '_'
        self.M[pos[0] + 1][pos[1] + 1] = '/'
        self.M[pos[0] + 1][pos[1] + 7] = '\\'
        self.M[pos[0] + 2][pos[1]] = '/'
        self.M[pos[0] + 2][pos[1] + 8] = '\\'
        self.M[pos[0] + 3][pos[1]] = '\\'
        self.M[pos[0] + 3][pos[1] + 8] = '/'
        self.M[pos[0] + 4][pos[1] + 1] = '\\'
        self.M[pos[0] + 4][pos[1] + 7] = '/'

    def draw_str(self, i, j, s):
        pos = self.get_hex_top_left(i, j)
        ii = pos[0] + 2
        jj = pos[1] + 2
        k = 0
        for i in range(2):
            for j in range(5):
                if k < len(s):
                    self.M[pos[0] + 2 + i][pos[1] + 2 + j] = s[k]
                    k += 1

    def get_hex_top_left(self, i, j):
        return (4 * i + 2 * (j % 2), 7 * j)


    def __str__(self):
        s = ''
        for i in range(len(self.M)):
            for j in range(len(self.M[i])):
                s += self.M[i][j]
            if i < len(self.M) - 1:
                s += '\n'
        return s