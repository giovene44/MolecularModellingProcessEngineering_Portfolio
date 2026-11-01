import pandas as pd
import os
# Read the CSV file
csv_files = [f for f in os.listdir() if f.endswith('.csv')]
accuracy_map = {
    ('ccsdt', 'aug-cc-pvtz'): 1,
    ('ccsdt', 'cc-pvtz'): 2,
    ('ccsdt', 'aug-cc-pvdz'): 3,
    ('ccsdt', '6-311plusg2dp'): 4,
    ('ccsdt', 'cc-pvdz'): 5,
    ('ccsdt', '6-31gdp'): 6,
    ('b2plypd3', 'aug-cc-pvtz'): 7,
    ('b2plypd3', 'cc-pvtz'): 8,
    ('b2plypd3', 'aug-cc-pvdz'): 9,
    ('b2plypd3', '6-311plusg2dp'): 10,
    ('b2plypd3', 'cc-pvdz'): 11,
    ('b2plypd3', '6-31gdp'): 12,
    ('mp2', 'aug-cc-pvtz'): 13,
    ('mp2', 'cc-pvtz'): 14,
    ('mp2', 'aug-cc-pvdz'): 15,
    ('mp2', '6-311plusg2dp'): 16,
    ('mp2', 'cc-pvdz'): 17,
    ('mp2', '6-31gdp'): 18,
    ('m062x', 'aug-cc-pvtz'): 19,
    ('m062x', 'cc-pvtz'): 20,
    ('m062x', 'aug-cc-pvdz'): 21,
    ('m062x', '6-311plusg2dp'): 22,
    ('m062x', 'cc-pvdz'): 23,
    ('m062x', '6-31gdp'): 24,
    ('b3lyp', 'aug-cc-pvtz'): 25,
    ('b3lyp', 'cc-pvtz'): 26,
    ('b3lyp', 'aug-cc-pvdz'): 27,
    ('b3lyp', '6-311plusg2dp'): 28,
    ('b3lyp', 'cc-pvdz'): 29,
    ('b3lyp', '6-31gdp'): 30,
    ('hf', 'aug-cc-pvtz'): 31,
    ('hf', 'cc-pvtz'): 32,
    ('hf', 'aug-cc-pvdz'): 33,
    ('hf', '6-311plusg2dp'): 34,
    ('hf', 'cc-pvdz'): 35,
    ('hf', '6-31gdp'): 36
}

for df_files in csv_files:
    df = pd.read_csv(df_files, sep=';', engine='python', decimal=',')
    df.columns = df.columns.str.strip()

    df['Theory'] = df['Theory'].astype(str).str.strip().str.lower()
    df['Basis Set'] = (
        df['Basis Set']
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df['Accuracy_Rank'] = list(zip(df['Theory'], df['Basis Set']))
    df['Accuracy_Rank'] = df['Accuracy_Rank'].map(accuracy_map)

    df_sorted = df.sort_values('Accuracy_Rank', na_position='last').drop(columns=['Accuracy_Rank']).reset_index(drop=True)

    print(df_sorted)
    # Save the sorted data
    output_file = f"{df_files}"

    print(f"Sorted data saved to {output_file}")
    df_sorted.to_csv(output_file, index=False, sep=';', decimal=',')