pyoxidizer build
robocopy build\x86_64-pc-windows-msvc\debug\install dist /s
robocopy defaults.ini dist\defaults.ini /s
robocopy plugins dist\plugins /s
robocopy projects dist\projects /s
7z a -tzip pypefx_release.zip dist