#!/usr/bin/python3
import sys
import os
import csv
import re

def extract_gaussian_data(log_file):
    """
    Extracts fundamental parameters needed for TST rate constants:
    electronic degeneracy, ZPE correction, mass, symmetry numbers, pressure,
    individual moments of inertia, rotational temperatures, and vibrational frequencies.
    """
    data = {
        "Elec_Degeneracy": None,
        "ZPE_Correction_Ha": None,
        "Mass_amu": None,
        "Symmetry_Number": None,
        "Pressure_Atm": None,
        "moments_of_inertia": [],
        "rot_temps": [],
        "vib_freqs": []
    }
    
    if not os.path.exists(log_file):
        print(f"Warning: Gaussian file '{log_file}' not found.")
        return data

    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    capture_moi = False
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Keep frequency and rotational lists dynamically updated to the final converged step
        if "harmonic frequencies (cm**-1)" in line_lower:
            data["vib_freqs"] = []
        if "- thermochemistry -" in line_lower:
            data["rot_temps"] = []
            
        # 1. Electronic Degeneracy extraction (Multiplicity = Degeneracy)
        if "charge =" in line_lower and "multiplicity =" in line_lower:
            clean_line = line.replace("Charge", "").replace("Multiplicity", "").replace("=", "")
            try:
                data["Elec_Degeneracy"] = int(clean_line.split()[1])
            except (ValueError, IndexError):
                pass

        # 2. Zero-Point Energy Correction
        elif "zero-point correction=" in line_lower:
            try:
                data["ZPE_Correction_Ha"] = float(line.split()[2])
            except (ValueError, IndexError):
                pass
            
        # 3. Molecular mass and Symmetry Number
        elif "molecular mass:" in line_lower:
            try:
                data["Mass_amu"] = float(line.split()[2])
            except (ValueError, IndexError):
                pass
        elif "rotational symmetry number" in line_lower:
            match = re.search(r"number\s+(\d+)", line_lower)
            if match:
                data["Symmetry_Number"] = float(match.group(1))
                
        # 4. Pressure extraction
        elif "temperature " in line_lower and "pressure " in line_lower:
            parts = line.split()
            try:
                p_idx = [idx for idx, p in enumerate(parts) if "pressure" in p.lower()][0]
                data["Pressure_Atm"] = float(parts[p_idx+1])
            except (ValueError, IndexError):
                pass
                
        # 5. Robust Moments of Inertia extraction (captured as separate list items)
        elif "principal axes and moments of inertia in atomic units:" in line_lower:
            capture_moi = True
        elif capture_moi and "eigenvalues --" in line_lower:
            parts = line.split()
            try:
                idx = parts.index("--")
                eigenvalues_au = parts[idx+1:]
            except ValueError:
                eigenvalues_au = parts[2:]
            
            moi_A2 = []
            for val in eigenvalues_au:
                try:
                    # Convert from amu*bohr^2 to amu*Angstrom^2
                    converted = float(val) / 3.57106418
                    moi_A2.append(f"{converted:.5f}")
                except ValueError:
                    pass
            
            if moi_A2:
                data["moments_of_inertia"] = moi_A2
            capture_moi = False
                    
        # 6. Rotational Temperatures (Kelvin)
        elif "rotational temperature" in line_lower:
            parts = line.split()
            try:
                idx = [idx for idx, p in enumerate(parts) if "(kelvin)" in p.lower()][0]
                temps = parts[idx+1:]
                data["rot_temps"] = [float(t) for t in temps]
            except (ValueError, IndexError):
                pass
                
        # 7. Vibrational Frequencies (cm^-1)
        elif "frequencies --" in line_lower:
            parts = line.split()
            try:
                idx = parts.index("--")
                freqs = parts[idx+1:]
            except ValueError:
                freqs = parts[2:]
            for f_val in freqs:
                try:
                    data["vib_freqs"].append(float(f_val))
                except ValueError:
                    pass

    return data

