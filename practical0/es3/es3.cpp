#include <cmath>
#include <stdexcept>
#include <complex>
#include <fstream>
#include <iostream>

double double_factorial(int n)
{
    if (n <= 0)
    {
        return 1;
    }
    double result = 1;
    for (int i = n; i > 0; i -= 2)
    {
        result *= i;
    }
    return result;
}

class Orbital
{
public:
    int n;
    int l;
    int m;
    double const a0 = 1.0; // Bohr radius

    double compute_associated_Laguerre(int k, int a, double x)
    {
        // Basic mathematical Laguerre L_k^a(x) using recurrence
        double L_prev = 1.0;
        if (k == 0)
        {
            // According to the table: L_a^a(x) = -a!
            // We calculate the factorial and apply the sign
            double fact = 1.0;
            for (int i = 1; i <= a; ++i)
                fact *= i;
            return -fact;
        }

        double L_curr = 1.0 + a - x;
        if (k > 1)
        {
            for (int i = 1; i < k; i++)
            {
                double L_next = ((2.0 * i + 1.0 + a - x) * L_curr - (i + a) * L_prev) / (i + 1.0);
                L_prev = L_curr;
                L_curr = L_next;
            }
        }

        // Apply the conversion factor: Table_L = (-1)^k * (k+a)! * Math_L
        // Specifically, the table shows L_{n+k}^k(x) where n is our 'k' (degree)
        // and k is our 'a' (alpha).
        double factor = 1.0;
        for (int i = 1; i <= (k + a); ++i)
            factor *= i;

        if (k % 2 != 0)
            factor *= -1.0;

        return factor * L_curr;
    }

    double compute_associated_Legendre(int l, int m, double x)
    {
        m = std::abs(m);
        if (m > l)
            return 0.0;

        double p_m_m = 1.0;
        double somx2 = std::sqrt((1.0 - x) * (1.0 + x));
        double fact = 1.0;
        for (int i = 1; i <= m; i++)
        {
            p_m_m *= -fact * somx2;
            fact += 2.0;
        }

        if (l == m)
            return p_m_m;

        double p_m_m_1 = x * (2 * m + 1) * p_m_m;
        if (l == m + 1)
            return p_m_m_1;

        double p_m_l = 0;
        for (int i = m + 2; i <= l; i++)
        {
            p_m_l = (x * (2 * i - 1) * p_m_m_1 - (i + m - 1) * p_m_m) / (i - m);
            p_m_m = p_m_m_1;
            p_m_m_1 = p_m_l;
        }
        return p_m_l;
    }

    double compute_R_nl(int n, int l, int m, double r)
    {
        double rho = 2.0 * r / (n * a0);

        int degree = n - l - 1;
        int alpha = 2 * l + 1;
        double laguerre = compute_associated_Laguerre(degree, alpha, rho);

        double normalization = std::sqrt(std::tgamma(n - l) / (2.0 * n * std::tgamma(n + l + 1) * std::tgamma(n + l + 1) * std::tgamma(n + l + 1)));
        double radial_pow = std::pow(2.0 / (n * a0), l + 1.5) * std::pow(r, l);
        double radial_exp = std::exp(-r / (n * a0));
        return -normalization * radial_pow * radial_exp * laguerre;
    }

    std::complex<double> compute_Y_lm(int l, int m, double theta, double phi)
    {
        double normalization = std::sqrt((2.0 * l + 1) / (4.0 * M_PI) * (std::tgamma(l - std::abs(m) + 1)) / (std::tgamma(l + std::abs(m) + 1)));


        double legendre = std::pow(-1, m) * compute_associated_Legendre(l, std::abs(m), std::cos(theta));
        std::complex<double> phase = std::exp(std::complex<double>(0, m * phi));

        if (m==1){
            if(std::abs((legendre) - std::sin(theta)) > 1e-6)
            {
                std::cerr << "Legendre mismatch for m = " << m << ": " << legendre << " vs " << std::sin(theta) << "\n";
            }

            if(std::abs(normalization - std::sqrt(3.0 / (8.0 * M_PI))) > 1e-6)
            {
                std::cerr << "Normalization mismatch for m = " << m << ": " << normalization << " vs " << std::sqrt(3.0 / (8.0 * M_PI)) << "\n";
            }

            if (std::abs(phase) - std::abs(std::exp(std::complex<double>(0, phi))) > 1e-6)
            {
                std::cerr << "Phase mismatch for m = " << m << ": " << phase << " vs " << std::exp(std::complex<double>(0, phi)) << "\n";
            }
        }

        return normalization * legendre * phase;
    }

    Orbital(int n, int l, int m)
    {
        if (l >= n)
        {
            throw std::invalid_argument("l must be less than n");
        }
        if (m < -l || m > l)
        {
            throw std::invalid_argument("m must be between -l and l");
        }
        this->n = n;
        this->l = l;
        this->m = m;
    }

