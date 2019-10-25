cmake_minimum_required(VERSION 3.14)
project(3d-utilities)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED true)

include(FetchContent)

FetchContent_Declare(
    libigl
    URL https://github.com/libigl/libigl/archive/c645aac.tar.gz
)
FetchContent_MakeAvailable(libigl)

# Spiral length
find_package(GSL)
if(GSL_FOUND)
    add_executable(spiral-length SpiralLength.cpp)
    target_link_libraries(spiral-length igl GSL::gsl)
endif()

# Iterative diff
find_package(CGAL NO_MODULE)
find_package(Eigen3 3.3 NO_MODULE)
if(CGAL_FOUND AND Eigen3_FOUND)
    add_executable(overhang-remover OverhangRemover.cpp)
    target_include_directories(overhang-remover
        PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${INSTALL_INCLUDE_DIR}>
    )
    target_link_libraries(overhang-remover igl CGAL::CGAL Eigen3::Eigen)
endif()
