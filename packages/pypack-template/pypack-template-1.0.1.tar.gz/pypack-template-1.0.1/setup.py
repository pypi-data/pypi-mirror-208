# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup
from glob import glob
import os

# The main interface is through Pybind11Extension.
# * You can add cxx_std=11/14/17, and then build_ext can be removed.
# * You can set include_pybind11=false to add the include directory yourself,
#   say from a submodule.
#
# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)

package_name = "pypack"
ext_modules = [
    Pybind11Extension(f"{package_name}.c",
        sorted(glob(f"src/{package_name}/c/*.cpp")),
        # Example: passing in the version to the compiled code
        define_macros = [('VERSION_INFO', 1)],
        include_dirs = [f"src/{package_name}/c"],
        language = "c++",
        ),
]
setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
