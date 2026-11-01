import numpy as np
import matplotlib.pyplot as plt
import sys

def load_and_filter(filename):
    # Load data: Column 0 is X, Column 1 is Y, Column 2 is Z, Column 3 is psi
    data = np.loadtxt(filename)
    
    # --- DATA FILTERING ---
    prob_density = data[:, 3]**2
    threshold = 0.05 * np.max(prob_density)  # Adjust 0.05 to change orbital "size"
    
    # Apply filter
    mask = prob_density > threshold
    f_data = data[mask]
    # ----------------------
    
    return f_data

# Load and process each orbital
files = ["orbital3D1_0_0.dat", "orbital3D2_0_0.dat", "orbital3D2_1_0.dat", 
         "orbital3D2_1_1.dat", "orbital3D2_1_-1.dat"]
labels = [r'$1s$', r'$2s$', r'$2p_z$', r'$2p_x$', r'$2p_y$']

fig = plt.figure(figsize=(18, 12))
fig.suptitle('Hydrogen Orbitals (3D)', fontsize=18)

for idx, (file, label) in enumerate(zip(files, labels)):
    try:
        f_data = load_and_filter(file)
        
        ax = fig.add_subplot(2, 3, idx + 1, projection='3d')
        
        # Plot only the high-probability points
        limit = np.max(np.abs(f_data[:, 3]))
        scatter = ax.scatter(f_data[:, 0], f_data[:, 1], f_data[:, 2], 
                             c=f_data[:, 3], cmap='RdBu_r', 
                             vmin=-limit, vmax=limit,
                             s=10, alpha=0.6)

        ax.set_title(label, fontsize=14)
        ax.set_xlabel('x (a₀)')
        ax.set_ylabel('y (a₀)')
        ax.set_zlabel('z (a₀)')
        # plt.colorbar(scatter, label=r'Phase $\psi$', ax=ax)
        
    except Exception as e:
        print(f"Skipping {file}: {e}")

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig("./img3D/orbital_3d_grid.png", dpi=150)