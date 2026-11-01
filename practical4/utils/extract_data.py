#!/usr/bin/python3
import sys
import re
import csv
import os

def extract_gaussian_data(filepath):
    e_elec = None
    zpe = 0.0 # Defaults to 0 so it works for isolated atoms
    
    with open(filepath, 'r') as f:
        for line in f:
            # 1. Check for the basic SCF energy (Fallback)
            if "SCF Done:" in line:
                match = re.search(r'E\([a-zA-Z0-9-]+\)\s*=\s*([-+]?\d*\.\d+)', line)
                if match:
                    e_elec = float(match.group(1)) * 627.5095
            
            # 2. Check for MP2 correlation energy
            elif "EUMP2 =" in line:
                match = re.search(r'EUMP2\s*=\s*([-+]?\d*\.\d+[dD]?[+-]?\d*)', line)
                if match:
                    # Replace Fortran 'D' scientific notation with python 'e'
                    val_str = match.group(1).replace('D', 'e').replace('d', 'e')
                    e_elec = float(val_str) * 627.5095
                    
            # 3. Check for CCSD(T) correlation energy
            elif "CCSD(T)=" in line:
                match = re.search(r'CCSD\(T\)=\s*([-+]?\d*\.\d+[dD]?[+-]?\d*)', line)
                if match:
                    val_str = match.group(1).replace('D', 'e').replace('d', 'e')
                    e_elec = float(val_str) * 627.5095
                    
            # 4. Check for Double Hybrid (B2PLYP, etc.) total energy
            # Broadened regex to catch E(B2PLYP), E(UB2PLYP+D3), E(B2PLYPD3), etc.
            elif re.search(r'E\([U]?[a-zA-Z0-9+]*B2PLYP[a-zA-Z0-9+]*\)', line):
                match = re.search(r'E\([U]?[a-zA-Z0-9+]*B2PLYP[a-zA-Z0-9+]*\)\s*=\s*([-+]?\d*\.\d+[dD]?[+-]?\d*)', line)
                if match:
                    val_str = match.group(1).replace('D', 'e').replace('d', 'e')
                    e_elec = float(val_str) * 627.5095

            # 5. Extract the Zero-point correction
            elif "Zero-point correction=" in line:
                match = re.search(r'Zero-point correction=\s*([-+]?\d*\.\d+)', line)
                if match:
                    zpe = float(match.group(1)) * 627.5095
                    
    return e_elec, zpe

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./extract_energy.py <gaussian_output_file.log>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    e_elec, zpe = extract_gaussian_data(filepath)
    
    if e_elec is not None:
        corrected_energy = e_elec + zpe
        print(f"File: {filepath}")
        print(f"Electronic Energy (E_elec): {e_elec:.6f} kcal/mol")
        print(f"Zero-Point Energy (ZPE):    {zpe:.6f} kcal/mol")
        print(f"Corrected Energy at 0 K:    {corrected_energy:.6f} kcal/mol")
        
        # Write to CSV
        csv_filename = f"{filepath.split('_')[0]}.csv"
        file_exists = os.path.isfile(csv_filename)
        theory = os.path.basename(filepath).split('/')[-1].split('_')[1]  # Extract the method from filename
        basis_set = os.path.basename(filepath).split('/')[-1].split('_')[2].replace('.log', '')  # Extract the basis set from filename
        with open(csv_filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            if not file_exists:
                writer.writerow(['Theory', 'Basis Set', 'E_elec (kcal/mol)', 'ZPE (kcal/mol)', 'Corrected Energy (kcal/mol)'])
            writer.writerow([theory, basis_set, f"{e_elec:.6f}".replace('.', ','), f"{zpe:.6f}".replace('.', ','), f"{corrected_energy:.6f}".replace('.', ',')])
        
    else:
        print(f"Error: Could not find an 'SCF Done' electronic energy in {filepath}.")
