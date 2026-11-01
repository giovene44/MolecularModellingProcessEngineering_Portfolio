%nprocshared=8
%mem=16GB
%chk=ts_nh3_h_m062x_cc-pvtz.chk

#p M062X/cc-pVTZ Opt=(TS,CalcFC,NoEigenTest) Freq SCF=Tight

TS NH3 + H -> NH2 + H2

0 2
N          0.000000        0.000000        0.000000
H          0.000000        1.010000        0.000000
H          0.875000       -0.505000        0.000000
H          0.000000        0.000000        1.300000
H          0.000000        0.000000        2.200000

