import numpy as np
import matplotlib.pyplot as plt
import sys


if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <molecule>")
    sys.exit(1)

xtb_file = f"{sys.argv[1]}_xtb/{sys.argv[1]}_xtb.dat"
oniom_file = f"{sys.argv[1]}_oniom/{sys.argv[1]}_oniom.dat"

# ==========================================
# 1. DATA LOADING
# ==========================================

# Load continuous spectrum (xtb)
# np.loadtxt automatically skips rows starting with '#'
xtb_data = np.loadtxt(xtb_file)
xtb_wavenumber = xtb_data[:, 0]
xtb_intensity = xtb_data[:, 1]

# Load continuous spectrum (ONIOM)
# np.loadtxt automatically skips rows starting with '#'
oniom_data = np.loadtxt(oniom_file)
oniom_wavenumber = oniom_data[:, 0]
oniom_intensity = oniom_data[:, 1]

# ==========================================
# 2. PLOT CREATION (Dual Y-Axis)
# ==========================================

fig, ax1 = plt.subplots(figsize=(10, 6))

# --- Left Y-Axis: Continuous xtb Spectrum ---
color_xtb = '#1f77b4'  # Blue
color_oniom = '#ff7f0e'  # Orange
ax1.set_xlabel(r'Wavenumber ($\mathdefault{cm^{-1}}$)', fontsize=12, fontweight='bold')
ax1.set_ylabel(r'Intensity (a.u.)', fontsize=12, fontweight='bold')
ax1.plot(xtb_wavenumber, xtb_intensity, color=color_xtb, label='xTB Spectrum', linewidth=1.5)
ax1.plot(oniom_wavenumber, oniom_intensity, color=color_oniom, label='ONIOM Spectrum', linewidth=1.5)
ax1.tick_params(axis='y', labelcolor=color_xtb)
ax1.grid(True, linestyle='--', alpha=0.5)

# --- Optional: Gaussian Broadening (Convolution) ---
# Un-comment the section below if you want to apply a broadening effect to ORCA sticks
"""
def gaussian_broadening(x, x0, intensities, fwhm=20):
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    y = np.zeros_like(x)
    for xi, yi in zip(x0, intensities):
        y += yi * np.exp(-((x - xi)**2) / (2 * sigma**2))
    return y

orca_convoluted = gaussian_broadening(xtb_wavenumber, orca_wavenumber, orca_intensity, fwhm=30)
ax2.plot(xtb_wavenumber, orca_convoluted, color=color_orca, linestyle=':', alpha=0.7, label='ORCA Convoluted (FWHM=30)')
"""

# --- Final Adjustments ---
# Combine legends from both axes
lines1, labels1 = ax1.get_legend_handles_labels()
ax1.legend(lines1, labels1, loc='best', frameon=True)

# Define X-axis limits (e.g., full IR range 0 to 4000 cm^-1)
# Adjust these values to zoom in on specific regions (e.g., 1200 to 1800 for C=O stretch)
ax1.set_xlim(0, 4000) 

plt.title('Vibrational Spectrum Comparison: xTB vs. ONIOM', fontsize=14, fontweight='bold', pad=15)
fig.tight_layout()

# Save the plot in high resolution
plt.savefig('oniom_xtb.png', dpi=300)
print("Plot successfully saved as 'oniom_xtb.png'!")
plt.show()
