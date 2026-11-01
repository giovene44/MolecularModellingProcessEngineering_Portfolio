%nprocshared=8
%mem=16GB
%chk=./ch3_m4.chk

#p wB97XD/def2TZVP Opt Freq

CH3 optimization

0 2
C
H 1 R1
H 1 R1 2 A1
H 1 R1 2 A1 3 D1

R1=1.07
A1=120.0
D1=180.0

