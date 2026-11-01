#!/usr/bin/python3
import sys
import os

# Dictionary to map atomic numbers to symbols (expandable if needed)
ATOMIC_NUMBERS = {
    1: "H",
    6: "C",
    7: "N"
}

def extract_charge_and_spin(lines):
    """
    Scans the log file lines for the Charge and Multiplicity definition.
    Converts Gaussian Multiplicity (2S + 1) to Molpro Spin (2S).
    """
    charge = 0
    molpro_spin = 0
    found = False

    for line in lines:
        if "Charge =" in line and "Multiplicity =" in line:
            # Example line: " Charge =  0 Multiplicity = 2"
            # Strip out the text and equals signs to isolate the numbers
            clean_line = line.replace("Charge", "").replace("Multiplicity", "").replace("=", "")
            parts = clean_line.split()
            try:
                charge = int(parts[0])
                multiplicity = int(parts[1])
                # Molpro spin is the number of unpaired electrons (Multiplicity - 1)
                molpro_spin = multiplicity - 1  
                found = True
                print(f"Detected Gaussian settings -> Charge: {charge}, Multiplicity: {multiplicity}")
                print(f"Converted to Molpro spin  -> Unpaired Electrons: {molpro_spin}")
                break
            except (ValueError, IndexError):
                pass
                
    if not found:
        print("Warning: Could not automatically detect Charge and Multiplicity. Defaulting to Charge=0, Spin=0.")
        
    return charge, molpro_spin

def extract_final_geometry(lines):
    """
    Scans the Gaussian log file lines for the last 'Standard orientation' block
    and extracts the atomic symbols and XYZ coordinates.
    """
    geometry = []
    
    # Search backwards to find the LAST optimized geometry block
    block_start_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        if "Standard orientation:" in lines[i] or "Input orientation:" in lines[i]:
            block_start_idx = i
            break
            
    if block_start_idx == -1:
        print("Error: Could not find any coordinate orientation block in the log file.")
        sys.exit(1)

    # Parse the coordinate block
    # Standard orientation header is followed by 4 lines of dashes/headers
    idx = block_start_idx + 5 
    while idx < len(lines):
        line = lines[lines].strip() if isinstance(lines, dict) else lines[idx].strip()
        if line.startswith("---"):  # End of the coordinate block
            break
            
        parts = line.split()
        if len(parts) == 6:
            try:
                atomic_num = int(parts[1])
                x, y, z = parts[3], parts[4], parts[5]
                symbol = ATOMIC_NUMBERS.get(atomic_num, f"Z{atomic_num}")
                geometry.append((symbol, x, y, z))
            except ValueError:
                pass
        idx += 1

    return geometry

def write_molpro_input(molpro_filename, geometry, charge=0, spin=0, basis="cc-pvtz"):
    """
    Writes the extracted geometry into a formatted Molpro CCSD(T) input file.
    """
    with open(molpro_filename, 'w') as f:
        f.write(f"***, CCSD(T) Single Point Energy for {os.path.basename(molpro_filename)}\n")
        f.write("memory, 1000, m\n\n")
        
        f.write("geometry={\nangstrom\n")
        for sym, x, y, z in geometry:
            f.write(f" {sym:<4} {float(x):>12.6f} {float(y):>12.6f} {float(z):>12.6f}\n")
        f.write("}\n\n")
        
        f.write(f"basis={basis}\n\n")
        f.write(f"set, charge={charge}\n")
        f.write(f"set, spin={spin}    ! Number of unpaired electrons\n\n")
        
        f.write("{rhf}\n")
        f.write("{uccsd(t)}\n")
        
    print(f"Success: Molpro input written to '{molpro_filename}'")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 gauss2molpro.py <gaussian_output.log>")
        print("Example: python3 gauss2molpro.py ch3_opt.log")
        sys.exit(1)

    log_file = sys.argv[1]
    
    if not os.path.exists(log_file):
        print(f"Error: File '{log_file}' not found.")
        sys.exit(1)
        
    base_name = os.path.splitext(log_file)[0]
    molpro_file = f"{base_name}_sp.inp"

    print(f"Reading: {log_file}...")
    with open(log_file, 'r') as file:
        lines = file.readlines()

    # Automatically extract everything from the read lines
    charge, spin = extract_charge_and_spin(lines)
    geom = extract_final_geometry(lines)
    
    print(f"Extracted {len(geom)} atoms.")
    write_molpro_input(molpro_file, geom, charge=charge, spin=spin)

if __name__ == "__main__":
    main()