    void draw_xy_density(double size, int resolution, const std::string &filename)
    {
        std::ofstream out(filename);
        double step = (2.0 * size) / resolution;

        for (int i = 0; i <= resolution; ++i)
        {
            double x = -size + i * step;
            for (int j = 0; j <= resolution; ++j)
            {
                double y = -size + j * step;

                // Convert to Spherical
                double r = std::sqrt(x * x + y * y);
                double theta = M_PI / 2.0; // xy-plane
                double phi = std::atan2(y, x);

                // Calculate Wavefunction Components
                double R = compute_R_nl(n, l, m, r);

                std::complex<double> Y = compute_Y_lm(l, m, theta, phi);
                double density = R * R * std::abs(Y) * std::abs(Y);

                out << x << " " << y << " " << density << "\n";
            }
            // out << "\n"; // Gnuplot needs a blank line between rows for pm3d
        }
        out.close();
    }

    void draw_xy_psi(double size, int resolution, const std::string &filename)
    {
        std::ofstream out(filename);
        double step = (2.0 * size) / resolution;

        for (int i = 0; i <= resolution; ++i)
        {
            double x = -size + i * step;
            for (int j = 0; j <= resolution; ++j)
            {
                double y = -size + j * step;

                // Convert to Spherical
                double r = std::sqrt(x * x + y * y);
                double theta = M_PI / 2.0; // xy-plane
                double phi = std::atan2(y, x);

                // Calculate Wavefunction Components
                double R = compute_R_nl(n, l, m, r);

                std::complex<double> Y = compute_Y_lm(l, m, theta, phi);

                if (l!=0 && m > 0)
                {
                    double real_psi = sqrt(2) * R * Y.real();
                    out << x << " " << y << " " << real_psi << "\n";
                }
                else if (l!=0 && m < 0)
                {
                    double imag_psi = sqrt(2) * R * Y.imag();
                    out << x << " " << y << " " << imag_psi << "\n";
                }
                else
                {
                    out << x << " " << y << " " << R * Y.real() << "\n";
                }

            }
            // out << "\n"; // Gnuplot needs a blank line between rows for pm3d
        }
        out.close();
    }

    void draw_3D_psi(double size, int resolution, const std::string &filename)
    {
        std::ofstream out(filename);
        double step = (2.0 * size) / resolution;

        for (int i = 0; i <= resolution; ++i)
        {
            double x = -size + i * step;
            for (int j = 0; j <= resolution; ++j)
            {
                double y = -size + j * step;

                for (int k = 0; k <= resolution; ++k)
                {
                    double z = -size + k * step;

                    // Convert to Spherical
                    double r = std::sqrt(x * x + y * y + z * z);
                    double theta = std::acos(z / r);
                    double phi = std::atan2(y, x);

                    // Calculate Wavefunction Components
                    double R = compute_R_nl(n, l, m, r);
                    std::complex<double> Y = compute_Y_lm(l, m, theta, phi);
                    
                    double psi_value;
                    if (l!=0 && m > 0)
                    {
                        psi_value = sqrt(2) * R * Y.real();
                    }
                    else if (l!=0 && m < 0)
                    {
                        psi_value = sqrt(2) * R * Y.imag();
                    }
                    else
                    {
                        psi_value = R * Y.real();
                    }

                    if (std::isnan(psi_value)) psi_value = 0.0;
                    out << x << " " << y << " " << z << " " << psi_value << "\n";
                }
            }
        }
        out.close();
    }

    bool verify_orbital(double size, int resolution, auto exact_R, auto exact_F)
    {
        double step = (2.0 * size) / resolution;
        bool all_passed = true;
        for (int i = 0; i <= resolution; ++i)
        {
            double x = -size + i * step;
            for (int j = 0; j <= resolution; ++j)
            {
                double y = -size + j * step;

                // Convert to Spherical
                double r = std::sqrt(x * x + y * y);
                double theta = M_PI / 2.0; // xy-plane
                double phi = std::atan2(y, x);

                // Calculate Wavefunction Components
                double R = compute_R_nl(n, l, m, r);

                if (std::abs(R - exact_R(r)) > 1e-6)
                {   
                    all_passed = false;
                    std::cerr << "R mismatch at r = " << r << ": " << R << " vs " << exact_R(r) << "\n";
                }

                std::complex<double> Y = compute_Y_lm(l, m, theta, phi);
                if (std::abs(Y - exact_F(theta, phi)) > 1e-6)
                {   
                    all_passed = false;
                    std::cerr << "Y mismatch at (theta, phi) = (" << theta << ", " << phi << "): " << Y << " vs " << exact_F(theta, phi) << "\n";
                }

                double density = R * R * std::abs(Y) * std::abs(Y);
                if (std::abs(density - exact_R(r) * exact_R(r) * std::abs(exact_F(theta, phi)) * std::abs(exact_F(theta, phi))) > 1e-6)
                {   
                    all_passed = false;
                    std::cerr << "Density mismatch at (r, theta, phi) = (" << r << ", " << theta << ", " << phi << "): " << density << " vs " << exact_R(r) * exact_R(r) * std::abs(exact_F(theta, phi)) * std::abs(exact_F(theta, phi)) << "\n";
                }
            }
        }
        return all_passed;
    }
};

