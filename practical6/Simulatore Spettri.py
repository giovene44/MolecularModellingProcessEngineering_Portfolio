import sys
import io
import os
import re
import argparse
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def lorentzian(x: np.ndarray, x0: float, area: float, gamma: float) -> np.ndarray:
    return area / np.pi * (gamma / ((x - x0) ** 2 + gamma ** 2))

MULTIPLET_NAMES = {1: 'singlet (s)', 2: 'doublet (d)', 3: 'triplet (t)', 4: 'quartet (q)', 5: 'quintet (quint)', 6: 'sextet (sext)', 7: 'septet (sept)'}

def pascal_row(n: int) -> List[int]:
    row = [1]
    for k in range(1, n + 1):
        row.append(row[-1] * (n - k + 1) // k)
    return row

def multiplet_positions(center: float, J_ppm: float, n_lines: int) -> np.ndarray:
    offsets = np.arange(n_lines) - (n_lines - 1) / 2.0
    return center + offsets * J_ppm

@dataclass
class NMRPeak:
    label: str
    shift_ppm: float
    J_Hz: List[float]
    n_neighbors: List[int]
    area: float = 1.0
    gamma: float = 0.015
    annotation: str = ''

    def __post_init__(self):
        if len(self.J_Hz) != len(self.n_neighbors):
            raise ValueError(f"Peak '{self.label}': J_Hz and n_neighbors must have the same length.")

    @property
    def multiplicity_name(self) -> str:
        if len(self.n_neighbors) == 0:
            return "singlet (s)"
        if len(self.n_neighbors) == 1:
            n_lines = self.n_neighbors[0] + 1
            return MULTIPLET_NAMES.get(n_lines, f'{n_lines}-let')
        else:
            parts = []
            for n in self.n_neighbors:
                n_lines = n + 1
                abbrev = {1: 's', 2: 'd', 3: 't', 4: 'q', 5: 'quint', 6: 'sext', 7: 'sept'}.get(n_lines, f'{n_lines}')
                parts.append(abbrev)
            return ''.join(parts) + f" ({'×'.join((str(n + 1) for n in self.n_neighbors))} lines)"

@dataclass
class Molecule:
    name: str
    formula: str
    peaks: List[NMRPeak]
    spectrometer_MHz: float = 400.0
    solvent: str = 'Computational'
    notes: str = ''

def simulate_peak(x: np.ndarray, peak: NMRPeak, spectrometer_MHz: float) -> np.ndarray:
    sub_peaks: List[Tuple[float, float]] = [(peak.shift_ppm, 1.0)]
    for J_Hz, n_neigh in zip(peak.J_Hz, peak.n_neighbors):
        if n_neigh == 0:
            continue
        J_ppm = J_Hz / spectrometer_MHz
        intensities = pascal_row(n_neigh)
        norm = sum(intensities)
        n_lines = n_neigh + 1
        new_sub_peaks = []
        for pos, rel_int in sub_peaks:
            positions = multiplet_positions(pos, J_ppm, n_lines)
            for sub_pos, pascal_int in zip(positions, intensities):
                new_sub_peaks.append((sub_pos, rel_int * pascal_int / norm))
        sub_peaks = new_sub_peaks
    y = np.zeros_like(x)
    for pos, rel_int in sub_peaks:
        y += lorentzian(x, pos, peak.area * rel_int, peak.gamma)
    return y

def simulate_spectrum(x: np.ndarray, molecule: Molecule) -> Tuple[np.ndarray, List[np.ndarray]]:
    y_total = np.zeros_like(x)
    y_individual = []
    for peak in molecule.peaks:
        y_peak = simulate_peak(x, peak, molecule.spectrometer_MHz)
        y_total += y_peak
        y_individual.append(y_peak)
    return (y_total, y_individual)

def compute_integration_curve(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    dx = np.abs(np.gradient(x))
    integral = np.cumsum(y * dx)
    if integral[-1] > 0:
        integral /= integral[-1]
    return integral

PEAK_COLORS = ['#2196F3', '#E91E63', '#4CAF50', '#FF9800', '#9C27B0', '#00BCD4', '#F44336', '#CDDC39']

def plot_spectrum(x: np.ndarray, molecule: Molecule, y_total: np.ndarray, y_individual: List[np.ndarray], show_integration: bool=True, show_individual: bool=True, show_annotations: bool=True, show_peak_table: bool=True, figsize: Tuple[float, float]=(14, 7), save_filename: Optional[str]=None, dpi: int=300) -> plt.Figure:
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(x, y_total, color='#1a1a2e', linewidth=1.2, zorder=5, label='Total spectrum')
    if show_individual:
        for i, (peak, y_peak) in enumerate(zip(molecule.peaks, y_individual)):
            color = PEAK_COLORS[i % len(PEAK_COLORS)]
            ax.fill_between(x, y_peak, alpha=0.15, color=color, zorder=2)
            ax.plot(x, y_peak, color=color, linewidth=0.8, alpha=0.6, linestyle='--', zorder=3, label=f'{peak.label} ({peak.multiplicity_name})')
    if show_integration:
        integral = compute_integration_curve(x, y_total)
        y_max = np.max(y_total)
        integral_scaled = integral * y_max * 0.5 + y_max * 0.05
        ax.plot(x, integral_scaled, color='#d32f2f', linewidth=1.5, alpha=0.7, zorder=4, label='Integration curve')
        _annotate_integration_steps(ax, x, integral_scaled, molecule)
    if show_annotations:
        y_max = np.max(y_total)
        for i, (peak, y_peak) in enumerate(zip(molecule.peaks, y_individual)):
            color = PEAK_COLORS[i % len(PEAK_COLORS)]
            _annotate_peak(ax, x, y_peak, peak, molecule.spectrometer_MHz, color, y_max)
    ax.invert_xaxis()
    ax.set_xlabel('Chemical Shift, $\\delta$ (ppm)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Relative Intensity', fontsize=13, fontweight='bold')
    ax.set_yticks([])
    title = f'Simulated ¹H NMR Spectrum (Gaussian 16)\n{molecule.name} at {molecule.spectrometer_MHz:.0f} MHz'
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.grid(axis='x', linestyle='--', alpha=0.3, zorder=0)
    ax.set_ylim(0, np.max(y_total) * 1.5)
    ax.axvline(x=0, color='#888888', linestyle=':', linewidth=1.0, alpha=0.5)
    ax.annotate('TMS\n(δ = 0)', xy=(0, 0), xytext=(0.3, np.max(y_total) * 0.05), fontsize=8, color='#888888', ha='center', va='bottom', fontstyle='italic')
    ax.legend(loc='upper right', fontsize=8, framealpha=0.9, edgecolor='#cccccc')
    if show_peak_table:
        _add_peak_table(fig, ax, molecule)
    fig.tight_layout()
    if save_filename:
        fig.savefig(save_filename, dpi=dpi, bbox_inches='tight', facecolor='white')
        print(f"  ✓ Spectrum saved to '{save_filename}'")
    return fig

def _annotate_peak(ax: plt.Axes, x: np.ndarray, y_peak: np.ndarray, peak: NMRPeak, spec_MHz: float, color: str, y_max: float) -> None:
    peak_max = np.max(y_peak)
    if peak_max < 1e-10:
        return
    label_parts = [peak.label]
    label_parts.append(peak.multiplicity_name)
    if any((J > 0 for J in peak.J_Hz)):
        J_str = ', '.join((f'J = {J:.1f} Hz' for J in peak.J_Hz if J > 0))
        label_parts.append(J_str)
    label_parts.append(f'∫ = {peak.area:.0f}H')
    if peak.annotation:
        label_parts.append(f'({peak.annotation})')
    text = '\n'.join(label_parts)
    y_text = peak_max + y_max * 0.12
    ax.annotate(text, xy=(peak.shift_ppm, peak_max), xytext=(peak.shift_ppm, y_text), fontsize=8, ha='center', va='bottom', color=color, fontweight='bold', arrowprops=dict(arrowstyle='-|>', color=color, lw=1.2, connectionstyle='arc3,rad=0.1'), bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color, alpha=0.9, linewidth=1.0), zorder=10)

def _annotate_integration_steps(ax: plt.Axes, x: np.ndarray, integral: np.ndarray, molecule: Molecule) -> None:
    total_area = sum((p.area for p in molecule.peaks))
    cumulative = 0
    for peak in sorted(molecule.peaks, key=lambda p: -p.shift_ppm):
        cumulative += peak.area
        idx = np.argmin(np.abs(x - peak.shift_ppm))
        val = integral[idx]
        ax.annotate(f'{peak.area:.0f}H', xy=(x[idx], val), fontsize=7, color='#d32f2f', ha='left', va='bottom', fontstyle='italic')

def _add_peak_table(fig: plt.Figure, ax: plt.Axes, molecule: Molecule) -> None:
    table_data = []
    headers = ['Group', 'δ (ppm)', 'Pattern', 'J (Hz)', '# H']
    for peak in molecule.peaks:
        J_str = ', '.join((f'{J:.1f}' for J in peak.J_Hz)) if any((J > 0 for J in peak.J_Hz)) else '—'
        table_data.append([peak.label, f'{peak.shift_ppm:.2f}', peak.multiplicity_name.split('(')[0].strip(), J_str, f'{peak.area:.0f}'])
    table = ax.table(cellText=table_data, colLabels=headers, loc='bottom', bbox=[0.0, -0.35, 1.0, 0.04 + 0.04 * len(table_data)], cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    for j, header in enumerate(headers):
        cell = table[0, j]
        cell.set_facecolor('#e3f2fd')
        cell.set_text_props(fontweight='bold')
    for i in range(1, len(table_data) + 1):
        for j in range(len(headers)):
            cell = table[i, j]
            cell.set_facecolor('#fafafa' if i % 2 == 0 else 'white')

# --- G16 Parsers ---

def parse_g16_shieldings(filepath: str) -> Dict[int, float]:
    """Parses isotropic magnetic shieldings for Hydrogen atoms."""
    shieldings = {}
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    in_nmr_section = False
    for line in lines:
        if "SCF GIAO Magnetic shielding tensor (ppm):" in line:
            in_nmr_section = True
            continue
            
        if in_nmr_section:
            match = re.match(r'\s*(\d+)\s+([A-Za-z]+)\s+Isotropic\s*=\s*(-?\d+\.\d+)', line)
            if match:
                idx = int(match.group(1))
                atom_type = match.group(2).upper()
                iso_val = float(match.group(3))
                if atom_type == 'H':
                    shieldings[idx] = iso_val
            elif " ****" in line or (line.strip() == "" and "Isotropic" not in "".join(lines[lines.index(line):lines.index(line)+5])):
                # Check next few lines to see if section is really over. A simpler way: just keep parsing until end of file
                pass
            if "Leave Link" in line and in_nmr_section:
                in_nmr_section = False
    return shieldings

def parse_g16_j_couplings(filepath: str) -> Dict[Tuple[int, int], float]:
    """Parses the total nuclear spin-spin coupling J (Hz) matrix."""
    couplings = {}
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    in_j_section = False
    col_headers = []
    
    for line in lines:
        if "Total nuclear spin-spin coupling J (Hz):" in line:
            in_j_section = True
            continue
            
        if in_j_section:
            if re.match(r'^\s+(\d+\s+)+\d*\s*$', line):
                col_headers = [int(x) for x in line.split()]
                continue
                
            tokens = line.split()
            if len(tokens) >= 2 and tokens[0].isdigit():
                row_idx = int(tokens[0])
                values = tokens[1:]
                for i, val in enumerate(values):
                    try:
                        j_val = float(val.replace('D', 'E').replace('d', 'e'))
                        col_idx = col_headers[i]
                        if row_idx != col_idx:
                            pair = tuple(sorted((row_idx, col_idx)))
                            couplings[pair] = j_val
                    except ValueError:
                        pass
                continue
            
            if "Leave Link" in line or "End of Minotr" in line or "-------" in line or "Total nuclear" in line:
                in_j_section = False
                
    return couplings

def process_g16_outputs(target_file: str, tms_file: str, coupling_threshold: float = 0.5, freq_mhz: float = 400.0) -> Molecule:
    tms_shieldings = parse_g16_shieldings(tms_file)
    if not tms_shieldings:
        raise ValueError("Could not find any Hydrogen isotropic shieldings in the TMS file.")
    
    tms_ref = sum(tms_shieldings.values()) / len(tms_shieldings)
    print(f"Computed TMS Reference Shielding: {tms_ref:.4f} ppm")
    
    target_shieldings = parse_g16_shieldings(target_file)
    if not target_shieldings:
        raise ValueError("Could not find any Hydrogen isotropic shieldings in the Target file.")
        
    target_j_couplings = parse_g16_j_couplings(target_file)
    if target_j_couplings:
        print(f"Found spin-spin couplings! Using a threshold of {coupling_threshold} Hz for splitting.")
    else:
        print("No spin-spin couplings found. Spectra will be simulated as singlets.")
        
    # Group equivalent protons based on chemical shift (tolerance 0.05 ppm)
    chemical_shifts = {idx: tms_ref - iso for idx, iso in target_shieldings.items()}
    
    groups = []
    for idx, shift in chemical_shifts.items():
        found_group = False
        for g in groups:
            if abs(g['shift'] - shift) < 0.05:
                g['indices'].append(idx)
                g['shift'] = sum([chemical_shifts[i] for i in g['indices']]) / len(g['indices'])
                found_group = True
                break
        if not found_group:
            groups.append({'indices': [idx], 'shift': shift})
            
    groups.sort(key=lambda g: -g['shift'])
    
    for i, g in enumerate(groups):
        g['label'] = f"Group {chr(65+i)}"
        
    peaks = []
    for g in groups:
        shift = g['shift']
        area = float(len(g['indices']))
        j_hz_list = []
        n_neighbors_list = []
        
        for other_g in groups:
            if g == other_g:
                continue
                
            couplings = []
            for idx1 in g['indices']:
                for idx2 in other_g['indices']:
                    pair = tuple(sorted((idx1, idx2)))
                    if pair in target_j_couplings:
                        couplings.append(target_j_couplings[pair])
                        
            if couplings:
                avg_j = sum(couplings) / len(couplings)
                if abs(avg_j) >= coupling_threshold:
                    j_hz_list.append(abs(avg_j))
                    n_neighbors_list.append(len(other_g['indices']))
                    
        if not j_hz_list:
            j_hz_list = [0.0]
            n_neighbors_list = [0]
            
        peaks.append(NMRPeak(
            label=g['label'],
            shift_ppm=shift,
            J_Hz=j_hz_list,
            n_neighbors=n_neighbors_list,
            area=area,
            gamma=0.015,
            annotation=f"H atoms: {', '.join(map(str, g['indices']))}"
        ))
        
    mol_name = os.path.basename(target_file).split('.')[0]
    return Molecule(
        name=mol_name,
        formula="G16 Calculation",
        peaks=peaks,
        spectrometer_MHz=freq_mhz,
        solvent="Computational"
    )

def main():
    parser = argparse.ArgumentParser(description="Simulate 1H NMR from Gaussian 16 outputs.")
    parser.add_argument("target", nargs='?', help="Path to the Target Molecule G16 output file (.log or .out)")
    parser.add_argument("tms", nargs='?', help="Path to the TMS Reference G16 output file (.log or .out)")
    parser.add_argument("-f", "--freq", type=float, default=400.0, help="Spectrometer frequency in MHz (default: 400.0)")
    
    args = parser.parse_args()
    
    target_file = args.target
    tms_file = args.tms
    
    if not target_file or not tms_file:
        print("Please provide the G16 output files.")
        target_file = input("Enter path to Target Molecule output: ").strip()
        tms_file = input("Enter path to TMS Reference output: ").strip()
        
    if not os.path.exists(target_file):
        print(f"Error: Target file not found at '{target_file}'")
        return
    if not os.path.exists(tms_file):
        print(f"Error: TMS file not found at '{tms_file}'")
        return

    try:
        mol = process_g16_outputs(target_file, tms_file, freq_mhz=args.freq)
    except Exception as e:
        print(f"Error parsing files: {e}")
        return
        
    print("\\n--- Processed Molecule ---")
    print(f"Name: {mol.name}")
    for peak in mol.peaks:
        print(f"  δ {peak.shift_ppm:.2f} ({peak.multiplicity_name}, {peak.area:.0f}H) — {peak.label}")
        
    x_ppm = np.linspace(12, 0, 10000)
    y_total, y_individual = simulate_spectrum(x_ppm, mol)
    
    save_filename = f"NMR_G16_{mol.name}.png"
    plot_spectrum(x_ppm, mol, y_total, y_individual, save_filename=save_filename)
    print(f"\\n  ✓ Plot saved successfully as {save_filename}")
    # Don't show interactive plot if running in unattended mode
    # plt.show()

if __name__ == '__main__':
    main()
