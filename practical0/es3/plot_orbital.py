import numpy as np
import sys
import matplotlib.pyplot as plt

# Load the data from the file
data = np.loadtxt(sys.argv[1])
output_file = "./img2D/" + sys.argv[1].replace('.dat', '.png')

x = data[:, 0]
y = data[:, 1]
z = data[:, 2]

x_unique = np.unique(x)
y_unique = np.unique(y)

X, Y = np.meshgrid(x_unique, y_unique)
Z = z.reshape(len(x_unique), len(y_unique)).T
Z *= np.abs(Z)>1e-10 

plt.figure(figsize=(8, 6))
plt.contourf(X, Y, Z, cmap='viridis', levels=20)
plt.colorbar(label='Intensity')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.title('2D Contour Plot of Orbital Data')

plt.savefig(output_file)
