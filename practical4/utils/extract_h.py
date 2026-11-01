import csv

def parse_gaussian_output(filepath):
    # Initialize defaults for an atom
    frequencies = []
    rot_temps = []
    mass = None
    sym_num = 1.0  # Default to 1.0 for atoms
    temperature = None
    pressure = None
    multiplicity = None

    with open(filepath, 'r') as file:
        for line in file:
            # Catch Multiplicity from the Z-matrix line
            if "Multiplicity =" in line:
                parts = line.split()
                multiplicity = int(parts[-1])

            # Catch Mass
            elif "Molecular mass:" in line:
                mass = float(line.split()[2])

            # Catch Symmetry (if it exists)
            elif "Rotational symmetry number" in line:
                sym_num = float(line.split()[3].rstrip('.'))

            # Catch Temp and Pressure
            elif "Temperature " in line and "Pressure " in line:
                parts = line.split()
                temperature = float(parts[1])
                pressure = float(parts[4])

            # Catch Frequencies (will skip for H)
            elif "Frequencies --" in line:
                frequencies.extend([float(x) for x in line.split()[2:]])

            # Catch Rotational Temps (will skip for H)
            elif "Rotational temperatures (Kelvin)" in line:
                rot_temps.extend([float(x) for x in line.split()[3:]])

    return {
        "mass_amu": mass,
        "symmetry_number": sym_num,
        "temperature_K": temperature,
        "pressure_atm": pressure,
        "gel": multiplicity,
        "rotational_temperatures_K": rot_temps,
        "frequencies_cm_1": frequencies
    }


def main():

    input_file = "h_b3lyp_6-31gdp.log"
    output_file = input_file.replace(".log", ".csv").replace(".out", ".csv")
    if input_file == output_file:
        output_file += ".csv"

    print(f"Parsing {input_file}...")
    data = parse_gaussian_output(input_file)

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write single-value properties
        writer.writerow(["Property", "Value", "Units"])
        writer.writerow(["Molecular Mass", data["mass_amu"], "amu"])
        writer.writerow(["Symmetry Number", data["symmetry_number"], ""])
        writer.writerow(["Temperature", data["temperature_K"], "K"])
        writer.writerow(["Pressure", data["pressure_atm"], "Atm"])
        # New row added here:
        writer.writerow(["gel", data["gel"], ""])
        writer.writerow([])

        # Write Rotational Temperatures
        writer.writerow(["Rotational Temperatures"])
        writer.writerow(["Mode", "Temperature (K)"])
        for i, t in enumerate(data["rotational_temperatures_K"]):
            writer.writerow([f"Theta_R{i+1}", t])
        writer.writerow([])

        # Write Frequencies
        writer.writerow(["Vibrational Frequencies"])
        writer.writerow(["Mode", "Wavenumber (cm^-1)"])
        for i, f in enumerate(data["frequencies_cm_1"]):
            writer.writerow([f"Freq_{i+1}", f])

    print(f"Success! Data exported to {output_file}")

if __name__ == "__main__":
    main()