def extract_molpro_energy(out_file):
    """
    Extracts the final Coupled Cluster electronic energy from a Molpro output file.
    """
    energy = None
    if not os.path.exists(out_file):
        print(f"Warning: Molpro file '{out_file}' not found.")
        return energy

    with open(out_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if "UCCSD(T) total energy" in line or "!CCSD(T) total energy" in line or "CCSD(T)" in line and "energy" in line and "-" in line:
                parts = line.split()
                for part in parts:
                    try:
                        if part.startswith("-") and len(part) > 8:
                            energy = float(part)
                    except ValueError:
                        pass
    return energy

def main():
    directories = ["reaction1", "reaction2"]

    for directory in directories:
        if not os.path.exists(directory):
            print(f"Skipping missing directory: {directory}")
            continue
            
        print(f"\n--- Processing directory: {directory} ---")
        for subdirectory in os.listdir(directory):
            subdirectory_path = os.path.join(directory, subdirectory)
            specie = subdirectory.split("_")[0]

            if os.path.isdir(subdirectory_path):
                for filename in os.listdir(subdirectory_path):
                    if filename.endswith(".log"):
                        label = filename[:-4]  # Remove .log extension
                        g_log = os.path.join(subdirectory_path, filename)
                        m_out = os.path.join(subdirectory_path, label + "_sp.out")
                        
                        csv_filename = f"{specie}.csv"
                        
                        print(f"Extracting data and writing to {csv_filename}...")
                        
                        g_data = extract_gaussian_data(g_log)
                        m_energy = extract_molpro_energy(m_out)
                        
                        def fmt(val):
                            return val if val is not None else "N/A"
                    
                        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                            writer = csv.writer(csvfile)
                            
                            # Section 1: Fundamental properties required for TST
                            writer.writerow(["Property", "Value", "Units"])
                            writer.writerow(["Electronic Energy (Molpro)", fmt(m_energy), "Ha"])
                            writer.writerow(["ZPE Correction (Gaussian)", fmt(g_data["ZPE_Correction_Ha"]), "Ha"])
                            writer.writerow(["Molecular Mass", fmt(g_data["Mass_amu"]), "amu"])
                            writer.writerow(["Symmetry Number", fmt(g_data["Symmetry_Number"]), ""])
                            writer.writerow(["Pressure", fmt(g_data["Pressure_Atm"]), "Atm"])
                            
                            # Dynamically output Moments of Inertia one after the other
                            if g_data["moments_of_inertia"]:
                                axis_labels = ["Moment of Inertia I_A", "Moment of Inertia I_B", "Moment of Inertia I_C"]
                                for idx, moi_val in enumerate(g_data["moments_of_inertia"]):
                                    lbl = axis_labels[idx] if idx < len(axis_labels) else f"Moment of Inertia {idx+1}"
                                    writer.writerow([lbl, moi_val, "amu*A^2"])
                            else:
                                writer.writerow(["Moment of Inertia", "N/A", "amu*A^2"])
                                
                            writer.writerow(["Electronic Degeneracy", fmt(g_data["Elec_Degeneracy"]), ""])
                            
                            # Blank line separator
                            writer.writerow([])
                            
                            # Section 2: Rotational Temperatures block
                            writer.writerow(["Rotational Temperatures"])
                            writer.writerow(["Mode", "Temperature (K)"])
                            for idx, t_val in enumerate(g_data["rot_temps"], 1):
                                writer.writerow([f"Theta_R{idx}", t_val])
                                
                            # Blank line separator
                            writer.writerow([])
                            
                            # Section 3: Vibrational Frequencies block
                            writer.writerow(["Vibrational Frequencies"])
                            writer.writerow(["Mode", "Wavenumber (cm^-1)"])
                            for idx, f_val in enumerate(g_data["vib_freqs"], 1):
                                writer.writerow([f"Freq_{idx}", f_val])
                            
                        print(f"Processed -> {label} (Saved as {csv_filename})")

    print("\nExtraction complete!")

if __name__ == "__main__":
    main()