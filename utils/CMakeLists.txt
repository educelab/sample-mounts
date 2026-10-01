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
