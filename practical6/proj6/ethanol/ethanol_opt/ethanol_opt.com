%nprocshared=24
%mem=300Gb
%chk=ethanol_opt.chk
# b3lyp/6-311+g(d,p) opt freq
 
ETHANOL Geometry Optimization and Frequencies

0  1
C
H  1  r2
H  1  r3  2  a3
C  1  r4  2  a4  3  d4
H  1  r5  2  a5  3  d5
H  4  r6  1  a6  2  d6
H  4  r7  1  a7  2  d7
O  4  r8  1  a8  2  d8
H  8  r9  4  a9  1  d9

r2= 1.0700
r3= 1.0700
a3= 109.47
r4= 1.5000
a4= 109.47
d4= 120.00
r5= 1.0700
a5= 109.47
d5= 240.00
r6= 1.0700
a6= 109.47
d6= 300.00
r7= 1.0700
a7= 109.47
d7=  60.00
r8= 1.3800
a8= 109.47
d8= 180.00
r9= 0.9500
a9= 109.47
d9=  60.00

