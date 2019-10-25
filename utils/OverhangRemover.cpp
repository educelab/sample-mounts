#include <chrono>
#include <cmath>
#include <iostream>
#include <sstream>
#include <string>

#include <igl/copyleft/cgal/CSGTree.h>
#include <igl/read_triangle_mesh.h>
#include <igl/write_triangle_mesh.h>

namespace iglcgal = igl::copyleft::cgal;
using namespace Eigen;

struct Mesh {
    MatrixXd v;
    MatrixXi f;
};

std::chrono::time_point<std::chrono::system_clock> start, end;

void StartTimer();
void StopTimer();
std::string TimerDuration();
std::string CurrentTime();
Mesh ClippingBox(const Vector3d& min, const Vector3d& mid, const Vector3d& max);
MatrixXd PreviewMode(MatrixXd liningVs, Vector3d min, Vector3d dims);

double overhangStepSize = 0.5;

int main(int argc, char* argv[])
{
    if (argc < 5) {
        std::cout << "Usage: " << argv[0];
        std::cout << " [lining-wall.stl]";
        std::cout << " [lining.stl]";
        std::cout << " [output-prefix]";
        std::cout << " [l/r]";
        std::cout << " {[rotation angle (degs)] [p (enable preview)]}";
        std::cout << std::endl;
        return EXIT_FAILURE;
    }

    std::string shellPath = argv[1];
    std::string liningPath = argv[2];
    std::string outputPrefix = argv[3];
    std::string side = argv[4];

    if(side != "l" && side != "r") {
      std::cout << "Unrecognized side option: " << side << std::endl;
      return EXIT_FAILURE;
    }

    // read the meshes
    MatrixXd v1, v2;
    MatrixXi f1, f2;
    igl::read_triangle_mesh(shellPath, v1, f1);
    igl::read_triangle_mesh(liningPath, v2, f2);

    // apply rotation
    if (argc > 5) {
        std::cout << CurrentTime() << " :: Rotating..." << std::flush;
        StartTimer();
        auto angle = std::stod(argv[5]) * M_PI / 180.0;
        AngleAxis<double> r(angle, Vector3d{0, 0, 1});
        v1.transpose() = r.toRotationMatrix() * v1.transpose();
        v2.transpose() = r.toRotationMatrix() * v2.transpose();
        StopTimer();
        std::cout << " (" << TimerDuration() << ")" << std::endl;
    }

    // preview mode
    auto preview{false};
    if(argc > 6) {
        preview = std::stoi(argv[6]) == 1;
    }

    // Get dimensions of the models
    Vector3d wallMin = v1.colwise().minCoeff();
    Vector3d wallMax = v1.colwise().maxCoeff();
    Vector3d wallMid = (wallMin + wallMax) / 2.0;
    Vector3d wallDims = wallMax - wallMin;

    Vector3d liningMin = v2.colwise().minCoeff();
    Vector3d liningMax = v2.colwise().maxCoeff();
    Vector3d liningMid = (liningMax + liningMin) / 2.0;
    Vector3d liningDims = wallMax - wallMin;

    // Do preview mode and exit
    if(preview) {
       std::cout << CurrentTime() << " :: Running preview mode..." << std::flush;
       StartTimer();
       auto v = PreviewMode(v2, wallMin, wallDims);
       igl::write_triangle_mesh(outputPrefix + "_lining_preview.ply", v, MatrixXi());
       igl::write_triangle_mesh(outputPrefix + "_liningwall_preview.stl", v1, f1);
       StopTimer();
       std::cout << " (" << TimerDuration() << ")" << std::endl;
       return EXIT_SUCCESS;
    }

    // Difference block
    auto box = ClippingBox(wallMin, wallMid, wallMax);
    if(side == "r") {
        VectorXd translate(3);
        translate << 0, -wallDims[1]/2, 0;
        box.v.rowwise() += translate.transpose();
    }

    ///// Overhang removal /////
    iglcgal::CSGTree csg;

    // Remove half of the wall model
    std::cout << CurrentTime() << " :: Splitting the lining wall model..."
              << std::flush;
    StartTimer();
    csg = {{v1, f1}, {box.v, box.f}, "m"};
    v1 = csg.cast_V<MatrixXd>();
    f1 = csg.F();
    StopTimer();
    std::cout << " (" << TimerDuration() << ")" << std::endl;

    // Remove half of the lining model
    std::cout << CurrentTime() << " :: Splitting the lining model..."
              << std::flush;
    StartTimer();
    csg = {{v2, f2}, {box.v, box.f}, "m"};
    v2 = csg.cast_V<MatrixXd>();
    f2 = csg.F();
    StopTimer();
    std::cout << " (" << TimerDuration() << ")" << std::endl;

    // Reset the CSG tree
    csg = {v2, f2};

    // Translation vector
    VectorXd translate(3);
    if(side == "r") {
      translate << 0, -overhangStepSize, 0;
    } else {
      translate << 0, overhangStepSize, 0;
    }

    // Union all of the overhang positions
    auto iters = std::max(
        static_cast<size_t>(std::ceil(wallDims[1] * 0.5 / overhangStepSize)),
        size_t(1));
    for (size_t i = 1; i < iters; i++) {
        std::cout << CurrentTime() << " :: Union iteration " << i << "/"
                  << iters - 1 << std::flush;
        StartTimer();
        v2.rowwise() += translate.transpose();
        csg = {csg, {v2, f2}, "u"};
        StopTimer();
        std::cout << " (" << TimerDuration() << ")" << std::endl;
    }

    // Do the final difference
    std::cout << CurrentTime() << " :: Removing the lining from the wall..."
              << std::flush;
    StartTimer();
    csg = {{v1, f1}, csg, "m"};
    StopTimer();
    std::cout << " (" << TimerDuration() << ")" << std::endl;

    std::cout << CurrentTime() << " :: Writing output..." << std::flush;
    StartTimer();
    igl::write_triangle_mesh(
        outputPrefix + "_" + side + "_final.stl", csg.cast_V<MatrixXd>(), csg.F());
    StopTimer();
    std::cout << " (" << TimerDuration() << ")" << std::endl;
    return EXIT_SUCCESS;
}

