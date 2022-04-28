import math
import random
import numpy as np
import matplotlib.pyplot as plt

data = [
    ((0,0), 0.84),
    ((0,1), 0.86),
    ((0,2), 0.89),
    ((0,3), 0.921),
    ((1,0), 0.801),
    ((1,1), 0.796),
    ((1,2), 0.854),
    ((1,3), 0.92),
    ((2,0), 0.87),
    ((2,1), 0.567),
    ((2,2), 0.76),
    ((2,3), 0.87)
]

data = [((0, 0), 0.8571428571428571), ((0, 1), 0.8392857142857143), ((0, 2), 0.9285714285714286), ((0, 3), 0.8928571428571429), ((0, 4), 0.9107142857142857), ((0, 5), 0.9285714285714286), ((1, 0), 0.875), ((1, 1), 0.8571428571428571), ((1, 2), 0.8928571428571429), ((1, 3), 0.8928571428571429), ((1, 4), 0.9285714285714286), ((1, 5), 0.9464285714285714), ((2, 0), 0.8035714285714286), ((2, 1), 0.8392857142857143), ((2, 2), 0.8928571428571429), ((2, 3), 0.875), ((2, 4), 0.8928571428571429), ((2, 5), 0.9285714285714286)]
# actual data lol

# too lazy to actually generate it lol

def main():

    ## handling the data first
    shape = (data[-1][0][0] + 1, data[-1][0][1] + 1)

    # oh my god this code is so goddamn terrible. 
    # it works though.
    y_array = np.zeros(shape=shape)
    for a in data:
        y_array[a[0][0]][a[0][1]] = a[1]

    increasing = np.arange(0, shape[1])
    # x_array = np.tile(increasing, (shape[0], 1)) # dont need this shit
    x_array = increasing

    # fig, (ax1, ax2) = plt.subplots(1, 2)

    fig=plt.figure(figsize=(10,5))

    fig.suptitle("Model Accuracy Plots") 
    ax1=fig.add_subplot(121)

    ax = ax1
    ax.set_title("Image Sizes")
    ax.set_xlabel("Iterations") 
    ax.set_ylabel("Accuracy") 
    for y in y_array:
        ax.plot(x_array, y)


    y = np.arange(0, shape[0])
    x = np.arange(0, shape[1])
    # z = y_array
    # print(x, y, z)

    ax = fig.add_subplot(122, projection='3d')
    
    colors = ['r', 'g', 'b', 'y']
    i = 0
    for a in y_array:
        print(a)
        print(a.shape)

        # You can provide either a single color or an array with the same length as
        # xs and ys. To demonstrate this, we color the first bar of each set cyan.
        # cs = [c] * len(xs)
        # cs[0] = 'c'

        # Plot the bar graph given by xs and ys on the plane y=k with 80% opacity.
        ax.plot(x, a, zs=i, zdir='y', alpha=0.8)
        i += 1

    ax.set_xlabel('Fine Tune')
    ax.set_ylabel('Model Run')
    ax.set_zlabel('Iterations')

    # On the y axis let's only label the discrete values that we have data for.
    ax.set_yticks(y)

    fig.show()
    


    

    print("\n")
    input()

if __name__ == "__main__":
    main()