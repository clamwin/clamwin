# ClamWin — Native Win32 C++ GUI for ClamAV

ClamWin is a native Windows GUI frontend for the [ClamAV](https://www.clamav.net/) antivirus engine.
It spawns the command-line ClamAV tools (`clamscan.exe`, `freshclam.exe`, etc.) as child processes — there is no direct `libclamav` link dependency.

This repository was split out from the [clamav-win32](https://github.com/nicorlaw/clamav-win32) project to keep the GUI code independent from the engine build.

## Requirements

- **ClamAV command-line binaries** — pre-built Windows packages are available at <https://oss.netfarm.it/clamav/>
- **CMake** 3.14 or later
- **MinGW-w64** (GCC) or **MSVC**

## Building

### Configure and build with MinGW

```powershell
$env:PATH = "C:\msys64\mingw64\bin;C:\Program Files\CMake\bin;" + $env:PATH

cmake -S . -B build -G "MinGW Makefiles" `
    -DCMAKE_C_COMPILER=gcc `
    -DCMAKE_CXX_COMPILER=g++ `
    -DCMAKE_MAKE_PROGRAM=mingw32-make `
    -DCLAMWIN_SHELLEXT_UNICODE=ON

cmake --build build --target clamwin
```

The GUI executable is produced at `build/clamwin.exe`.

### Configure and build with MSVC

```powershell
cmake -S . -B build -DCLAMWIN_SHELLEXT_UNICODE=ON
cmake --build build --target clamwin --config Release
```

### Shell extension

A Windows Explorer context-menu shell extension (`ExpShell.dll`) is built automatically alongside the GUI.
Set `-DCLAMWIN_SHELLEXT_UNICODE=ON` for Unicode builds (x64, Windows XP+) or `-DCLAMWIN_SHELLEXT_UNICODE=OFF` for ANSI builds (Windows 98).

### Installer

Inno Setup scripts are located under `setup/`. Use [Inno Setup 5](https://jrsoftware.org/isinfo.php) to compile `Setup.iss` (bundled database) or `Setup-nodb.iss` (no database).

## GUI Test Workflow

The native Win32 C++ GUI has a dedicated test executable named `clamwin_gui_test.exe`.

The shortest way to run the GUI suite from the repository root is:

```powershell
.\test-gui.ps1
```

Optional switches:

```powershell
.\test-gui.ps1 -RealTools
.\test-gui.ps1 -RealTools -FreshclamUpdate -FreshclamNegative
.\test-gui.ps1 -BuildOnly
```

Build it from the repository root:

```powershell
$env:PATH = "C:\msys64\mingw64\bin;C:\Program Files\CMake\bin;" + $env:PATH
cmake -S . -B build-gui -G "MinGW Makefiles" -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DCMAKE_MAKE_PROGRAM=mingw32-make
cmake --build build-gui --target clamwin_gui_test
```

Run the default GUI tests:

```powershell
cmake --build build-gui --target clamwin_check
```

Enable the real-binary smoke tests for `clamscan.exe` and `freshclam.exe`:

```powershell
cmake --build build-gui --target clamwin_check_real_tools
```

## License

ClamWin is free software released under the GNU General Public License v2.
