#pragma once
/*
 * cw_time_edit.h — helpers for hour/minute edit controls
 *
 * Hours are written per the OS regional setting (24h or 12h AM/PM).
 * Minutes are always zero-padded to two digits.
 * The hour edit must NOT have ES_NUMBER so that "AM"/"PM" text is accepted.
 */
#include <windows.h>
#include <tchar.h>

inline bool CW_ContainsNoCase(const TCHAR* haystack, const TCHAR* needle)
{
    if (!haystack || !needle || !*needle)
        return false;

    int nlen = lstrlen(needle);
    if (nlen <= 0)
        return false;

    for (const TCHAR* p = haystack; *p; ++p)
    {
        int i = 0;
        while (i < nlen)
        {
            TCHAR a = p[i];
            TCHAR b = needle[i];
            if (!a)
                return false;
            a = (TCHAR)_totlower((int)a);
            b = (TCHAR)_totlower((int)b);
            if (a != b)
                break;
            ++i;
        }
        if (i == nlen)
            return true;
    }

    return false;
}

/* Write hour (0–23) formatted per LOCALE_ITIME ("1"→24h, "0"→12h AM/PM). */
inline void CW_WriteHourToEdit(HWND edit, int hour24)
{
    if (!edit) return;
    TCHAR itime[4] = {0};
    TCHAR am[32] = TEXT("AM");
    TCHAR pm[32] = TEXT("PM");
    GetLocaleInfo(LOCALE_USER_DEFAULT, LOCALE_ITIME, itime, _countof(itime));
    GetLocaleInfo(LOCALE_USER_DEFAULT, LOCALE_S1159, am, _countof(am));
    GetLocaleInfo(LOCALE_USER_DEFAULT, LOCALE_S2359, pm, _countof(pm));
    TCHAR buf[16];
    if (itime[0] == TEXT('1'))                         /* 24-hour */
    {
        wsprintf(buf, TEXT("%d"), hour24);
    }
    else                                          /* 12-hour */
    {
        int h12 = hour24 % 12;
        if (h12 == 0) h12 = 12;
        wsprintf(buf, TEXT("%d %s"), h12, hour24 < 12 ? am : pm);
    }
    SetWindowText(edit, buf);
}

/* Read hour back.  Strips optional AM/PM; returns 24-hour value 0–23. */
inline int CW_ReadHourFromEdit(HWND edit, int fallback)
{
    if (!edit) return fallback;
    TCHAR buf[32] = {0};
    GetWindowText(edit, buf, _countof(buf));
    if (!buf[0]) return fallback;

    TCHAR am[32] = TEXT("AM");
    TCHAR pm[32] = TEXT("PM");
    GetLocaleInfo(LOCALE_USER_DEFAULT, LOCALE_S1159, am, _countof(am));
    GetLocaleInfo(LOCALE_USER_DEFAULT, LOCALE_S2359, pm, _countof(pm));

    bool isPM = CW_ContainsNoCase(buf, pm);
    bool isAM = CW_ContainsNoCase(buf, am);
    int h = _ttoi(buf);
    if (isPM && h != 12) h += 12;
    if (isAM && h == 12) h  = 0;
    if (h < 0)  h = 0;
    if (h > 23) h = 23;
    return h;
}

/* Write minute always zero-padded ("00"–"59"). */
inline void CW_WriteMinuteToEdit(HWND edit, int minute)
{
    if (!edit) return;
    TCHAR buf[8];
    wsprintf(buf, TEXT("%02d"), minute);
    SetWindowText(edit, buf);
}
