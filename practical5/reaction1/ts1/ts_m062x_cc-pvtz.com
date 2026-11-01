%nprocshared=8
%mem=16GB
%chk=ts_m062x_cc-pvtz.chk

#p M062X/cc-pVTZ Opt=(TS, CalcFC, NoEigenTest) Freq

Transition State optimization for CH4 + H -> CH3 + H2

0 2
C    0.000000    0.000000    0.000000
H    0.000000    1.040000   -0.280000
H    0.900000   -0.520000   -0.280000
H   -0.900000   -0.520000   -0.280000
H    0.000000    0.000000    1.380000
H    0.000000    0.000000    2.300000

