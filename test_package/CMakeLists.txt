cmake_minimum_required(VERSION 3.13)

project(Libnest2D_example)
set(CMAKE_CXX_STANDARD 17)
find_package(nest2d REQUIRED)

add_executable(test main.cpp)

target_link_libraries(test PRIVATE nest2d::nest2d)
target_include_directories(test PRIVATE ${nest2d_INCLUDE_DIRS})