import numpy as np
import re
import sys
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.animation as animation

# extensions (?)
# from optparse import OptionParser

"""
Global parameters

The plan is to have these as command line arguments. But for now this will do.
"""

dimen_x = 128
dimen_y = 128
maxiter = 11000
# if animating, keep in mind rendering takes a long time. Try a neighborhood of maxiter = ~100 at first.
animate = False
num_ants = 1
face_direction = 0
rule = 'rl'
xpos = int(dimen_x/2)
ypos = int(dimen_y/2)
nstates = len(rule)

geometries = ['finite', 'toroid', 'kleinbottlex', 'kleinbottley']
geometry = geometries[2]

def checkrule(string, search=re.compile(r'[^lnru]').search):

    return not bool(search(string))



def main(argv):

    # parse command-line arguments, but not quite yet.
    # parser = OptionParser()
    # parser.add_option("-r", "--rule", dest="rule",
    #                  help="Turning rule. Must be a string containing 'l', 'r', 'n', and 'u' only",
    #                  default='lr')
    # (options, args) = parser.parse_args()

    if not checkrule(rule):
        sys.exit('Invalid rule. Exiting.')

    # create grid
    grid = Grid(dimen_x, dimen_y, geometry)
    # create ants
    ants = []
    for i in range(num_ants):
        ants.append(Ant(face_direction, xpos, ypos, rule, nstates))

    fig = plt.figure()
    ax = plt.axes()
    ax.set_axis_off()

    if animate:
        video = animation.FuncAnimation(fig, update, frames=maxiter, fargs=(grid, ants, ax, animate, maxiter),
                                        init_func=None, blit=True)
        video.save(rule+'-'+str(num_ants)+'ants'+'-'+str(maxiter)+'steps-' +
                   grid.geometry +'.gif', writer='imagemagick', fps=30)
    if not animate:
        for i in np.arange(maxiter):
            # loop over ants (in case there's more than one)
            grid, ants = update(i, grid, ants, ax, animate, maxiter)


def update(i, grid, ants, ax, animate, maxiter):

    for ant in ants:
        try:
            grid.board = ant.move(grid.board)
        except:
            # general error handling: just quit, write debug msg
            grid.final_plot(ants, i, ax)
            sys.exit("Something weird is going on")

        # check geometry to make sure we didn't fall off a cliff, quit if we did
        # for other topologies, apply boundary conditions
        if not grid.check_geometry(ant):
            # end the simulation if the ant hits the wall
            grid.final_plot(ants, i, ax)
            plt.savefig(rule+'-'+str(num_ants)+'ants'+'-'+str(i+1)+'steps'+'.png')
            plt.show()
            sys.exit("Ant fell off the map at timestep = %d!" % i)

    if animate:
        return grid.final_plot(ants, i, ax)
    if not animate:
        if i == maxiter - 1:
            grid.final_plot(ants, i, ax)
            plt.savefig(rule + '-' + str(num_ants) + 'ants-' + str(i + 1) + 'steps-' + grid.geometry + '.png')
            plt.show()
        return grid, ants

class Grid:

    """
    Create arrays as numpy arrays since indexing will be a little faster,
    and the total number of iterations may be extremely large
    """

    def __init__(self, dimen_x, dimen_y, geometry):

        self.dimen = (dimen_y, dimen_x)
        self.geometry = geometry
        self.board = np.zeros((self.dimen[0], self.dimen[1]), dtype=np.int)

    def final_plot(self, ants, step, ax):

        # plot the board state and ants
        # use a mask to make the ant array transparent and overlay only
        # the ants' positions onto the final result
        y = np.zeros((self.dimen[0], self.dimen[1]))
        for ant in ants:
            y[ant.position[0], ant.position[1]] = 1
        y = np.ma.masked_where(y == 0, y)

        # use imshow to print matrix elements using gray colormap. Ants are red.
        ax.imshow(self.board, cmap=plt.get_cmap('gray_r'), interpolation='none')
        image = ax.imshow(y, cmap=mpl.cm.jet_r, interpolation='none')
        return [image]

    def check_geometry(self, ant):

        # return true if in valid geometry, false if ant has fallen off the map
        # also, for non-finite, but bounded geometries, adjust ant position
        check = True
        if self.geometry == 'finite' and (ant.position[0] < 0 or ant.position[0] >= self.dimen[0] or
                                          ant.position[1] < 0 or ant.position[1] >= self.dimen[1]):
            check = False
        if self.geometry == 'toroid' and (ant.position[0] < 0 or ant.position[0] >= self.dimen[0] or
                                          ant.position[1] < 0 or ant.position[1] >= self.dimen[1]):
            ant.position[0] = ant.position[0] % self.dimen[0]
            ant.position[1] = ant.position[1] % self.dimen[1]
        elif self.geometry == 'kleinbottlex' and (ant.position[0] < 0 or ant.position[0] >= self.dimen[0]):
            ant.position[0] = ant.position[0] % self.dimen[0]
        elif self.geometry == 'kleinbottlex' and (ant.position[1] < 0 or ant.position[1] >= self.dimen[1]):
            ant.position[0] = self.dimen[0] - 1 - (ant.position[0] % self.dimen[0])
            ant.position[1] = ant.position[1] % self.dimen[1]
        elif self.geometry == 'kleinbottley' and (ant.position[0] < 0 or ant.position[0] >= self.dimen[0]):
            ant.position[0] = ant.position[0] % self.dimen[0]
            ant.position[1] = self.dimen[1] - 1 - (ant.position[1] % self.dimen[1])
        elif self.geometry == 'kleinbottley' and (ant.position[1] < 0 or ant.position[1] >= self.dimen[1]):
            ant.position[1] = ant.position[1] % self.dimen[1]

        return check

class Ant:

    """
    Facing Direction:

         Up              [0,-1]  1
    Left    Right  2 [-1,0]  [1,0]  0
        Down          3  [0,1]

    dirs = [[1,0],[0,-1],[-1,0],[0,1]]
    index of dirs is the face_direction
    Right turn applies cyclic shift in negative direction
    Left turn applies cyclic shift in positive direction
    """

    def __init__(self, face_direction, xpos, ypos, rule, nstates):

        self.face_direction = face_direction
        self.position = [ypos, xpos]
        self.rule = rule
        self.nstates = nstates
        self.possiblefacings = ((1, 0), (0, -1), (-1, 0), (0, 1))
        self.geometry = geometry

    def move(self, board):

        # get state of board and current direction
        state = board[self.position[0], self.position[1]]
        directive = self.rule[state]

        # change the ant's direction
        self.face_direction = self.cycle_dir(directive)

        # cyclically increment the state of the board
        board[self.position[0], self.position[1]] = (state + 1) % self.nstates

        # apply motion based on new direction
        self.position[0] = self.position[0] + self.possiblefacings[self.face_direction][0]
        self.position[1] = self.position[1] + self.possiblefacings[self.face_direction][1]

        return board

    def cycle_dir(self, directive):

        new_face_direction = None
        # perform a cyclic permutation on the possible facing
        # directions with respect to the movement directive
        if directive == 'r':
            new_face_direction = (self.face_direction - 1) % len(self.possiblefacings)
        elif directive == 'l':
            new_face_direction = (self.face_direction + 1) % len(self.possiblefacings)
        elif directive == 'u':
            new_face_direction = (self.face_direction + 2) % len(self.possiblefacings)
        elif directive == 'n':
            new_face_direction = self.face_direction

        return new_face_direction


#pretend there's command-line arguments for now
if __name__ == "__main__":
    main(sys.argv[1:])
