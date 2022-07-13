from conans import tools
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake


class LibNest2DTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def generate(self):
        cmake = CMakeDeps(self)
        cmake.generate()

        tc = CMakeToolchain(self, generator = "Ninja")
        if self.settings.compiler == "Visual Studio":
            tc.blocks["generic_system"].values["generator_platform"] = None
            tc.blocks["generic_system"].values["toolset"] = None
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            ext = ".exe" if self.settings.os == "Windows" else ""
            prefix_path = "" if self.settings.os == "Windows" else "./"
            self.run(f"{prefix_path}test{ext}", env = "conanrun")