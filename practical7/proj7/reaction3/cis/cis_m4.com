%nprocshared=8
%mem=16GB
%chk=./cis_m4.chk

#p wB97XD/def2TZVP Opt Freq

CIS-HCOOH optimization

0 1
O
C 1 r1
O 2 r2 1 a1
H 3 r3 2 a2 1 0.0
H 2 r4 1 a3 3 180.0

r1=1.21
r2=1.34
r3=0.96
r4=1.09
a1=124.0
a2=106.0
a3=124.0

