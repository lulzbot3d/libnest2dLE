find_package(Catch2 REQUIRED)

include(CTest)
include(Catch)

set(SRC_TEST
        test.cpp
        ../tools/svgtools.hpp
        ../tools/printer_parts.hpp
        ../tools/printer_parts.cpp
        )

add_executable(tests ${SRC_TEST})
target_link_libraries(tests PUBLIC nest2d Catch2::Catch2WithMain)

catch_discover_tests(tests
        TEST_PREFIX
        "unittests."
        OUTPUT_DIR
        .
        OUTPUT_PREFIX
        "unittests."
        OUTPUT_SUFFIX
        .xml)

