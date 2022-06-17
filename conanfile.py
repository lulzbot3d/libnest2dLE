import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conans import tools
from conan.tools.files import AutoPackager
from conans.errors import ConanException

required_conan_version = ">=1.46.2"


class Libnest2DConan(ConanFile):
    name = "libnest2d"
    description = "2D irregular bin packaging and nesting library written in modern C++"
    topics = ("conan", "cura", "prusaslicer", "nesting", "c++", "bin packaging")
    settings = "os", "compiler", "build_type", "arch"
    build_policy = "missing"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tests": [True, False],
        "header_only": [True, False],
        "geometries": ["clipper", "boost", "eigen"],
        "optimizer": ["nlopt", "optimlib"],
        "threading": ["std", "tbb", "omp", "none"]
    }
    default_options = {
        "shared": True,
        "tests": False,
        "fPIC": True,
        "header_only": False,
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

    @property
    def _conan_data_version(self):
        version = tools.Version(self.version)
        return f"{version.major}.{version.minor}.{version.patch}-{version.prerelease}"

    def layout(self):
        self.folders.source = "."
        try:
            build_type = str(self.settings.build_type)
        except ConanException:
            raise ConanException("'build_type' setting not defined, it is necessary for cmake_layout()")
        self.folders.build = f"cmake-build-{build_type.lower()}"
        self.folders.generators = os.path.join(self.folders.build, "conan")

        self.cpp.source.includedirs = ["include"]

        self.cpp.build.libdirs = ["."]
        self.cpp.build.bindirs = ["."]


    def configure(self):
        self.options["*"].shared = True
        if self.options.shared or self.settings.compiler == "Visual Studio":
            del self.options.fPIC
        if self.options.geometries == "clipper":
            self.options["boost"].header_only = True

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("ninja/[>=1.10.0]")
        self.tool_requires("cmake/[>=3.23.0]")
        if self.options.tests:
            self.tool_requires("catch2/2.13.6", force_host_context=True)

    def requirements(self):
        for req in self.conan_data[f"requirements_{self.options.geometries}"][self._conan_data_version]:
            self.requires(req)
        for req in self.conan_data[f"requirements_{self.options.optimizer}"][self._conan_data_version]:
            self.requires(req)

    def generate(self):
        cmake = CMakeDeps(self)
        cmake.generate()

        tc = CMakeToolchain(self, generator = "Ninja")

        # Don't use Visual Studio as the CMAKE_GENERATOR
        if self.settings.compiler == "Visual Studio":
            tc.blocks["generic_system"].values["generator_platform"] = None
            tc.blocks["generic_system"].values["toolset"] = None

        tc.variables["LIBNEST2D_HEADER_ONLY"] = self.options.header_only
        if self.options.header_only:
            tc.variables["BUILD_SHARED_LIBS"] = False
        else:
            tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["LIBNEST2D_BUILD_UNITTESTS"] = self.options.tests
        tc.variables["LIBNEST2D_GEOMETRIES"] = self.options.geometries
        tc.variables["LIBNEST2D_OPTIMIZER"] = self.options.optimizer
        tc.variables["LIBNEST2D_THREADING"] = self.options.threading

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        packager = AutoPackager(self)
        packager.run()

    def package_info(self):
        if not self.options.header_only:
            self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.defines.append(f"LIBNEST2D_GEOMETRIES_{self.options.geometries}")
        self.cpp_info.defines.append(f"LIBNEST2D_OPTIMIZERS_{self.options.optimizer}")
        self.cpp_info.defines.append(f"LIBNEST2D_THREADING_{self.options.threading}")
        if self.settings.os in ["Linux", "FreeBSD", "Macos"]:
            self.cpp_info.system_libs.append("pthread")

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()
