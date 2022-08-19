import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conans import tools
from conan.tools.files import AutoPackager, files

required_conan_version = ">=1.48.0"


class Nest2DConan(ConanFile):
    name = "nest2d"
    description = "2D irregular bin packaging and nesting library written in modern C++"
    topics = ("conan", "cura", "prusaslicer", "nesting", "c++", "bin packaging")
    settings = "os", "compiler", "build_type", "arch"
    build_policy = "missing"

    python_requires = "umbase/0.1.5@ultimaker/testing"
    python_requires_extend = "umbase.UMBaseConanfile"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tests": [True, False],
        "header_only": [True, False],
        "enable_testing": [True, False],
        "geometries": ["clipper", "boost"],
        "optimizer": ["nlopt", "optimlib"],
        "threading": ["std", "tbb", "omp", "none"]
    }
    default_options = {
        "shared": True,
        "tests": False,
        "fPIC": True,
        "header_only": False,
        "enable_testing": False,
        "geometries": "clipper",
        "optimizer": "nlopt",
        "threading": "std"
    }
    scm = {
        "type": "git",
        "subfolder": ".",
        "url": "auto",
        "revision": "auto"
    }

    def layout(self):
        cmake_layout(self)
        self.cpp.package.libs = ["nest2d"]

    def config_options(self):
        if self.options.header_only:
            del self.options.shared
        else:
            if self.options.shared or self.settings.compiler == "Visual Studio":
                del self.options.fPIC

    def configure(self):
        self.options["boost"].header_only = True
        if self.options.geometries == "clipper":
            self.options["clipper"].shared = True if self.options.header_only else self.options.shared
        self.options[str(self.options.optimizer)].shared = True if self.options.header_only else self.options.shared
        if self.options.threading == "tbb":
            self.options["tbb"].shared = True if self.options.header_only else self.options.shared
        if self.options.threading == "omp":
            self.options["llvm-openmp"].shared =True if self.options.header_only else self.options.shared

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)

    def build_requirements(self):
        if self.options.enable_testing:
            for req in self._um_data()["requirements_testing"]:
                self.tool_requires(req)

    def requirements(self):
        for req_option in [f"requirements_{self.options.geometries}", f"requirements_{self.options.optimizer}", f"requirements_{self.options.threading}"]:
            for req in self._um_data()[req_option]:
                self.requires(req)

    def generate(self):
        deps = CMakeDeps(self)
        if self.options.enable_testing:
            deps.build_context_activated = ["catch2"]
            deps.build_context_build_modules = ["catch2"]
        deps.generate()

        tc = CMakeToolchain(self)

        # Don't use Visual Studio as the CMAKE_GENERATOR
        if self.settings.compiler == "Visual Studio":
            tc.blocks["generic_system"].values["generator_platform"] = None
            tc.blocks["generic_system"].values["toolset"] = None

        tc.variables["HEADER_ONLY"] = self.options.header_only
        if not self.options.header_only:
            tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["ENABLE_TESTING"] = self.options.enable_testing
        tc.variables["GEOMETRIES"] = self.options.geometries
        tc.variables["OPTIMIZER"] = self.options.optimizer
        tc.variables["THREADING"] = self.options.threading

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        packager = AutoPackager(self)
        packager.run()

        # Remove the header files from options not used in this package
        if self.options.geometries != "clipper":
            files.rmdir(self, os.path.join(self.package_folder, "include", "libnest2d", "backends", "clipper"))
        if self.options.optimizer != "nlopt":
            files.rmdir(self, os.path.join(self.package_folder, "include", "libnest2d", "optimizers", "nlopt"))
        if self.options.optimizer != "optimlib":
            files.rmdir(self, os.path.join(self.package_folder, "include", "libnest2d", "optimizers", "optimlib"))

    def package_info(self):
        if not self.options.header_only:
            self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.defines.append(f"LIBNEST2D_GEOMETRIES_{self.options.geometries}")
        self.cpp_info.defines.append(f"LIBNEST2D_OPTIMIZERS_{self.options.optimizer}")
        self.cpp_info.defines.append(f"LIBNEST2D_THREADING_{self.options.threading}")
        if self.settings.os in ["Linux", "FreeBSD", "Macos"] and self.options.threading == "std":
            self.cpp_info.system_libs.append("pthread")

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()
