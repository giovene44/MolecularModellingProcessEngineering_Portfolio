%nprocshared=16
%mem=16GB
%chk=./nh3_m062x_cc-pvtz.chk

#p M062X/cc-pVTZ Opt Freq

NH3 optimization M062X cc-pVTZ

0 1
N
H  1  r2
H  1  r3  2  a3
H  1  r4  2  a4  3  d4

r2=1.0
r3=1.0
r4=1.0
a3=110.0
a4=110.0
d4=120.0

