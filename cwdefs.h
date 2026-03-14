/*
 * ClamWin Free Antivirus — Platform version defines
 *
 * Must be included before <windows.h> to set WINAPI target correctly.
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

#ifndef CWDEFS_H
#define CWDEFS_H


/* Suppress rarely-used Windows headers */
#ifndef WIN32_LEAN_AND_MEAN
#  define WIN32_LEAN_AND_MEAN
#endif
#ifndef NOMINMAX
#  define NOMINMAX
#endif

#endif /* CWDEFS_H */
