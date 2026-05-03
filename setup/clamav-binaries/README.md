# Prebuilt ClamAV Binaries

The SignPath packaging workflow consumes prebuilt ClamAV engine binaries from this directory. The workflow does not cross-compile ClamAV; it builds the ClamWin GUI, packages these checked-in engine files with Inno Setup 5, uploads the unsigned installer as a GitHub Actions artifact, and submits that artifact to SignPath.

Required layout:

```text
setup/clamav-binaries/
  clamav-legacy-win9x/
    clamscan.exe
    freshclam.exe
    sigtool.exe
    libclamav.dll
    libfreshclam.dll
    curl-ca-bundle.crt
  clamav-legacy-x86/
    clamscan.exe
    freshclam.exe
    sigtool.exe
    libclamav.dll
    libfreshclam.dll
    curl-ca-bundle.crt
    certs/clamav.crt
  clamav-legacy-x64/
    clamscan.exe
    freshclam.exe
    sigtool.exe
    libclamav.dll
    libfreshclam.dll
    curl-ca-bundle.crt
    certs/clamav.crt
  clamav-x64/
    clamscan.exe
    freshclam.exe
    sigtool.exe
    libclamav.dll
    libfreshclam.dll
    curl-ca-bundle.crt
    certs/clamav.crt
```

Required alongside the binaries:

```text
SHA256SUMS.txt
```

`SHA256SUMS.txt` contains hashes for the checked-in binaries. The packaging script verifies the manifest before compiling the installer.

Recommended alongside the binaries:

```text
SOURCE.md
```

`SOURCE.md` should describe where the binaries came from and how they were produced.
