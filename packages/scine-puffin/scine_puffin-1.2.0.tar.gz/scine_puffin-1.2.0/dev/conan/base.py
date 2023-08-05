__copyright__ = """This code is licensed under the 3-clause BSD license.
Copyright ETH Zurich, Laboratory of Physical Chemistry, Reiher Group.
See LICENSE.txt for details
"""

import os
import sys
from .utils import microarch, python_module_dir, reference_name
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from typing import Dict, Any


class ScineConan(ConanFile):
    """ Object to inherit from to implement a ConanFile.

        When inheriting from this base class, you need to make
        a _configure_cmake method, which can usually be implemented
        in terms of _configure_cmake_base.
    """

    license = "BSD-3-Clause"
    author = "Research Group Prof. Markus Reiher, LPC, ETH Zurich"
    url = "https://github.com/qcscine"
    topics = ("chemistry", "cheminformatics")
    settings: Any = ("os", "compiler", "build_type", "arch")
    generators = "cmake", "cmake_find_package"
    revision_mode = "scm"
    keep_imports = True

    _cmake = None

    def _conan_hook_path(self) -> str:
        """ Path of the exported cmake hook file """
        return os.path.join("dev", "conan", "hook.cmake")

    def _exports_suffix(self, suffix: str) -> bool:
        """ Whether any exported file ends with a particular suffix """
        return any(fname.endswith(suffix) for fname in self.exports_sources)

    def _propagate_scine_option(self, option: str) -> None:
        """ Propagates an option to upstream SCINE dependencies.

            Assumes SCINE dependencies will also have the option as it
            unfortunately can't be checked.

        """
        option_value = self.options.get_safe(option)
        if option_value is None:
            return

        # You might want to check if the dependency has this option, but you
        # can't. The fields aren't populated with default values nor validated
        # until the point where they are propagated.
        #
        # Try self.output.info("{}".format(self.options[dep].fields)) -> []
        if hasattr(self, "requires"):
            for dep in self.requires:
                if dep.startswith("scine_"):
                    if option not in self.options[dep].fields:
                        setattr(self.options[dep], option, option_value)

        if hasattr(self, "build_requires"):
            deps = self.build_requires
            if isinstance(deps[0], tuple):
                deps = [dep[0] for dep in deps]

            for dep in deps:
                if dep.startswith("scine_"):
                    if option not in self.options[dep].fields:
                        setattr(self.options[dep], option, option_value)

    def configure(self) -> None:
        """ Determine whether the settings and options are correct """
        if self._exports_suffix(".cpp"):
            tools.check_min_cppstd(self, "14")

        if self.options.get_safe("coverage"):
            if not self.options.get_safe("tests"):
                raise ConanInvalidConfiguration(
                    "Coverage requires testing to be enabled")

            if self.settings.get_safe("build_type") != "Debug":
                raise ConanInvalidConfiguration(
                    "Coverage testing should be done on a debug build")

        # See the assumptions on this fn
        self._propagate_scine_option("python")
        if self.settings.get_safe("python") == True:
            self._propagate_scine_option("python_version")

        if self.options.get_safe("microarch") == "none":
            self._propagate_scine_option("microarch")

    def _default_cmake_definitions(self, project_name: str
                                   ) -> Dict[str, Any]:
        """ Builds the default SCINE CMake definitions """
        definitions = {
            "SCINE_BUILD_DOCS": False,
            "SCINE_MARCH": "",
            "PYTHON_EXECUTABLE": sys.executable
        }

        project_include_key = "CMAKE_PROJECT_" + project_name + "_INCLUDE"
        definitions[project_include_key] = self._conan_hook_path()

        if self.options.get_safe("microarch") == "detect":
            definitions["SCINE_MARCH"] = microarch(self) or ""

        if "tests" in self.options:
            definitions["SCINE_BUILD_TESTS"] = self.options.tests

        if "python" in self.options:
            definitions["SCINE_BUILD_PYTHON_BINDINGS"] = self.options.python

        if "coverage" in self.options:
            definitions["COVERAGE"] = self.options.coverage

        if "docs" in self.options:
            definitions["SCINE_BUILD_DOCS"] = self.options.docs

        return definitions

    def _configure_cmake(self) -> CMake:
        """ Configuration of the project """

        # CMake instance is class state to avoid running configure twice
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        default_definitions = self._default_cmake_definitions(self.cmake_name)
        self._cmake.definitions.update(default_definitions)
        if hasattr(self, "cmake_definitions"):
            for k, v in self.cmake_definitions.items():
                if callable(v):
                    self._cmake.definitions[k] = v(self)
                else:
                    self._cmake.definitions[k] = v

        self._cmake.configure()
        return self._cmake

    def build(self) -> None:
        """ Builds the project and runs tests if enabled """
        cmake = self._configure_cmake()
        cmake.build()

        if self.options.get_safe("tests"):
            # Many of our tests are parallel. If the tests are run in parallel,
            # then the individual tests are run serially, seriously affecting
            # wall clock times.
            cmake.parallel = False
            cmake.test(output_on_failure=True)
            cmake.parallel = True

    def imports(self) -> None:
        """ Copies license files from all dependencies """
        self.copy("license*", dst="licenses", folder=True, ignore_case=True)
        self.copy("copying*", dst="licenses", folder=True, ignore_case=True)
        self.copy("copyright*", dst="licenses", folder=True, ignore_case=True)

    def package(self) -> None:
        """ Post-build, create desired package file structure """
        cmake = self._configure_cmake()
        cmake.install()
        cmake.patch_config_paths()
        # Copy dependencies' licenses and our own
        self.copy("licenses/*")
        self.copy("LICENSE.txt")
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def build_requirements(self) -> None:
        """ Determine additional requirements needed only to build """
        if self.options.get_safe("python"):
            self.build_requires("pybind11/2.6.2")

        if self.options.get_safe("tests"):
            self.build_requires("gtest/1.10.0")

        # CMake 3.13.4 is the minimum required for modern Boost releases
        cmake_version = CMake.get_version()
        if not tools.which("cmake") or cmake_version < "3.13.4" or cmake_version == "3.20.0":
            # CMake 3.20.0 has a bug when finding/linking openmp
            #  so it is exluded from the allowed versions, the version
            #  gap can be increased if 3.20.1 does not fix the error
            self.build_requires("cmake/[>=3.18.0 <3.20.0 || >3.20.0]")

    def package_id(self) -> None:
        """ Defines package ABI by modifying a hashable info object """
        # Remove options that do not contribute to package ID
        for name in ["tests", "coverage", "docs"]:
            if name in self.options:
                delattr(self.info.options, name)

        # Overwrite microarch value in info with detected or make it empty
        if "microarch" in self.options:
            if self.options.get_safe("microarch") == "detect":
                self.info.options.microarch = microarch(self) or ""
            else:
                self.info.options.microarch = ""

        # Clear python version if not applicable
        if "python" in self.options:
            if not self.options.get_safe("python") and "python_version" in self.options:
                self.info.options.python_version = ""

        # Set package-revision mode for scine dependencies
        for dep in self.info.requires.pkg_names:
            if dep.startswith("scine_"):
                self.info.requires[dep].package_revision_mode()

    def package_info_cmake(self) -> None:
        """ Sets general properties of generated CMake code """
        # Set the name of the find module and the target namespace name
        for generator in ["cmake_find_package", "cmake_find_package_multi"]:
            self.cpp_info.filenames[generator] = "Scine" + self.cmake_name
            self.cpp_info.names[generator] = "Scine"

        # Generate a single component to complete the triad
        main_component = self.cpp_info.components[self.cmake_name]
        main_component.libs = [
            lib for lib in tools.collect_libs(self)
            if "module" not in lib
        ]
        main_component.includedirs = [os.path.join("include", "Scine")]

        # Collect all direct non-private dependencies and add them as requires
        # to the main component
        direct_dep_names = [reference_name(pkg) for pkg in self.requires]
        for name, dependency in self.deps_cpp_info.dependencies:
            if str(name) not in direct_dep_names:
                continue

            if self.requires[name].private:
                continue

            if len(dependency.components) == 0:
                main_component.requires.append(str(name) + "::" + str(name))
            else:
                main_component.requires.extend([
                    str(name) + "::" + str(component)
                    for component in dependency.components
                ])

    def package_info_env(self) -> None:
        """ Sets package environment variables for downstream """
        # Add binaries to PATH
        binpath = os.path.join(self.package_folder, "bin")
        if os.path.exists(binpath):
            self.env_info.PATH.append(binpath)

        # Add shared libraries to os appropriate environment variable
        libpath = os.path.join(self.package_folder, "lib")
        if self.options.get_safe("shared") and os.path.exists(libpath):
            if self.settings.os == "Windows":
                self.env_info.PATH.append(libpath)
            elif self.settings.os == "Linux":
                self.env_info.LD_LIBRARY_PATH.append(libpath)
            elif self.settings.os == "Macos":
                self.env_info.DYLD_LIBRARY_PATH.append(libpath)

        # If this package has a module, add it to the scine module path
        if any("module" in lib for lib in tools.collect_libs(self)):
            self.env_info.SCINE_MODULE_PATH.append(libpath)

        # Add python packages to PYTHONPATH
        if self.options.get_safe("python"):
            pypath = python_module_dir(self.package_folder)
            self.env_info.PYTHONPATH.append(pypath)

    def package_info(self) -> None:
        """ Defines properties of the package for downstream """
        self.package_info_cmake()
        self.package_info_env()
