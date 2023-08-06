# This file defines how PyOxidizer application building and packaging is
# performed. See PyOxidizer's documentation at
# https://pyoxidizer.readthedocs.io/en/stable/ for details of this
# configuration file format.


# Configuration files consist of functions which define build "targets."
# This function creates a Python executable and installs it in a destination
# directory.
def make_exe():
    # Obtain the default PythonDistribution for our build target. We link
    # this distribution into our produced executable and extract the Python
    # standard library from it.
    dist = default_python_distribution(python_version="3.9")

    # The configuration of the embedded Python interpreter can be modified
    # by setting attributes on the instance. Some of these are
    # documented below.
    python_config = dist.make_python_interpreter_config()

    # defines the Python module to run as __main__ in Py_RunMain()
    # this is equivalent to python -m pglift
    python_config.run_module = "pglift"

    exe = dist.to_python_executable(
        name="pglift",
        config=python_config,
    )

    exe.add_python_resources(
        exe.pip_install([".", "-r", "pyoxidizer/requirements.txt"])
    )

    return exe


# Tell PyOxidizer about the build targets defined above.
register_target("exe", make_exe)

# Resolve whatever targets the invoker of this configuration file is requesting
# be resolved.
resolve_targets()