int main(int argc, char *argv[])
{
    if (argc != 4 && argc != 1)
    {
        std::cerr << "Usage: " << argv[0] << " n l m\n or " << argv[0] << "\n";
        return 1;
    }

    if (argc == 4)
    {
        int n = std::stoi(argv[1]);
        int l = std::stoi(argv[2]);
        int m = std::stoi(argv[3]);
        std::string output_file = "orbital" + std::to_string(n) + "_" + std::to_string(l) + "_" + std::to_string(m) + ".dat";
        std::string output_3Dfile = "orbital3D" + std::to_string(n) + "_" + std::to_string(l) + "_" + std::to_string(m) + ".dat";
        try
        {
            Orbital orbital(n, l, m);
            orbital.draw_xy_psi(5.0*(1+l), 1000, output_file);
            orbital.draw_3D_psi(5.0*(1+l), 100, output_3Dfile);
        }
        catch (const std::exception &e)
        {
            std::cerr << "Error: " << e.what() << "\n";
            return 1;
        }
    }

    else if (argc == 1)
    {
        std::cout << "Running verification for 1s, 2s, 2px, 2py, 2pz orbitals...\n";
        Orbital one_s(1, 0, 0);
        bool one_s_passed = one_s.verify_orbital(5.0, 100, [](double r) {
            double a0 = 1.0;
            return -std::sqrt(0.5) * std::pow(2.0 / a0, 1.5) * std::exp(-r / a0) * (-1);
        }, [](double theta, double phi) {
            return std::complex<double>(1.0 / std::sqrt(4.0 * M_PI), 0);
        });

        std::cout << "1s orbital: " << (one_s_passed ? "PASSED" : "FAILED") << "\n";

        Orbital two_s(2, 0, 0);
        bool two_s_passed = two_s.verify_orbital(10.0, 100, [](double r) {
            double a0 = 1.0;
            return -std::sqrt(1.0 / 32.0) * std::pow(1 / (a0), 1.5) * std::exp(-r / (2 * a0)) * (-2) * (2 - r / a0);
        }, [](double theta, double phi) {
            return std::complex<double>(1.0 / std::sqrt(4.0 * M_PI), 0);
        });
        std::cout << "2s orbital: " << (two_s_passed ? "PASSED" : "FAILED") << "\n";

        Orbital two_p_x(2, 1, 0);
        bool two_p_0_passed = two_p_x.verify_orbital(10.0, 100, [](double r) {
            double a0 = 1.0;
            return -std::sqrt(1.0 / 864.0) * std::pow(1 / (a0), 2.5) * r * std::exp(-r / (2 * a0)) * -(3*2);
        }, [](double theta, double phi) {
            return std::complex<double>(std::sqrt(3.0 / (4.0 * M_PI)) * std::cos(theta), 0);
        });
        std::cout << "2px orbital: " << (two_p_0_passed ? "PASSED" : "FAILED") << "\n";

        Orbital two_p_y(2, 1, 1);
        bool two_p_1_passed = two_p_y.verify_orbital(10.0, 100, [](double r) {
            double a0 = 1.0;
            return -std::sqrt(1.0 / 864.0) * std::pow(1 / (a0), 2.5) * r * std::exp(-r / (2 * a0)) * -(3*2);
        }, [](double theta, double phi) {
            return std::sqrt(3.0 / (8.0 * M_PI)) * std::sin(theta) * std::exp(std::complex<double>(0, phi));
        });
        std::cout << "2py orbital: " << (two_p_1_passed ? "PASSED" : "FAILED") << "\n";

        Orbital two_p_z(2, 1, -1);
        bool two_p_neg1_passed = two_p_z.verify_orbital(10.0, 100, [](double r) {
            double a0 = 1.0;
            return -std::sqrt(1.0 / 864.0) * std::pow(1 / (a0), 2.5) * r * std::exp(-r / (2 * a0)) * -(3*2);
        }, [](double theta, double phi) {
            return std::sqrt(3.0 / (8.0 * M_PI)) * std::sin(theta) * std::exp(std::complex<double>(0, -phi));
        });
        std::cout << "2pz orbital: " << (two_p_neg1_passed ? "PASSED" : "FAILED") << "\n";
    }

    return 0;
}