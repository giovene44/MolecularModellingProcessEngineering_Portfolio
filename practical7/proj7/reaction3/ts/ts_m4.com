%nprocshared=8
%mem=16GB
%chk=./ts_m4.chk

#p wB97XD/def2TZVP Opt=(TS,CalcFC,MaxCycles=50) SCF=XQC Freq

TS optimization - cis to trans formic acid

0 1
C      0.000000    0.000000    0.000000
O      0.000000    0.000000    1.200000
O      1.267000    0.000000   -0.500000
H     -1.090000    0.000000   -0.540000
H      1.267000    0.970000   -0.100000

