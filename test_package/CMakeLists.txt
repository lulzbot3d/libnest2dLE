cmake_minimum_required(VERSION 3.20)

project(nest2dle_testpackage)
find_package(nest2d REQUIRED)

add_executable(test main.cpp)

target_link_libraries(test PRIVATE nest2d::nest2d)