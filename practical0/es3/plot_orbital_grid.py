import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def load_and_reshape(filename):
    # Load data: Column 0 is X, Column 1 is Y, Column 2 is Value
    data = np.loadtxt(filename)
    x = data[:, 0]
    y = data[:, 1]
    z = data[:, 2]
    z *= np.abs(z)>1e-10  # Set very small values to zero for better visualization
    # Determine the grid dimensions
    # We find how many unique points exist for x and y
    num_x = len(np.unique(x))
    num_y = len(np.unique(y))
    
    # Reshape z into a (num_x, num_y) grid
    # Note: order='C' or 'F' depends on how your data was saved
    return z.reshape((num_x, num_y)), (x.min(), x.max(), y.min(), y.max())

# Load and process each orbital
files = ["orbital1_0_0.dat", "orbital2_0_0.dat", "orbital2_1_0.dat", 
         "orbital2_1_1.dat", "orbital2_1_-1.dat"]
labels = [r'$1s$', r'$2s$', r'$2p_z$', r'$2p_x$', r'$2p_y$']

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('Hydrogen Orbitals (Reshaped Grid)', fontsize=18)

for idx, (ax, file, label) in enumerate(zip(axes.flat, files, labels)):
    try:
        grid_z, extent = load_and_reshape(file)
        
        # extent=[xmin, xmax, ymin, ymax] maps the pixels to actual coordinates
        im = ax.imshow(grid_z.T, cmap='RdBu_r', origin='lower', extent=extent)
        
        ax.set_title(label, fontsize=14)
        ax.set_xlabel('x (a₀)')
        ax.set_ylabel('y (a₀)')
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        
    except Exception as e:
        print(f"Skipping {file}: {e}")
        ax.axis('off')

# Hide the last empty plot
axes[1, 2].axis('off')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig("./img2D/orbital_grid.png", dpi=150)