void StartTimer() { start = std::chrono::system_clock::now(); }

void StopTimer() { end = std::chrono::system_clock::now(); }

std::string TimerDuration()
{
    std::stringstream ss;
    std::chrono::duration<double> elapsed = end - start;
    ss << elapsed.count() << "s";
    return ss.str();
}

std::string CurrentTime()
{
    auto now = std::chrono::system_clock::now();
    auto in_time_t = std::chrono::system_clock::to_time_t(now);
    std::stringstream ss;
    ss << std::put_time(std::localtime(&in_time_t), "%Y-%m-%d %X");
    return ss.str();
}

// Difference block
Mesh ClippingBox(const Vector3d& min, const Vector3d& mid, const Vector3d& max)
{

    Mesh mesh{{8, 3}, {12, 3}};
    // clang-format off
    mesh.v <<
        min[0], mid[1], min[2], // 0
        min[0], max[1], min[2], // 1
        min[0], max[1], max[2], // 2
        min[0], mid[1], max[2], // 3
        max[0], mid[1], min[2], // 4
        max[0], max[1], min[2], // 5
        max[0], max[1], max[2], // 6
        max[0], mid[1], max[2]; // 7

    mesh.f <<
        0, 2, 1,
        0, 3, 2,
        1, 6, 5,
        1, 2, 6,
        5, 7, 4,
        5, 6, 7,
        4, 3, 0,
        4, 7, 3,
        3, 6, 2,
        3, 7, 6,
        0, 1, 5,
        0, 5, 4;
    // clang-format on

    return mesh;
}

MatrixXd PreviewMode(MatrixXd liningVs, Vector3d min, Vector3d dims)
{
    // Move lining to minimum Y
    VectorXd translate(3);
    translate << 0, min[1], 0;
    liningVs.rowwise() += translate.transpose();

    // Setup the iterative translation
    translate[1] = overhangStepSize;

    // get number of iterations
    auto iters = std::max(
        static_cast<size_t>(std::ceil(dims[1] / overhangStepSize)), size_t(1));

    // Setup output vertex list
    std::vector<MatrixXd> all;

    // Run iterations
    for (size_t i = 0; i < iters; i++) {
      all.push_back(liningVs);
      liningVs.rowwise() += translate.transpose();
    }

    // Result matrix
    MatrixXd result{all.size() * liningVs.rows(), 3};
    result.Zero(all.size() * liningVs.rows(), 3);
    size_t y{0};
    for(const auto& m : all) {
      result.block(y, 0, m.rows(), m.cols()) = m;
      y += m.rows();
    }

    return result;
}
