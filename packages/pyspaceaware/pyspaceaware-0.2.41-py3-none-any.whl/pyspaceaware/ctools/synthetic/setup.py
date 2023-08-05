from distutils.core import setup, Extension
import distutils
import os
import sysconfig
import numpy as np

distutils.log.set_verbosity(1)
src_dir = os.getcwd()
# Common flags for both release and debug builds.
extra_compile_args = sysconfig.get_config_var("CFLAGS").split()

include_dirs = [
    os.path.join(src_dir, "synthetic_include"),
    np.get_include(),
]
library_dirs = [os.path.join(src_dir, "synthetic_lib")]

os.environ[
    "LDFLAGS"
] = """-framework CoreVideo -framework IOKit -framework Cocoa -framework GLUT -framework OpenGL synthetic_lib/libraylib_m1.a"""


def main():
    print(f"{include_dirs=}")
    print(f"{library_dirs=}")
    setup(
        name="synth_rpo",
        version="1.0.0",
        description="Python interface for the SyntheticRPO image generator",
        author="Liam Robinson",
        author_email="robin502@purdue.edu",
        ext_modules=[
            Extension(
                "synth_rpo",
                sources=["SyntheticRPO.c"],
                include_dirs=include_dirs,
            )
        ],
    )


if __name__ == "__main__":
    main()
