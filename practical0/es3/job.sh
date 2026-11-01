make -j

./es3 1 0 0
python plot_orbital.py orbital1_0_0.dat
python plot_3Dorbital.py orbital3D1_0_0.dat
echo "Plotted 1s orbital"
# gnuplot -e "infile='orbital1_0_0.dat'; outfile='orbital1_0_0.png'" draw_orbital.gnu

./es3 2 0 0
python plot_orbital.py orbital2_0_0.dat
python plot_3Dorbital.py orbital3D2_0_0.dat
echo "Plotted 2s orbital"
# gnuplot -e "infile='orbital2_0_0.dat'; outfile='orbital2_0_0.png'" draw_orbital.gnu

./es3 2 1 0
python plot_orbital.py orbital2_1_0.dat
python plot_3Dorbital.py orbital3D2_1_0.dat
echo "Plotted 2p_z orbital"
# gnuplot -e "infile='orbital2_1_0.dat'; outfile='orbital2_1_0.png'" draw_orbital.gnu

./es3 2 1 1
python plot_orbital.py orbital2_1_1.dat
python plot_3Dorbital.py orbital3D2_1_1.dat
echo "Plotted 2p_x orbital"
# gnuplot -e "infile='orbital2_1_1.dat'; outfile='orbital2_1_1.png'" draw_orbital.gnu

./es3 2 1 -1
python plot_orbital.py orbital2_1_-1.dat
python plot_3Dorbital.py orbital3D2_1_-1.dat
echo "Plotted 2p_y orbital"
# gnuplot -e "infile='orbital2_1_-1.dat';

python plot_orbital_grid.py
python plot_3Dorbital_grid.py
# gnuplot -e "infile='orbital2_1_-1.dat'; outfile='orbital2_1_-1.png'" draw_orbital.gnu