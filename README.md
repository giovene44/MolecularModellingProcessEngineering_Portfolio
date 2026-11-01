# Molecular Modeling in Process Engineering - Portfolio

This repository contains the computational projects, source code, data analysis, and technical reports developed for the **Molecular Modeling in Process Engineering** course (A.Y. 2025-2026) as part of the MSc in High Performance Computing Engineering at Politecnico di Milano.

The repository serves as a portfolio demonstrating the application of advanced quantum chemistry software, statistical mechanics, and custom programming (C++, Python) to solve complex physical chemistry and kinetic problems.

## 🛠️ Technologies & Tools
* **Programming Languages:** Python (Data Analysis, Matplotlib), C++ (Numerical evaluation of analytical wavefunctions), Bash/PowerShell.
* **Quantum Chemistry Software:** Gaussian 16, Molpro, ORCA, xTB.
* **Key Methods:** DFT (B3LYP, M06-2X, wB97X-D), Ab-initio (HF, MP2, CCSD(T)), Multi-reference (CASSCF, CASPT2), BOMD (Molecular Dynamics).

## 📂 Repository Structure

* **`Report/`**: Contains the comprehensive final project report (`Giorgio_Venezia_10807335_Report_MolModProcEng.pdf`) detailing the theoretical background, methodologies, and results for all assignments.
* **`practical0/ - practical8/`**: Individual directories containing:
  * Input files (`.com`, `.inp`, `.xyz`, `.gzmat`)
  * Extracted data and thermodynamic calculations (`.csv`, `.xlsx`)
  * Custom scripts (`.py`, `.cpp`, `.sh`)
  * Generated plots and visualizations (`.png`)

## 🚀 Key Projects & Implementations

* **Atomic Orbital Visualization (C++ / Python):** Developed a standalone C++ application paired with a Python post-processing script to numerically evaluate and plot 2D and 3D isosurfaces of hydrogenic atomic orbitals using Associated Laguerre and Legendre polynomials.
* **Thermodynamics & Partition Functions:** Computed rotational, vibrational, translational, and electronic partition functions from electronic structure calculations to determine heat capacities, entropies, and equilibrium constants.
* **Basis Set Limits & Electron Correlation:** Evaluated the impact of basis set size (Pople vs. Dunning cc-pVXZ) and level of theory (HF, DFT, MP2, CCSD(T)) on the accuracy of bond dissociation energies.
* **Chemical Kinetics & Transition State Theory (TST):** Calculated rate constants for bimolecular abstraction and unimolecular isomerization reactions. Applied Wigner and Eckart quantum tunneling corrections to map Arrhenius plot deviations at low temperatures.
* **First-Principles NMR Spectroscopy:** Estimated $^1$H NMR chemical shifts and J-couplings using the Gauge-Including Atomic Orbital (GIAO) method, directly comparing simulated continuous wave spectra with experimental data.
* **Minimum Energy Path (MEP):** Modeled the homolytic cleavage of methane utilizing multi-reference methods (CASSCF/CASPT2) to accurately capture the dissociation asymptote, overcoming standard HF limitations.
* **Anharmonic Vibrational Spectroscopy (BOMD):** Performed Born-Oppenheimer Molecular Dynamics (BOMD) on $(H_2O)_{11}$ clusters using semi-empirical xTB to extract anharmonic vibrational spectra via Velocity Autocorrelation Functions (VACF) and Fourier Transforms.

## 👤 Author
**Giorgio Venezia**
* [LinkedIn](https://www.linkedin.com/in/giorgio-venezia-616053356/)
* [GitHub](https://github.com/giovene44)