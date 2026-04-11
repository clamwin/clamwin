/*
 * cw_bcrypt_compat.c — XP-compatible shim for BCryptGenRandom
 *
 * libcurl's rand.c references BCryptGenRandom (bcrypt.dll) when compiled
 * against _WIN32_WINNT >= 0x0600.  bcrypt.dll does not exist on Windows XP
 * or earlier, causing an import-table failure at process startup.
 *
 * This translation unit provides our own definition of BCryptGenRandom that:
 *   - On Vista+: dynamically loads bcrypt.dll and calls the real function.
 *   - On XP/Win98: falls back to CryptGenRandom from advapi32.dll.
 *
 * Link WITHOUT -lbcrypt; this file replaces that dependency.
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

#include <windows.h>
#include <wincrypt.h>

typedef LONG NTSTATUS;
#define CW_STATUS_SUCCESS     ((NTSTATUS)0x00000000L)
#define CW_STATUS_UNSUCCESSFUL ((NTSTATUS)0xC0000001L)

/* BCryptGenRandom dwFlags value used by libcurl */
#define BCRYPT_USE_SYSTEM_PREFERRED_RNG 0x00000002UL

typedef NTSTATUS (WINAPI *BCryptGenRandom_fn)(PVOID, PUCHAR, ULONG, ULONG);

NTSTATUS WINAPI BCryptGenRandom(PVOID   hAlgorithm,
                                 PUCHAR  pbBuffer,
                                 ULONG   cbBuffer,
                                 ULONG   dwFlags)
{
    /* Try the real bcrypt.dll — present on Vista and later. */
    static volatile LONG s_state = 0; /* 0=uninit, 1=found, 2=not found */
    static BCryptGenRandom_fn s_fn = NULL;

    if (s_state == 0)
    {
        HMODULE hMod = LoadLibraryA("bcrypt.dll");
        if (hMod)
        {
            s_fn = (BCryptGenRandom_fn)GetProcAddress(hMod, "BCryptGenRandom");
            InterlockedExchange(&s_state, s_fn ? 1 : 2);
        }
        else
        {
            InterlockedExchange(&s_state, 2);
        }
    }

    if (s_state == 1 && s_fn)
        return s_fn(hAlgorithm, pbBuffer, cbBuffer, dwFlags);

    /* Fallback: CryptGenRandom via the legacy crypto provider (XP compatible). */
    HCRYPTPROV hProv = 0;
    if (!CryptAcquireContextA(&hProv, NULL, NULL, PROV_RSA_FULL,
                               CRYPT_VERIFYCONTEXT | CRYPT_SILENT))
        return CW_STATUS_UNSUCCESSFUL;

    BOOL ok = CryptGenRandom(hProv, cbBuffer, pbBuffer);
    CryptReleaseContext(hProv, 0);
    return ok ? CW_STATUS_SUCCESS : CW_STATUS_UNSUCCESSFUL;
}
