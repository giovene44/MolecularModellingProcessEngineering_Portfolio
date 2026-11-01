%chk=tmp
%mem=100MB
%NProcShared=16

#P B3LYP/6-31+g(d,p) opt=z-matrix nosym freq Pop=Full gfinput

Ethane Scan - Fixed Z-Matrix

0 1
C
C  1  r2
H  1  r3  2  a3
H  1  r4  2  a4  3  d4
H  1  r5  2  a5  3  d5
H  2  r6  1  a6  3  d6
H  2  r7  1  a7  3  d7
H  2  r8  1  a8  3  d8

r2= 1.5121
r3= 1.0941
a3= 110.57
r4= 1.0941
a4= 110.57
d4= 120.00
r5= 1.0941
a5= 110.57
d5= 240.00
d6= 300.00 S 6 10.0
r6= 1.0941
a6= 110.57
r7= 1.0941
a7= 110.57
d7= 60.00
r8= 1.0941
a8= 110.57
d8= 180.00
