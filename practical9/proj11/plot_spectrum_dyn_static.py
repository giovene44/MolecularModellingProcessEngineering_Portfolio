import numpy as np
import matplotlib.pyplot as plt
import sys


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <file.dat> <file.vibspectrum>")
    sys.exit(1)

qct_file = sys.argv[1]
orca_file = sys.argv[2]

# ==========================================
# 1. DATA LOADING
# ==========================================

# Load continuous spectrum (QCT)
# np.loadtxt automatically skips rows starting with '#'
qct_data = np.loadtxt(qct_file)
qct_wavenumber = qct_data[:, 0]
qct_intensity = qct_data[:, 1]

# Load stick spectrum (ORCA)
orca_wavenumber = []
orca_intensity = []

with open(orca_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        # Skip empty lines or headers
        if not line or line.startswith('#') or line.startswith('$'):
            continue
        parts = line.split()
        if len(parts) >= 4:
            try:
                # Read from the end to avoid issues if the symmetry column is missing
                wn = float(parts[-3])
                intensity = float(parts[-2])
                
                # Consider only real, positive frequencies (> 10 cm^-1)
                # to exclude translations/rotations located at ~0 cm^-1
                if wn > 10:
                    orca_wavenumber.append(wn)
                    orca_intensity.append(intensity)
            except ValueError:
                continue

orca_wavenumber = np.array(orca_wavenumber)
orca_intensity = np.array(orca_intensity) / np.max(orca_intensity)

# ==========================================
# 2. PLOT CREATION (Dual Y-Axis)
# ==========================================

fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot QCT (Continuous) on ax1
ax1.plot(qct_wavenumber, qct_intensity, color='blue', label='QCT Spectrum')

# Plot ORCA (Sticks) on ax1 as well!
color_orca = 'red' # Or whatever color you defined
ax1.vlines(orca_wavenumber, 0, orca_intensity, color=color_orca, label='Normal Modes (ORCA)', linewidth=1.8)

# Set common labels
ax1.set_xlabel(r'Wavenumber ($\mathdefault{cm^{-1}}$)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Normalized Intensity', fontsize=12, fontweight='bold')

# (Optional) If you have the Gaussian Broadening section uncommented, 
# make sure to change ax2.plot to ax1.plot there as well!

# --- Optional: Gaussian Broadening (Convolution) ---
# Un-comment the section below if you want to apply a broadening effect to ORCA sticks
"""
def gaussian_broadening(x, x0, intensities, fwhm=20):
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    y = np.zeros_like(x)
    for xi, yi in zip(x0, intensities):
        y += yi * np.exp(-((x - xi)**2) / (2 * sigma**2))
    return y

orca_convoluted = gaussian_broadening(qct_wavenumber, orca_wavenumber, orca_intensity, fwhm=30)
ax2.plot(qct_wavenumber, orca_convoluted, color=color_orca, linestyle=':', alpha=0.7, label='ORCA Convoluted (FWHM=30)')
"""

# --- Final Adjustments ---
# Combine legends from both axes
ax1.legend(loc='best', fontsize=10)

# Define X-axis limits (e.g., full IR range 0 to 4000 cm^-1)
# Adjust these values to zoom in on specific regions (e.g., 1200 to 1800 for C=O stretch)
ax1.set_xlim(0, 4000) 

plt.title('Vibrational Spectrum Comparison: QCT vs. ORCA', fontsize=14, fontweight='bold', pad=15)
fig.tight_layout()

# Save the plot in high resolution
plt.savefig('vibrational_spectrum_comparison.png', dpi=300)
print("Plot successfully saved as 'vibrational_spectrum_comparison.png'!")
plt.show()
