#!/bin/bash
module load python/3.11.6--gcc--8.4.1
source ~/bin/py3.11/bin/activate

# Ensure an input directory is passed as an argument
if [ -z "$1" ]; then
    echo "Error: Missing input directory."
    echo "Usage: $0 /path/to/input_dir"
    exit 1
fi

# Resolve absolute path of the input directory
INPUT_DIR=$(realpath "$1")

# Global variable to pass job IDs out of the modifier function
LATEST_JOB_ID=""

# Helper function to monitor the Slurm queue for a specific job ID
wait_for_job() {
    local job_id=$1
    echo "Job $job_id submitted. Monitoring queue..."
    while squeue -j "$job_id" 2>/dev/null | grep -q "$job_id"; do
        sleep 30
    done
    echo "Job $job_id has completed."
}

# Helper function to substitute the first line of an input file and submit it
modify_and_submit() {
    local inp_file=$1
    shift # Capture any remaining arguments to pass to sbatch

    if [ -f "$inp_file" ]; then
        echo "Modifying first line of $inp_file..."
        sed -i '1s/.*/! VERYTIGHTOPT FREQ GFN2-xTB VeryTightSCF/' "$inp_file"
        
        # Launch job and capture output
        JOB_OUT=$(sbatch orcarun "$inp_file" "$@")
        LATEST_JOB_ID=$(echo "$JOB_OUT" | awk '{print $4}')
        echo "Successfully launched Job ID: $LATEST_JOB_ID"
        
        # Wait for this specific job to finish
        wait_for_job "$LATEST_JOB_ID"
    else
        echo "Error: Input file '$inp_file' not found. Cannot proceed."
        exit 1
    fi
}

modify_and_submit_qmd() {
    local inp_file=$1
    shift # Capture any remaining arguments to pass to sbatch

    if [ -f "$inp_file" ]; then
        echo "Modifying first line of $inp_file..."
        sed -i '1s/.*/! MD GFN2-xTB VeryTightSCF/' "$inp_file"

        # Launch job and capture output
        JOB_OUT=$(sbatch orcarun "$inp_file" "$@")
        LATEST_JOB_ID=$(echo "$JOB_OUT" | awk '{print $4}')
        echo "Successfully launched Job ID: $LATEST_JOB_ID"

        # Wait for this specific job to finish
        wait_for_job "$LATEST_JOB_ID"
    else
        echo "Error: Input file '$inp_file' not found. Cannot proceed."
        exit 1
    fi
}

# 1) Change to input directory
echo "[DEBUG: DIR] Changing into target input directory: $INPUT_DIR"
cd "$INPUT_DIR" || exit 1

# Automatically detect the .xyz file in the directory
FILE_XYZ=$(ls *.xyz 2>/dev/null | head -n 1)
if [ -z "$FILE_XYZ" ]; then
    echo "Error: No .xyz file found in $INPUT_DIR"
    exit 1
fi
FILE_BASE="${FILE_XYZ%.xyz}"

echo "Target file detected: $FILE_XYZ (Base name: $FILE_BASE)"
echo "--------------------------------------------------"

# 3) Create and enter optimization directory
echo "[DEBUG: DIR] Creating and entering directory: 1_2_opt_freq"
mkdir -p 1_2_opt_freq && cd 1_2_opt_freq || exit 1

# 4) Copy the target xyz file
cp "../$FILE_XYZ" .

# 5) Run initial optimization input generation
echo "[DEBUG: RUN] Executing: python3.11 ../../bulma.py $FILE_XYZ --orca-opt"
python3.11 ../../bulma.py "$FILE_XYZ" --orca-opt

# 6 & 7 & 8) Substitute first line, submit, and track OPT Job ID
TARGET_INP="geom.inp"
if [ ! -f "$TARGET_INP" ] && [ -f "${FILE_BASE}.inp" ]; then
    TARGET_INP="${FILE_BASE}.inp"
