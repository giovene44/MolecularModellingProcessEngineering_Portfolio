%chk=tmp
%mem=400MW
%NProcShared=16

#P B3LYP/6-31+g(d,p) opt=internal freq Pop=Full gfinput

Methane Optimization and Freq

0 1
C1
H2 C1 d1
H3 C1 d2 H2 a1
H4 C1 d3 H2 a2 H3 t1
H5 C1 d4 H2 a3 H3 t2

d1=1.09
a1=109.
t1=120.
d2=1.03
a2=110.
t2=-120.
d3=1.05
d4=1.1
a3=109.

