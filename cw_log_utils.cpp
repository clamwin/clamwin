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

void CW_AppendToLogFile(const std::string& filePath, const std::string& text)
{
    if (filePath.empty() || text.empty())
        return;

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
