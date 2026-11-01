import numpy as np
import sys
import matplotlib.pyplot as plt

# Load data [x, y, z, psi]
data = np.loadtxt(sys.argv[1])
output_file = "./img3D/" + sys.argv[1].replace('.dat', '.png')

# --- DATA FILTERING ---
# Calculate density and find the threshold
prob_density = data[:, 3]**2
threshold = 0.05 * np.max(prob_density) # Adjust 0.05 to change orbital "size"

# Apply filter
mask = prob_density > threshold
f_data = data[mask]
# ----------------------

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot only the high-probability points
# We use the original psi for color to keep the red/blue phase information
limit = np.max(np.abs(f_data[:, 3]))
scatter = ax.scatter(f_data[:, 0], f_data[:, 1], f_data[:, 2], 
                     c=f_data[:, 3], cmap='RdBu_r', 
                     vmin=-limit, vmax=limit,
                     s=10, alpha=0.6)

ax.set_title(f'Orbital Isosurface (Threshold: {threshold:.2e})')
ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')

# Ensure the view is a perfect cube
max_dim = np.max(np.abs(data[:, :3]))
ax.set_xlim(-max_dim, max_dim)
ax.set_ylim(-max_dim, max_dim)
ax.set_zlim(-max_dim, max_dim)

# plt.colorbar(scatter, label=r'Phase $\psi$')
plt.savefig(output_file)