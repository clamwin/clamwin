/*
 * ClamWin Free Antivirus — Log file utilities
 *
 * Shared helpers for appending timestamped markers and footers to
 * the persistent scan / update log files.  Thread-safe.
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

#pragma once
#include <string>

/* Append arbitrary text to a log file using FILE_APPEND_DATA (atomic
 * seek-to-end on NTFS).  Silently emits an OutputDebugString on failure. */
void CW_AppendToLogFile(const std::string& filePath, const std::string& text);

/* Build a "Scan Started <timestamp>" or "Update Started <timestamp>" line
 * using localtime + strftime. */
std::string CW_BuildStartTimestamp(bool isUpdate);

/* Build the separator footer written after a scan/update completes. */
std::string CW_BuildCompletedFooter();

/* Build a footer for when the process failed to launch. */
std::string CW_BuildFailedFooter();

/* ─── Debug Logging ─────────────────────────────────────────── */

/* Derive the path for ClamWinDebug.log based on the scan log path.
 * The debug log is placed in the same directory as the sibling path. */
std::string CW_GetDebugLogPath(const std::string& siblingPath);

/* Append a timestamped, formatted string to the debug log file.
 * If logPath is empty, the log is skipped. */
void CW_DebugLog(const std::string& logPath, const char* fmt, ...);
