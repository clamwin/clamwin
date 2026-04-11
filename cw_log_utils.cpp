/*
 * ClamWin Free Antivirus — Log file utilities
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

#include "cw_log_utils.h"
#include "cw_text_conv.h"

#include <windows.h>
#include <tchar.h>
#include <time.h>
#include <stdio.h>

namespace
{
void ensureParentDirectoryExists(const std::string& filePath)
{
    if (filePath.empty())
        return;

    std::basic_string<TCHAR> tPath = CW_ToT(filePath);
    size_t sep = tPath.rfind(TEXT('\\'));
    if (sep == std::basic_string<TCHAR>::npos)
        sep = tPath.rfind(TEXT('/'));
    if (sep == std::basic_string<TCHAR>::npos)
        return;

    std::basic_string<TCHAR> dir = tPath.substr(0, sep);
    if (dir.empty())
        return;

    for (size_t i = 0; i < dir.size(); ++i)
    {
        const TCHAR ch = dir[i];
        if (ch != TEXT('\\') && ch != TEXT('/'))
            continue;

        if (i == 0)
            continue;
        if (i == 2 && dir.size() > 1 && dir[1] == TEXT(':'))
            continue;

        std::basic_string<TCHAR> part = dir.substr(0, i);
        if (!part.empty())
            CreateDirectory(part.c_str(), NULL);
    }

    CreateDirectory(dir.c_str(), NULL);
}
}

void CW_AppendToLogFile(const std::string& filePath, const std::string& text)
{
    if (filePath.empty() || text.empty())
        return;

    ensureParentDirectoryExists(filePath);

    std::basic_string<TCHAR> tPath = CW_ToT(filePath);
    HANDLE hFile = CreateFile(tPath.c_str(), FILE_APPEND_DATA,
                              FILE_SHARE_READ | FILE_SHARE_WRITE,
                              NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE)
    {
        OutputDebugStringA("ClamWin: failed to open log file for append\n");
        return;
    }

    DWORD written = 0;
    if (!WriteFile(hFile, text.c_str(), (DWORD)text.size(), &written, NULL)
        || written != (DWORD)text.size())
    {
        OutputDebugStringA("ClamWin: partial or failed write to log file\n");
    }
    CloseHandle(hFile);
}

std::string CW_BuildStartTimestamp(bool isUpdate)
{
    time_t now = time(NULL);
    char timeBuf[64];

    if (now == (time_t)(-1))
    {
        snprintf(timeBuf, sizeof(timeBuf), "(unknown)");
    }
    else
    {
        struct tm tmBuf = {0};
        struct tm* tmPtr = localtime(&now);
        if (tmPtr) {
            tmBuf = *tmPtr;
            strftime(timeBuf, sizeof(timeBuf), "%a %b %d %H:%M:%S %Y", &tmBuf);
        } else {
            snprintf(timeBuf, sizeof(timeBuf), "(unknown)");
        }
    }

    std::string line = "\r\n";
    line += isUpdate ? "Update Started " : "Scan Started ";
    line += timeBuf;
    line += "\r\n";
    return line;
}

std::string CW_BuildCompletedFooter()
{
    return "\r\n"
           "--------------------------------------\r\n"
           "Completed\r\n"
           "--------------------------------------\r\n";
}

std::string CW_BuildFailedFooter()
{
    return "\r\n"
           "--------------------------------------\r\n"
           "Failed to Start\r\n"
           "--------------------------------------\r\n";
}

/* ─── Debug Logging ─────────────────────────────────────────── */

std::string CW_GetDebugLogPath(const std::string& siblingPath)
{
    char tempPath[MAX_PATH + 1] = {0};
    DWORD len = GetTempPathA(MAX_PATH, tempPath);
    if (len > 0 && len < MAX_PATH)
        return std::string(tempPath) + "ClamWinDebug.log";

    if (siblingPath.empty())
        return "";

    std::string::size_type sep = siblingPath.rfind('\\');
    if (sep == std::string::npos)
        sep = siblingPath.rfind('/');
    std::string dir = (sep != std::string::npos)
                    ? siblingPath.substr(0, sep + 1)
                    : "";
    return dir + "ClamWinDebug.log";
}

void CW_DebugLog(const std::string& logPath, const char* fmt, ...)
{
    if (logPath.empty() || !fmt)
        return;

    time_t now = time(NULL);
    char timeBuf[32] = "(unknown)";
    struct tm tmBuf = {0};
    struct tm* tmPtr = localtime(&now);
    if (now != (time_t)(-1) && tmPtr) {
        tmBuf = *tmPtr;
        strftime(timeBuf, sizeof(timeBuf), "%Y-%m-%d %H:%M:%S", &tmBuf);
    }

    char msg[1024];
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(msg, sizeof(msg), fmt, ap);
    msg[sizeof(msg) - 1] = '\0';
    va_end(ap);

    std::string line = "[";
    line += timeBuf;
    line += "] ";
    line += msg;
    line += "\r\n";

    CW_AppendToLogFile(logPath, line);
}
