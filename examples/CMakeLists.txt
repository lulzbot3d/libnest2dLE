cmake_minimum_required(VERSION 3.1)

project(Libnest2DLE_example)

message(STATUS "PREFIX PATH = ${CMAKE_PREFIX_PATH}")
find_package(Libnest2DLE QUIET)

if(NOT Libnest2DLE_FOUND)
    message(STATUS "No installed version of Libnest2D has been found in the system. Falling back to subproject mode...")
    add_subdirectory(${PROJECT_SOURCE_DIR}/../ ${CMAKE_BINARY_DIR}/Libnest2DLE-build)
    add_library(Libnest2DLE::libnest2dle ALIAS libnest2dle)
else()
    message(STATUS "Libnest2DLE was found in ${Libnest2DLE_DIR}")
endif()

add_executable(example ${PROJECT_SOURCE_DIR}/main.cpp
                       ${PROJECT_SOURCE_DIR}/../tools/svgtools.hpp
                       ${PROJECT_SOURCE_DIR}/../tools/printer_parts.cpp
                       ${PROJECT_SOURCE_DIR}/../tools/printer_parts.hpp
                       )

target_link_libraries(example Libnest2DLE::libnest2dle)
