#include <cmath>
#include <iostream>
#include <gsl/gsl_integration.h>
#include <gsl/gsl_math.h>

struct Params {
    double r0{0};
    double drdt{0};
};

double f(double theta, void* params)
{
    Params* p = static_cast<Params*>(params);
    auto base = gsl_pow_2(p->drdt * theta + p->r0);
    auto delta = gsl_pow_2(p->drdt);
    return std::sqrt(base + delta);
}

int main(int argc, char* argv[])
{
    if (argc < 4) {
        std::cout << "Usage: " << argv[0]
                  << " [start-radius] [spirals] [spacing]" << std::endl;
        return EXIT_FAILURE;
    }

    // Parameters
    Params params;
    params.r0 = std::stod(argv[1]);
    auto spirals = std::stod(argv[2]);
    auto spacing = std::stod(argv[3]);
    params.drdt = spacing / (2 * M_PI);
    double a = 0;
    double b = spirals * 2 * M_PI;

    // Integrate
    gsl_function F;
    F.function = &f;
    F.params = &params;

    auto w = gsl_integration_workspace_alloc(1000);
    double result, error;
    gsl_integration_qags(&F, a, b, 0, 1e-7, 1000, w, &result, &error);

    std::cout << "Spiral Length: " << result << std::endl;
    std::cout << "Error: " << error << std::endl;
}
