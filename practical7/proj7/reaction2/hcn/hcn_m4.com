%nprocshared=8
%mem=16GB
%chk=./hcn_m4.chk

#p wB97XD/def2TZVP Opt Freq

HCN optimization

0 1
H
C  1  RCH
N  2  RCN  1  AHCN

RCH  = 1.065
RCN  = 1.153
AHCN = 180.0

