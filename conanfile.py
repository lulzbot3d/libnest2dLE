import os

from os import path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import AutoPackager, files, collect_libs, copy
from conan.tools.build import check_min_cppstd
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version


required_conan_version = ">=1.58.0"


class Nest2DConan(ConanFile):
    name = "nest2d"
    description = "2D irregular bin packaging and nesting library written in modern C++"
    topics = ("conan", "cura", "prusaslicer", "nesting", "c++", "bin packaging")
    settings = "os", "compiler", "build_type", "arch"
    build_policy = "missing"

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

    def set_version(self):
        if self.version is None:
            self.version = "5.4.0-alpha"

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "clang": "9",
            "apple-clang": "9",
            "msvc": "192",
            "visual_studio": "14",
        }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        copy(self, "*", path.join(self.recipe_folder, "src"), path.join(self.export_sources_folder, "src"))
        copy(self, "*", path.join(self.recipe_folder, "include"), path.join(self.export_sources_folder, "include"))
        copy(self, "*", path.join(self.recipe_folder, "tests"), path.join(self.export_sources_folder, "tests"))
        copy(self, "*", path.join(self.recipe_folder, "tools"), path.join(self.export_sources_folder, "tools"))

    def layout(self):
        cmake_layout(self)
        self.cpp.package.libs = ["nest2d"]

    def requirements(self):
        if self.options.geometries == "clipper":
            self.requires("boost/1.82.0", transitive_headers=True)
            self.requires("clipper/6.4.2", transitive_headers=True)
        if self.options.geometries == "boost":
            self.requires("boost/1.82.0", transitive_headers=True)
        if self.options.optimizer == "nlopt":
            self.requires("nlopt/2.7.0", transitive_headers=True)
        if self.options.optimizer == "optimlib":
            self.requires("armadillo/10.7.3", transitive_headers=True)
        if self.options.threading == "tbb":
            self.requires("tbb/2020.3", transitive_headers=True)
        if self.options.threading == "omp":
            self.requires("llvm-openmp/12.0.1", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 192)  # TODO: remove in Conan 2.0
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def build_requirements(self):
        self.test_requires("standardprojectsettings/[>=0.1.0]@ultimaker/stable")
        if self.options.enable_testing:
            self.test_requires("catch2/[>=2.13.6]")


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["boost"].header_only = True
        if self.options.geometries == "clipper":
            self.options["clipper"].shared = True if self.options.header_only else self.options.shared
        self.options[str(self.options.optimizer)].shared = True if self.options.header_only else self.options.shared
        if self.options.threading == "tbb":
            self.options["tbb"].shared = True if self.options.header_only else self.options.shared
        if self.options.threading == "omp":
            self.options["llvm-openmp"].shared =True if self.options.header_only else self.options.shared

    def generate(self):
        deps = CMakeDeps(self)
        if self.options.enable_testing:
            deps.build_context_activated = ["catch2"]
            deps.build_context_build_modules = ["catch2"]
        deps.generate()

        tc = CMakeToolchain(self)
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
            self.cpp_info.libs = collect_libs(self)
        self.cpp_info.defines.append(f"LIBNEST2D_GEOMETRIES_{self.options.geometries}")
        self.cpp_info.defines.append(f"LIBNEST2D_OPTIMIZERS_{self.options.optimizer}")
        self.cpp_info.defines.append(f"LIBNEST2D_THREADING_{self.options.threading}")
        if self.settings.os in ["Linux", "FreeBSD", "Macos"] and self.options.threading == "std":
            self.cpp_info.system_libs.append("pthread")

    def package_id(self):
        if self.options.header_only:
            self.info.clear()