fi
modify_and_submit "$TARGET_INP"
OPT_JOB_ID=$LATEST_JOB_ID

# 9) Return to root input directory
echo "[DEBUG: DIR] Leaving 1_2_opt_freq, returning up to: $INPUT_DIR"
cd ..

# 10) Create and enter relaunch directory
echo "[DEBUG: DIR] Creating and entering directory: 3_rilancio"
mkdir -p 3_rilancio && cd 3_rilancio || exit 1

# 11) Copy xyz file and locate geom.out INSIDE the specific JOB_ID directory
if [ -f "../1_2_opt_freq/$OPT_JOB_ID/geom.out" ]; then
    cp "../1_2_opt_freq/$OPT_JOB_ID/geom.out" ./orca_opt.out
elif [ -f "../1_2_opt_freq/$OPT_JOB_ID/${FILE_BASE}.out" ]; then
    cp "../1_2_opt_freq/$OPT_JOB_ID/${FILE_BASE}.out" ./orca_opt.out
else
    echo "Warning: Could not find optimization output file."
    exit 1
fi

# 12) Extract geometry
FILE_OPT="${FILE_BASE}_opt.xyz"
echo "[DEBUG: RUN] Executing: python3.11 ../../bulma.py orca_opt.out --extract-geo --geo-out $FILE_OPT"
python3.11 ../../bulma.py orca_opt.out --extract-geo --geo-out "$FILE_OPT"

# 13) Run frequency setup
echo "[DEBUG: RUN] Executing: python ../../bulma.py $FILE_OPT --orca-freq"
python ../../bulma.py "$FILE_OPT" --orca-freq

# 14 & 15) Substitute first line of geom_freq.inp, submit, and track FREQ Job ID
modify_and_submit "geom_freq.inp" "$FILE_XYZ"
FREQ_JOB_ID=$LATEST_JOB_ID

# 16) Move up and create Hessian directory
echo "[DEBUG: DIR] Leaving 3_rilancio, creating and entering directory: 4_hessian"
cd .. && mkdir -p 4_hessian && cd 4_hessian || exit 1

# 17) Copy the generated Hessian file from INSIDE the frequency JOB_ID directory
cp "../3_rilancio/$FREQ_JOB_ID/geom_freq.hess" .

# 18) Parse Hessian
echo "[DEBUG: RUN] Executing: python ../../bulma.py geom_freq.hess --orca-hess"
python ../../bulma.py geom_freq.hess --orca-hess

# 19) Move up and create initial velocities directory
echo "[DEBUG: DIR] Leaving 4_hessian, creating and entering directory: 5_initial_velocities"
cd .. && mkdir -p 5_initial_velocities && cd 5_initial_velocities || exit 1

# 20) Copy optimized geometry from 3_rilancio/JOB_ID/ and Hessian outputs
if [ -f "../3_rilancio/$FREQ_JOB_ID/$FILE_OPT" ]; then
    echo "[DEBUG] Found optimized structure as $FILE_OPT in 3_rilancio/$FREQ_JOB_ID/"
    cp "../3_rilancio/$FREQ_JOB_ID/$FILE_OPT" .
    OPT_XYZ="$FILE_OPT"
elif [ -f "../3_rilancio/$FREQ_JOB_ID/geom_freq.xyz" ]; then
    echo "[DEBUG] Found optimized structure as geom_freq.xyz in 3_rilancio/$FREQ_JOB_ID/"
    cp "../3_rilancio/$FREQ_JOB_ID/geom_freq.xyz" ./"$FILE_OPT"
    OPT_XYZ="$FILE_OPT"
else
    echo "Warning: Optimized structure not found in 3_rilancio/$FREQ_JOB_ID/."
    exit 1
fi
cp ../4_hessian/Hessian_flat.out .

