def make_dist():
    return default_python_distribution()

def make_exe(dist):
    policy = dist.make_python_packaging_policy()

    # policy.allow_files = True
    # policy.allow_in_memory_shared_library_loading = True

    # policy.bytecode_optimize_level_zero = True
    # policy.bytecode_optimize_level_one = True
    # policy.bytecode_optimize_level_two = True

    # policy.extension_module_filter = "all"

    # policy.extension_module_filter = "minimal"

    # policy.extension_module_filter = "no-libraries"

    # policy.extension_module_filter = "no-gpl"

    # policy.file_scanner_classify_files = True

    # policy.file_scanner_emit_files = False

    # Controls the `add_include` attribute of "classified" resources
    # (`PythonModuleSource`, `PythonPackageResource`, etc).
    policy.include_classified_resources = True

    # Toggle whether Python module source code for modules in the Python
    # distribution's standard library are included.
    # policy.include_distribution_sources = False

    # Toggle whether Python package resource files for the Python standard
    # library are included.
    # policy.include_distribution_resources = False

    # Controls the `add_include` attribute of `File` resources.
    # policy.include_file_resources = False

    # Controls the `add_include` attribute of `PythonModuleSource` not in
    # the standard library.
    policy.include_non_distribution_sources = True

    # Toggle whether files associated with tests are included.
    # policy.include_test = False

    # Resources are loaded from "in-memory" or "filesystem-relative" paths.
    # The locations to attempt to add resources to are defined by the
    # `resources_location` and `resources_location_fallback` attributes.
    # The former is the first/primary location to try and the latter is
    # an optional fallback.

    # Use in-memory location for adding resources by default.
    # policy.resources_location = "in-memory"

    # Use filesystem-relative location for adding resources by default.
    policy.resources_location = "filesystem-relative:lib"

    # Attempt to add resources relative to the built binary when
    # `resources_location` fails.
    # policy.resources_location_fallback = "filesystem-relative:prefix"

    # Clear out a fallback resource location.
    # policy.resources_location_fallback = None

    # Define a preferred Python extension module variant in the Python distribution
    # to use.
    # policy.set_preferred_extension_module_variant("foo", "bar")

    # Configure policy values to classify files as typed resources.
    # (This is the default.)
    # policy.set_resource_handling_mode("classify")

    # Configure policy values to handle files as files and not attempt
    # to classify files as specific types.
    # TODO THIS BREAKS THE LOCAL MODULE!!
    # TODO BUT THIS IS REQUIRED FOR NUMPY!!
    # policy.set_resource_handling_mode("files")

    # This variable defines the configuration of the embedded Python
    # interpreter. By default, the interpreter will run a Python REPL
    # using settings that are appropriate for an "isolated" run-time
    # environment.
    #
    # The configuration of the embedded Python interpreter can be modified
    # by setting attributes on the instance. Some of these are
    # documented below.
    python_config = dist.make_python_interpreter_config()

    # Make the embedded interpreter behave like a `python` process.
    # python_config.config_profile = "python"

    # Set initial value for `sys.path`. If the string `$ORIGIN` exists in
    # a value, it will be expanded to the directory of the built executable.
    # python_config.module_search_paths = ["$ORIGIN/lib"]

    # Use jemalloc as Python's memory allocator
    # python_config.raw_allocator = "jemalloc"

    # Use the system allocator as Python's memory allocator.
    # python_config.raw_allocator = "system"

    # Control whether `oxidized_importer` is the first importer on
    # `sys.meta_path`.
    # python_config.oxidized_importer = False

    # Enable the standard path-based importer which attempts to load
    # modules from the filesystem.
    # python_config.filesystem_importer = True

    # Set `sys.frozen = True`
    # python_config.sys_frozen = True

    # Set `sys.meipass`
    # python_config.sys_meipass = True

    # Write files containing loaded modules to the directory specified
    # by the given environment variable.
    # python_config.write_modules_directory_env = "/tmp/oxidized/loaded_modules"

    # Evaluate a string as Python code when the interpreter starts.
    # python_config.run_command = "<code>"

    # Run a Python module as __main__ when the interpreter starts.
    python_config.run_module = "helloworld"

    # Run a Python file when the interpreter starts.
    # python_config.run_filename = "/path/to/file"

    # Produce a PythonExecutable from a Python distribution, embedded
    # resources, and other options. The returned object represents the
    # standalone executable that will be built.
    exe = dist.to_python_executable(
        name="helloworld",

        # If no argument passed, the default `PythonPackagingPolicy` for the
        # distribution is used.
        packaging_policy=policy,

        # If no argument passed, the default `PythonInterpreterConfig` is used.
        config=python_config,
    )

    # Install tcl/tk support files to a specified directory so the `tkinter` Python
    # module works.
    # exe.tcl_files_path = "lib"

    # Make the executable a console application on Windows.
    # exe.windows_subsystem = "console"

    # Make the executable a non-console application on Windows.
    # exe.windows_subsystem = "windows"

    # Invoke `pip download` to install a single package using wheel archives
    # obtained via `pip download`. `pip_download()` returns objects representing
    # collected files inside Python wheels. `add_python_resources()` adds these
    # objects to the binary, with a load location as defined by the packaging
    # policy's resource location attributes.
    #exe.add_python_resources(exe.pip_download(["pyflakes==2.2.0"]))

    # Invoke `pip install` with our Python distribution to install a single package.
    # `pip_install()` returns objects representing installed files.
    # `add_python_resources()` adds these objects to the binary, with a load
    # location as defined by the packaging policy's resource location
    # attributes.
    #exe.add_python_resources(exe.pip_install(["appdirs"]))

    # Invoke `pip install` using a requirements file and add the collected resources
    # to our binary.
    exe.add_python_resources(exe.pip_install(["-r", "requirements.txt"]))

    

    # Read Python files from a local directory and add them to our embedded
    # context, taking just the resources belonging to the `foo` and `bar`
    # Python packages.
    # for resource in exe.read_package_root(path=".", packages=["helloworld"]):
    #     resource.add_location = "filesystem-relative:lib"
    #     exe.add_python_resource(resource)

    exe.add_python_resources(exe.read_package_root(
        path=".",
        packages=["helloworld"],
    ))

    # Discover Python files from a virtualenv and add them to our embedded
    # context.
    #exe.add_python_resources(exe.read_virtualenv(path="/path/to/venv"))

    # Filter all resources collected so far through a filter of names
    # in a file.
    #exe.filter_from_files(files=["/path/to/filter-file"]))

    # Return our `PythonExecutable` instance so it can be built and
    # referenced by other consumers of this target.
    return exe

def make_embedded_resources(exe):
    return exe.to_embedded_resources()

def make_install(exe):
    # Create an object that represents our installed application file layout.
    files = FileManifest()

    # Add the generated executable to our install layout in the root directory.
    files.add_python_resource(".", exe)

    return files

# Tell PyOxidizer about the build targets defined above.
register_target("dist", make_dist)
register_target("exe", make_exe, depends=["dist"])
register_target("resources", make_embedded_resources, depends=["exe"], default_build_script=True)
register_target("install", make_install, depends=["exe"], default=True)

# Resolve whatever targets the invoker of this configuration file is requesting
# be resolved.
resolve_targets()

# END OF COMMON USER-ADJUSTED SETTINGS.
#
# Everything below this is typically managed by PyOxidizer and doesn't need
# to be updated by people.

PYOXIDIZER_VERSION = "0.10.2"
PYOXIDIZER_COMMIT = "UNKNOWN"
