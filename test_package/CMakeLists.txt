cmake_minimum_required(VERSION 3.20)

project(nest2dle_testpackage)
find_package(nest2dle REQUIRED)

add_executable(test main.cpp)

target_link_libraries(test PRIVATE nest2dle::nest2dle)