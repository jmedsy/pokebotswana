@echo off

:: Set the path to your mGBA development build
set MGBA_DEV_BUILD_PATH=C:\Users\Josh\repos\pokebotswana\mGBA-build-2025-07-15-win32-8840-62070f11d5c8b9c55c53479c7e133d06ca676323

cd /d "%MGBA_DEV_BUILD_PATH%"
mGBA.exe --script "%~dp0mgba_scripting\server\socket_server.lua" "%~dp0roms\Pokemon - Fire Red Version (U) (V1.1).zip" 