#!/usr/bin/python3
import os

def generate_gaussian_inputs():
    # Define the computational methods
    methods = ["HF", "B3LYP", "M062X", "B2PLYPD3", "MP2", "CCSD(T)"]
    
    # Define a selection of Pople and correlation consistent (cc) basis sets

    basis_sets = ["6-31G(d,p)", "6-311+G(2d,p)", "cc-pVDZ", "cc-pVTZ", "aug-cc-pVDZ","aug-cc-pVTZ"]
    # Define species: "Name": (Charge, Multiplicity, "XYZ Coordinates")
    # Note: These are rough starting coordinates. 

    species = {
        "H": (0, 2, "H", "", "./hydrogen/h/"),
        "H2": (0, 1, "H\nH 1 R1", "R1=0.74", "./hydrogen/h2/"),
        "CH3": (0, 2, "C\nH 1 R1\nH 1 R1 2 A1\nH 1 R1 2 A1 3 D1", "R1=1.07\nA1=120.0\nD1=180.0", "./methane/ch3/"),
        "CH4": (0, 1, "C\nH 1 R1\nH 1 R1 2 A1\nH 1 R1 2 A1 3 D1\nH 1 R1 2 A1 3 D2", "R1=1.09\nA1=109.471\nD1=120.0\nD2=-120.0", "./methane/ch4/"),
        "NH2": (0, 2, "N\nH 1 R1\nH 1 R1 2 A1", "R1=1.00\nA1=105.0", "./methylamine/nh2/"),
        "CH3NH2": (0, 1, "C\nN 1 R1\nH 1 R2 2 A1\nH 1 R2 2 A1 3 D1\nH 1 R2 2 A1 3 D2\nH 2 R3 1 A2 3 D3\nH 2 R3 1 A2 3 D4", "R1=1.47\nR2=1.09\nR3=1.01\nA1=109.5\nA2=109.5\nD1=120.0\nD2=-120.0\nD3=60.0\nD4=-60.0", "./methylamine/ch3nh2/")
    }

    for mol_name, (charge, mult, zmat, variables, path) in species.items():
        for method in methods:
            for basis in basis_sets:
                # if method == "CCSD(T)" and basis == "aug-cc-pVTZ":
                #     print(f"Skipping {method} with {basis} for {mol_name} due to computational cost.")
                #     continue
                
                # The H atom does not vibrate, so we omit Freq and Opt
                if mol_name == "H":
                    route = f"#p {method}/{basis}"
                else:
                    route = f"#p {method}/{basis} Opt Freq"
                
                # Identify and impose symmetry for faster calculations
                symmetry = ""
                if mol_name == "CH4":
                    symmetry = "Td"  # Tetrahedral symmetry
                elif mol_name == "CH3":
                    symmetry = "D3h"  # Trigonal planar symmetry
                elif mol_name == "H2":
                    symmetry = "D2h"  # Linear symmetry

                if symmetry:
                    route += f" Symm=PG={symmetry}"
                    print(f"Applying {symmetry} symmetry to {mol_name}")
                
                # Create a clean filename
                clean_basis = basis.replace(',', '').replace('(', '').replace(')', '').replace('+', 'plus')
                dir_path = os.path.dirname(path)
                os.makedirs(f"{dir_path}", exist_ok=True)
                mol_name_lower = mol_name.lower()
                
                filename = f"{dir_path}/{mol_name_lower}_{method.replace('(', '').replace(')', '')}_{clean_basis}.com".lower()
                tmp_filename = f"{dir_path}/{mol_name_lower}_{method.replace('(', '').replace(')', '')}_{clean_basis}.chk".lower()
                
                with open(filename, "w") as f:
                    f.write(f"%nprocshared=8\n")
                    f.write(f"%mem=16GB\n")
                    f.write(f"%chk={tmp_filename}\n\n")
                    f.write(f"{route}\n\n")
                    f.write(f"{mol_name} optimization {method} {basis}\n\n")
                    f.write(f"{charge} {mult}\n")
                    f.write(f"{zmat}\n")
                    # If variables exist, write a blank line, then the variables
                    if variables:
                        f.write(f"\n{variables}\n")
                    # Final blank line required by Gaussian to terminate the geometry/variables section
                    f.write("\n")

    print(f"Input files generated successfully")

if __name__ == "__main__":
    generate_gaussian_inputs()