%nprocshared=8
%mem=16GB
%chk=./ch4_m4.chk

#p wB97XD/def2TZVP Opt Freq

CH4 optimization

0 1
C
H 1 R1
H 1 R1 2 A1
H 1 R1 2 A1 3 D1
H 1 R1 2 A1 3 D2

R1=1.09
A1=109.471
D1=120.0
D2=-120.0

