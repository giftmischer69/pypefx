echo off

goto(){
# Linux code here
# https://nastytester.com/posts/script-that-works-in-windows-and-linux.html
echo TODO Linux Build!
}

goto $@
exit

:(){
rem Windows script here
echo %OS%
echo reading version
CALL version.cmd
echo cleaning build dir
pyoxidizer build
robocopy build\x86_64-pc-windows-msvc\debug\install dist /s
robocopy defaults.ini dist\defaults.ini /s
robocopy plugins dist\plugins /s
robocopy projects dist\projects /s
7z a -tzip pypefx-%__version__%.zip ./dist/*
goto :eof
