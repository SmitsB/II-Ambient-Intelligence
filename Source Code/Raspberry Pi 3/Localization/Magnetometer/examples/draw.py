from matplotlib import pyplot
import pylab
from mpl_toolkits.mplot3d import Axes3D
import random

# prepare data
test = [[0, 78, 0, 57, 81, 0],[0, 75, 0, 56, 71, 0],[0, 72, 0, 46, 89, 0]]

fig = pylab.figure()
ax = Axes3D(fig)

for x in range(len(test)):
    ax.scatter(test[x][1], test[x][3], test[x][4])
pyplot.show()