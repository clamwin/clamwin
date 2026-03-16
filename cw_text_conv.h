/*
 * ClamWin Free Antivirus — text conversion helpers
 *
 * Shared ANSI/TCHAR conversion utilities for GUI codepaths.
 */

#pragma once

#include <windows.h>
#include <tchar.h>
#include <string>
#include <vector>

inline std::basic_string<TCHAR> CW_ToT(const std::string& text)
{
#if defined(UNICODE) || defined(_UNICODE)
    int needed = MultiByteToWideChar(CP_ACP, 0, text.c_str(), -1, NULL, 0);
    if (needed <= 0)
        return std::basic_string<TCHAR>();
    std::vector<wchar_t> buf((size_t)needed);
    MultiByteToWideChar(CP_ACP, 0, text.c_str(), -1, &buf[0], needed);
    return std::basic_string<TCHAR>(&buf[0]);
#else
    return text;
#endif
}

inline std::string CW_ToNarrow(const TCHAR* text)
{
    if (!text)
        return std::string();

#if defined(UNICODE) || defined(_UNICODE)
    int needed = WideCharToMultiByte(CP_ACP, 0, text, -1, NULL, 0, NULL, NULL);
    if (needed <= 0)
        return std::string();
    std::vector<char> buf((size_t)needed);
    WideCharToMultiByte(CP_ACP, 0, text, -1, &buf[0], needed, NULL, NULL);
    return std::string(&buf[0]);
#else
    return std::string(text);
#endif
}

inline std::string CW_ToNarrow(const std::basic_string<TCHAR>& text)
{
    return CW_ToNarrow(text.c_str());
}