# 21) Generate initial velocities using the optimized geometry
echo "[DEBUG: RUN] Executing: python3.11 ../../vegeta.py --xyz $OPT_XYZ -H Hessian_flat.out -o velocity_orca.xyz"
python3.11 ../../vegeta.py --xyz "$OPT_XYZ" -H Hessian_flat.out -o velocity_orca.xyz

# 22) Move up and create MD directory
echo "[DEBUG: DIR] Leaving 5_initial_velocities, creating and entering directory: 6_classical_dynamics"
cd .. && mkdir -p 6_classical_dynamics && cd 6_classical_dynamics || exit 1

# 23) Copy optimized geometry forward for MD
cp "../5_initial_velocities/$OPT_XYZ" .
cp "../5_initial_velocities/velocity_orca.xyz" .

# 24) Generate QMD inputs using optimized coordinates
echo "[DEBUG: RUN] Executing: python3.11 ../../bulma.py $OPT_XYZ --orca-qmd"
python3.11 ../../bulma.py "$OPT_XYZ" --orca-qmd

# 25 & 26) Substitute first line of the QMD input file and submit
QMD_INP="${OPT_XYZ%.xyz}_qmd.inp"
if [ ! -f "$QMD_INP" ] && [ -f "${FILE_BASE}_qmd.inp" ]; then
    QMD_INP="${FILE_BASE}_qmd.inp"
fi
modify_and_submit_qmd "$QMD_INP"
QMD_JOB_ID=$LATEST_JOB_ID

# 27) Parse QMD results
echo "[DEBUG: RUN] Executing: python ../../bulma.py dummy_input --parse-orca-qmd"
cp "$LATEST_JOB_ID/trajectory.xyz" .
cp "$LATEST_JOB_ID/velocity.xyz" .
python3.11 ../../bulma.py dummy_input --parse-orca-qmd

# 28) Move up and create spectra directory
echo "[DEBUG: DIR] Leaving 6_classical_dynamics, creating and entering directory: 7_classical_spectra"
cd .. && mkdir -p 7_classical_spectra && cd 7_classical_spectra || exit 1

# 29) Copy required outputs from dynamics and hessian runs
cp "../6_classical_dynamics/$QMD_JOB_ID/${FILE_BASE}_opt.xyz" . 2>/dev/null \
    || cp "../6_classical_dynamics/$QMD_JOB_ID/geom_opt.xyz" . \
    || cp "../6_classical_dynamics/$QMD_JOB_ID/${OPT_XYZ%.xyz}_opt.xyz" . 2>/dev/null

if [ ! -f "${FILE_BASE}_opt.xyz" ]; then
    LOCAL_OPT=$(ls *_opt.xyz 2>/dev/null | head -n 1)
    if [ -n "$LOCAL_OPT" ]; then cp "$LOCAL_OPT" "${FILE_BASE}_opt.xyz"; fi
fi

cp ../4_hessian/Hessian_flat.out .

if [ -f "../6_classical_dynamics/parsed_log_traj.xyz" ]; then
    cp "../6_classical_dynamics/parsed_log_traj.xyz" .
else
    cp "../6_classical_dynamics/$QMD_JOB_ID/parsed_log_traj.xyz" .
fi

# 30) Generate final plots
RUN_NIMBUS="flying_nimbus.py"
if [ -f "../../flying_nimbus.py" ]; then RUN_NIMBUS="../../flying_nimbus.py"; fi

echo "[DEBUG: RUN] Executing: python $RUN_NIMBUS --coord cart --plot --plot-dpi 600 --xyz ${FILE_BASE}_opt.xyz --hess Hessian_flat.out --traj parsed_log_traj.xyz --norm1"
python3.11 "$RUN_NIMBUS" --coord cart --plot --plot-dpi 600 --xyz "${FILE_BASE}_opt.xyz" --hess Hessian_flat.out --traj parsed_log_traj.xyz --norm1

echo "--------------------------------------------------"
echo "Workflow execution successfully finished!"
