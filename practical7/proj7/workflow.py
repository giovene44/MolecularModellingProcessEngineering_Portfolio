import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from pathlib import Path
import sys


def log_message(message, log_file):
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{message}\n")

def extract_thermo_from_eyringpy(eyringpy_log_path, target_temp=300.0, log_file=None):
    """
    Parses the Eyringpy text output log to extract Activation Enthalpy (DH++) 
    and Activation Entropy (DS++) at a specific temperature.
    
    Returns:
        delta_H_kcal (float): Activation enthalpy in kcal/mol
        delta_S_sym (float): Symmetric activation entropy in cal/(mol K)
    """
    if log_file:
        log_message(f"\n--- Extracting Thermodynamics from Eyringpy Log at {target_temp} K ---", log_file)
        
    in_activation_thermo_section = False
    delta_h = None
    delta_s_sym = None
    delta_s_nosym = None

    try:
        with open(eyringpy_log_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Look for the start of the activation thermochemistry block
                if "Activation internal energy and activation enthalpy" in line:
                    in_activation_thermo_section = True
                    continue
                
                if in_activation_thermo_section:
                    # Stop parsing if we reach the next block
                    if "Activation Gibbs free energies" in line:
                        break
                        
                    parts = line.split()
                    # The data lines have exactly 5 columns: T(K), DU++, DS++(sym), DS++(nosym), DH++
                    if len(parts) >= 5:
                        try:
                            t = float(parts[0])
                            # Check if the current line matches the target temperature
                            if abs(t - target_temp) < 0.1:
                                delta_s_sym = float(parts[2])
                                delta_s_nosym = float(parts[3])
                                delta_h = float(parts[4])
                                
                                if log_file:
                                    log_message(f"Found match for {target_temp} K:", log_file)
                                    log_message(f"  DH++ = {delta_h} kcal/mol", log_file)
                                    log_message(f"  DS++ (sym) = {delta_s_sym} cal/mol K", log_file)
                                    log_message(f"  DS++ (nosym) = {delta_s_nosym} cal/mol K", log_file)
                                break
                        except ValueError:
                            # Skip header lines like "T(K) DU++ DS++ DH++"
                            pass
                            
    except FileNotFoundError:
        if log_file:
            log_message(f"Error: Eyringpy output log '{eyringpy_log_path}' not found.", log_file)
        print(f"Error: Log file {eyringpy_log_path} not found.")
        return None, None

    if delta_h is None or delta_s_sym is None:
        if log_file:
            log_message(f"Warning: Could not find thermochemistry data for {target_temp} K in the log.", log_file)
            
    return delta_h, delta_s_sym

def process_kinetic_data(file_notunn, file_wigner, file_eckart, log_file):
    """
    Reads the Eyringpy CSV files and merges them into a single DataFrame.
    """
    log_message("Loading data...", log_file)
    # Load CSVs
    df_base = pd.read_csv(file_notunn)
    df_wig = pd.read_csv(file_wigner)
    df_eck = pd.read_csv(file_eckart)

    # Extract required columns and rename to avoid confusion
    df_base = df_base[['T(K)', 'TST']].rename(columns={'TST': 'k_TST'})
    df_wig = df_wig[['T(K)', 'WIG']].rename(columns={'WIG': 'k_WIG'})
    df_eck = df_eck[['T(K)', 'ECK']].rename(columns={'ECK': 'k_ECK'})

    # Merge on Temperature to align all data points perfectly
    # Using 'outer' to keep all temperatures, even if one file is missing some (like Eckart at 100K)
    df = df_base.merge(df_wig, on='T(K)', how='outer')
    df = df.merge(df_eck, on='T(K)', how='outer')

    # Sort by temperature
    df = df.sort_values('T(K)').reset_index(drop=True)

    # Calculate 1/T and ln(k) for all models
    df['1/T'] = 1 / df['T(K)']
    df['ln_k_TST'] = np.log(df['k_TST'])
    df['ln_k_WIG'] = np.log(df['k_WIG'])
    df['ln_k_ECK'] = np.log(df['k_ECK'])
    
    return df

def plot_arrhenius(df, reaction_prefix='reaction1', log_file=None):
    """
    Point 1: Constructs and saves the Arrhenius Plot.
    """
    if log_file:
        log_message("\n--- Point 1: Generating Arrhenius Plot ---", log_file)
    plt.figure(figsize=(10, 6))
    
    # Plot standard lines
    plt.plot(df['1/T'], df['ln_k_TST'], marker='o', label='Classical TST', linestyle='-', color='black')
    
    # Plot tunneling (dropping NaNs in case Eckart doesn't go as low as Wigner)
    df_wig = df.dropna(subset=['ln_k_WIG'])
    plt.plot(df_wig['1/T'], df_wig['ln_k_WIG'], marker='s', label='Wigner', linestyle='--', color='blue')
    
    df_eck = df.dropna(subset=['ln_k_ECK'])
    plt.plot(df_eck['1/T'], df_eck['ln_k_ECK'], marker='^', label='Eckart', linestyle='-.', color='red')

    # Formatting
    plt.xlabel('1/T (K⁻¹)', fontsize=12)
    plt.ylabel('ln(k)', fontsize=12)
    plt.title('Arrhenius Plot: Classical vs. Tunneling Corrected', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, which='both', linestyle='--', alpha=0.7)
    
    # Save and show
    plt.savefig(f'{reaction_prefix}/{reaction_prefix}_arrhenius_plot.png', dpi=300)
    if log_file:
        log_message(f"Plot saved successfully as '{reaction_prefix}/{reaction_prefix}_arrhenius_plot.png'.", log_file)
    # plt.show()

def calculate_enhancements(df, target_temp=300.0, log_file=None):
    """
    Point 2: Calculates Wigner and Eckart enhancement factors at a specific temperature.
    """
    if log_file:
        log_message(f"\n--- Point 2: Rate Enhancements at {target_temp} K ---", log_file)
    
    # Isolate the row for the target temperature
    row = df[df['T(K)'] == target_temp]
    
    if not row.empty:
        k_tst = row['k_TST'].values[0]
        k_wig = row['k_WIG'].values[0]
        k_eck = row['k_ECK'].values[0]
        
        if log_file:
            log_message(f"Classical Rate (k_TST): {k_tst:.3e}", log_file)
            log_message(f"Wigner Rate (k_WIG): {k_wig:.3e}  |  Enhancement Factor: {k_wig / k_tst:.2f}", log_file)
            log_message(f"Eckart Rate (k_ECK): {k_eck:.3e}  |  Enhancement Factor: {k_eck / k_tst:.2f}", log_file)
    else:
        if log_file:
            log_message(f"Warning: Temperature {target_temp} K not found in the dataset.", log_file)

def extract_arrhenius_parameters(df, min_temp=1000.0, log_file=None):
    """
    Point 3: Extracts apparent Arrhenius parameters using linear regression 
    at high temperatures where tunneling is negligible.
    """
    if log_file:
        log_message(f"\n--- Point 3: Apparent Arrhenius Parameters (Fitted for T >= {min_temp} K) ---", log_file)
    R_J = 8.314462618 # Gas constant in J/(mol K)
    
    # Filter for high temperatures and drop missing data
    high_t_df = df[df['T(K)'] >= min_temp].dropna(subset=['1/T', 'ln_k_TST'])
    
    if len(high_t_df) >= 2:
        # Perform linear regression on 1/T vs ln(k)
        slope, intercept, r_value, p_value, std_err = linregress(high_t_df['1/T'], high_t_df['ln_k_TST'])
        
        # Calculate parameters
        Ea_J = -slope * R_J
        Ea_kJ = Ea_J / 1000
        A = np.exp(intercept)
        
        if log_file:
            log_message(f"Temperature Range Used: {high_t_df['T(K)'].min()} K to {high_t_df['T(K)'].max()} K", log_file)
            log_message(f"Activation Energy (Ea): {Ea_kJ:.2f} kJ/mol", log_file)
            log_message(f"Pre-exponential Factor (A): {A:.3e}", log_file)
            log_message(f"R-squared of fit: {r_value**2:.4f}", log_file)
    else:
        if log_file:
            log_message(f"Not enough data points found at or above {min_temp} K to perform regression.", log_file)

def analyze_thermodynamics(delta_H_kcal, delta_S_cal, T=300, log_file=None):
    """
    Point 4: Analyzes thermodynamic bottlenecks. 
    NOTE: These values must be pulled manually from your Eyringpy text/log output.
    """
    if log_file:
        log_message("\n--- Point 4: Thermodynamic Bottlenecks ---", log_file)
    
    # Convert input properties to standard SI/kJ units
    # 1 kcal = 4.184 kJ, 1 cal = 4.184 J
    delta_H_kJ = delta_H_kcal * 4.184
    delta_S_J_K = delta_S_cal * 4.184
    delta_S_kJ_K = delta_S_J_K / 1000
    
    T_delta_S_kJ = T * delta_S_kJ_K
    delta_G_kJ = delta_H_kJ - T_delta_S_kJ
    
    if log_file:
        log_message(f"At T = {T} K:", log_file)
        log_message(f"Enthalpy of Activation (ΔH‡):      {delta_H_kJ:.2f} kJ/mol", log_file)
        log_message(f"Entropic Term (-TΔS‡):             {-T_delta_S_kJ:.2f} kJ/mol", log_file)
        log_message(f"Gibbs Free Energy (ΔG‡):           {delta_G_kJ:.2f} kJ/mol", log_file)
    
    if abs(-T_delta_S_kJ) >= abs(delta_H_kJ):
        if log_file:
            log_message("Conclusion: The dominant bottleneck is ENTROPIC (|-TΔS‡| >= |ΔH‡|).", log_file)
    elif abs(-T_delta_S_kJ) >= (0.5 * abs(delta_H_kJ)):
        if log_file:
            log_message("Conclusion: The bottleneck is heavily mixed, with a major entropic penalty.", log_file)
    else:
        if log_file:
            log_message("Conclusion: The dominant bottleneck is ENTHALPIC (|ΔH‡| > |-TΔS‡|).", log_file)

def extract_imaginary_frequency(ts_log_path, log_file=None):
    """
    Parses a Gaussian TS output log to extract the imaginary frequency.
    
    Returns:
        imaginary_freq (float): The imaginary frequency in cm^-1 (represented as a negative value), 
                                or None if not found.
    """
    if log_file:
        log_message(f"\n--- Extracting Imaginary Frequency from TS Log ---", log_file)
        
    imaginary_freq = None

    try:
        with open(ts_log_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Look for the line containing the frequencies
                if "Frequencies --" in line:
                    # Line format usually: Frequencies --  -1234.5678   12.3456   23.4567
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                            # The first frequency is at index 2
                            freq = float(parts[2])
                            # Imaginary frequencies are represented as negative numbers in Gaussian
                            if freq < 0:
                                imaginary_freq = freq
                                if log_file:
                                    log_message(f"Found imaginary frequency: {imaginary_freq} cm^-1", log_file)
                                break # Stop searching after the first match is found
                        except ValueError:
                            pass
    except FileNotFoundError:
        if log_file:
            log_message(f"Error: TS log file '{ts_log_path}' not found.", log_file)
        print(f"Error: Log file {ts_log_path} not found.")
        return None

    if imaginary_freq is None:
        if log_file:
            log_message(f"Warning: Could not find an imaginary frequency in {ts_log_path}.", log_file)
            
    return imaginary_freq

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python workflow.py <reaction_prefix>")
        print("Example: python workflow.py reaction1")
        sys.exit(1)
    else:
        reaction_prefix = sys.argv[1]

    # File paths
    file_no_tunneling = f'{reaction_prefix}/{reaction_prefix}_noTunn.csv'
    file_wigner = f'{reaction_prefix}/{reaction_prefix}_Wigner.csv'
    file_eckart = f'{reaction_prefix}/{reaction_prefix}_Eckart.csv'
    log_file = f'{reaction_prefix}/{reaction_prefix}_analysis.log' # Renamed to avoid clashing with Eyringpy's log
    eyringpy_raw_log = f'{reaction_prefix}/{reaction_prefix}_noTunn.eof' 
    
    Path(reaction_prefix).mkdir(parents=True, exist_ok=True)
    Path(log_file).write_text('', encoding='utf-8')
    
    target_temperature = 300.0
    
    # Run the core analysis pipeline
    try:
        ts_log_path = f'{reaction_prefix}/ts/ts_m4.log'
        imag_freq = extract_imaginary_frequency(ts_log_path, log_file=log_file)

        df_kinetics = process_kinetic_data(file_no_tunneling, file_wigner, file_eckart, log_file)
        plot_arrhenius(df_kinetics, reaction_prefix=reaction_prefix, log_file=log_file)
        calculate_enhancements(df_kinetics, target_temp=target_temperature, log_file=log_file)
        extract_arrhenius_parameters(df_kinetics, min_temp=1000.0, log_file=log_file)
        
        extracted_H, extracted_S = extract_thermo_from_eyringpy(
            eyringpy_log_path=eyringpy_raw_log, 
            target_temp=target_temperature, 
            log_file=log_file
        )
        
        if extracted_H is not None and extracted_S is not None:
            analyze_thermodynamics(
                delta_H_kcal=extracted_H, 
                delta_S_cal=extracted_S, 
                T=target_temperature, 
                log_file=log_file
            )
        else:
            log_message("Skipping thermodynamic analysis due to missing data.", log_file)
        
    except FileNotFoundError as e:
        log_message(f"\nERROR: Could not find one of the required files. \n{e}", log_file)
        log_message("Please ensure all CSVs and the Eyringpy log file are in the target folder.", log_file)