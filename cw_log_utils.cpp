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

std::string buildTrimTempPath(const std::string& filePath)
{
    char suffix[64];
    _snprintf(suffix, sizeof(suffix), ".trim.%lu.%lu.tmp",
              (unsigned long)GetCurrentProcessId(),
              (unsigned long)GetTickCount());
    suffix[sizeof(suffix) - 1] = '\0';
    return filePath + suffix;
}

bool getFileSize64(HANDLE fileHandle, unsigned long long& sizeOut)
{
    DWORD high = 0;
    DWORD low = GetFileSize(fileHandle, &high);
    if (low == INVALID_FILE_SIZE && GetLastError() != NO_ERROR)
        return false;

    sizeOut = ((unsigned long long)high << 32) | (unsigned long long)low;
    return true;
}

bool setFilePointer64(HANDLE fileHandle, unsigned long long offset)
{
    LONG high = (LONG)(offset >> 32);
    DWORD low = SetFilePointer(fileHandle,
                               (LONG)(offset & 0xffffffffULL),
                               &high,
                               FILE_BEGIN);
    if (low == INVALID_SET_FILE_POINTER && GetLastError() != NO_ERROR)
        return false;

    return true;
}
}

void CW_TrimLogFileToMaxBytes(const std::string& filePath,
                              unsigned long long maxBytes)
{
    if (filePath.empty() || maxBytes == 0)
        return;

    std::basic_string<TCHAR> tPath = CW_ToT(filePath);
    HANDLE hSrc = CreateFile(tPath.c_str(), GENERIC_READ,
                             FILE_SHARE_READ | FILE_SHARE_WRITE,
                             NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hSrc == INVALID_HANDLE_VALUE)
        return;

    unsigned long long fileSize = 0;
    if (!getFileSize64(hSrc, fileSize) || fileSize == 0 || fileSize <= maxBytes)
    {
        CloseHandle(hSrc);
        return;
    }

    if (!setFilePointer64(hSrc, fileSize - maxBytes))
    {
        CloseHandle(hSrc);
        return;
    }

    std::string tempPath = buildTrimTempPath(filePath);
    std::basic_string<TCHAR> tTempPath = CW_ToT(tempPath);
    HANDLE hDst = CreateFile(tTempPath.c_str(), GENERIC_WRITE, 0,
                             NULL, CREATE_ALWAYS,
                             FILE_ATTRIBUTE_TEMPORARY, NULL);
    if (hDst == INVALID_HANDLE_VALUE)
    {
        CloseHandle(hSrc);
        return;
    }

    bool ok = true;
    unsigned long long remaining = maxBytes;
    char buffer[64 * 1024];

    while (remaining > 0)
    {
        DWORD chunk = remaining > (unsigned long long)sizeof(buffer)
                    ? (DWORD)sizeof(buffer)
                    : (DWORD)remaining;
        DWORD read = 0;
        if (!ReadFile(hSrc, buffer, chunk, &read, NULL) || read == 0)
        {
            ok = false;
            break;
        }

        DWORD written = 0;
        if (!WriteFile(hDst, buffer, read, &written, NULL) || written != read)
        {
            ok = false;
            break;
        }

        remaining -= read;
    }

    CloseHandle(hSrc);
    CloseHandle(hDst);

    if (ok && MoveFileEx(tTempPath.c_str(), tPath.c_str(),
                         MOVEFILE_REPLACE_EXISTING | MOVEFILE_COPY_ALLOWED))
        return;

    DeleteFile(tTempPath.c_str());
}

void CW_AppendToLogFile(const std::string& filePath,
                        const std::string& text,
                        unsigned long long maxBytes)
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

    if (maxBytes > 0)
        CW_TrimLogFileToMaxBytes(filePath, maxBytes);
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
