/*
 * ClamWin Free Antivirus - mnemonic drawing helpers
 *
 * Draw owner-drawn labels with accelerator underlines always visible,
 * independent of current UI cue state.
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

#pragma once
#include <windows.h>
#include <tchar.h>
#include <ctype.h>
#include <string>
#include "cw_dpi.h"

inline void CW_ParseMnemonicText(const TCHAR* text, std::basic_string<TCHAR>& plain, int& accelIndex)
{
    plain.clear();
    accelIndex = -1;
    if (!text)
        return;

    for (int i = 0; text[i]; ++i)
    {
        TCHAR c = text[i];
        if (c == TEXT('&'))
        {
            if (text[i + 1] == TEXT('&'))
            {
                plain.push_back(TEXT('&'));
                ++i;
                continue;
            }

            if (text[i + 1] && accelIndex < 0)
                accelIndex = (int)plain.size();
            continue;
        }
        plain.push_back(c);
    }
}

inline void CW_DrawMnemonicTextAlways(HDC hdc,
                                      HFONT hFont,
                                      const RECT& rc,
                                      const TCHAR* text,
                                      UINT drawFlags,
                                      bool showMnemonics = true)
{
    if (!hdc)
        return;

    if (!showMnemonics)
    {
        HFONT oldFont = NULL;
        if (hFont)
            oldFont = (HFONT)SelectObject(hdc, hFont);

        RECT textRc = rc;
        DrawText(hdc, text ? text : TEXT(""), -1, &textRc, drawFlags | DT_HIDEPREFIX);

        if (oldFont)
            SelectObject(hdc, oldFont);
        return;
    }

    std::basic_string<TCHAR> plain;
    int accelIndex = -1;
    CW_ParseMnemonicText(text, plain, accelIndex);

    HFONT oldFont = NULL;
    if (hFont)
        oldFont = (HFONT)SelectObject(hdc, hFont);

    RECT textRc = rc;
    DrawText(hdc, plain.c_str(), -1, &textRc, drawFlags);

    if (accelIndex >= 0 && accelIndex < (int)plain.size())
    {
        TEXTMETRIC tm;
        ZeroMemory(&tm, sizeof(tm));
        GetTextMetrics(hdc, &tm);

        SIZE fullSize;
        SIZE leftSize;
        SIZE charSize;
        ZeroMemory(&fullSize, sizeof(fullSize));
        ZeroMemory(&leftSize, sizeof(leftSize));
        ZeroMemory(&charSize, sizeof(charSize));

        GetTextExtentPoint32(hdc, plain.c_str(), (int)plain.size(), &fullSize);
        if (accelIndex > 0)
            GetTextExtentPoint32(hdc, plain.c_str(), accelIndex, &leftSize);
        GetTextExtentPoint32(hdc, plain.c_str() + accelIndex, 1, &charSize);

        int x = rc.left;
        if ((drawFlags & DT_CENTER) != 0)
            x = rc.left + ((rc.right - rc.left) - fullSize.cx) / 2;
        else if ((drawFlags & DT_RIGHT) != 0)
            x = rc.right - fullSize.cx;

        int gap = CW_Scale(1);
        int y = rc.top + ((rc.bottom - rc.top) - tm.tmHeight) / 2 + tm.tmAscent + gap;
        int x1 = x + leftSize.cx;
        int x2 = x1 + charSize.cx - 1;

        unsigned char mnemonicChar = (unsigned char)plain[(size_t)accelIndex];
        bool isLower = islower(mnemonicChar) != 0;
        if (isLower)
        {
            const int minUnderlineWidth = CW_Scale(8);
            int currentWidth = x2 - x1 + 1;
            if (currentWidth < minUnderlineWidth)
            {
                int grow = minUnderlineWidth - currentWidth;
                int leftGrow = grow / 2;
                int rightGrow = grow - leftGrow;
                x1 -= leftGrow;
                x2 += rightGrow;
            }
        }

        HPEN pen = CreatePen(PS_SOLID, CW_Scale(1), GetTextColor(hdc));
        HGDIOBJ oldPen = SelectObject(hdc, pen);
        MoveToEx(hdc, x1, y, NULL);
        LineTo(hdc, x2, y);
        SelectObject(hdc, oldPen);
        DeleteObject(pen);
    }

    if (oldFont)
        SelectObject(hdc, oldFont);
}

inline void CW_DrawMnemonicTextStaticLabel(HDC hdc,
                                           HFONT hFont,
                                           const RECT& rc,
                                           const TCHAR* text,
                                           UINT drawFlags,
                                           bool showMnemonics = true)
{
    if (!hdc)
        return;

    if (!showMnemonics)
    {
        HFONT oldFont = NULL;
        if (hFont)
            oldFont = (HFONT)SelectObject(hdc, hFont);

        RECT textRc = rc;
        DrawText(hdc, text ? text : TEXT(""), -1, &textRc, drawFlags | DT_HIDEPREFIX);

        if (oldFont)
            SelectObject(hdc, oldFont);
        return;
    }

    std::basic_string<TCHAR> plain;
    int accelIndex = -1;
    CW_ParseMnemonicText(text, plain, accelIndex);

    HFONT oldFont = NULL;
    if (hFont)
        oldFont = (HFONT)SelectObject(hdc, hFont);

    RECT textRc = rc;
    DrawText(hdc, plain.c_str(), -1, &textRc, drawFlags);

    if (accelIndex >= 0 && accelIndex < (int)plain.size())
    {
        TEXTMETRIC tm;
        ZeroMemory(&tm, sizeof(tm));
        GetTextMetrics(hdc, &tm);

        SIZE fullSize;
        SIZE leftSize;
        SIZE charSize;
        ZeroMemory(&fullSize, sizeof(fullSize));
        ZeroMemory(&leftSize, sizeof(leftSize));
        ZeroMemory(&charSize, sizeof(charSize));

        GetTextExtentPoint32(hdc, plain.c_str(), (int)plain.size(), &fullSize);
        if (accelIndex > 0)
            GetTextExtentPoint32(hdc, plain.c_str(), accelIndex, &leftSize);
        GetTextExtentPoint32(hdc, plain.c_str() + accelIndex, 1, &charSize);

        int x = rc.left;
        if ((drawFlags & DT_CENTER) != 0)
            x = rc.left + ((rc.right - rc.left) - fullSize.cx) / 2;
        else if ((drawFlags & DT_RIGHT) != 0)
            x = rc.right - fullSize.cx;

        int gap = CW_Scale(1);
        int y = rc.top + ((rc.bottom - rc.top) - tm.tmHeight) / 2 + tm.tmAscent + gap;
        int x1 = x + leftSize.cx;
        int x2 = x1 + charSize.cx - 1;

        const int minUnderlineWidth = CW_Scale(9);
        int currentWidth = x2 - x1 + 1;
        if (currentWidth < minUnderlineWidth)
        {
            int grow = minUnderlineWidth - currentWidth;
            int leftGrow = grow / 2;
            int rightGrow = grow - leftGrow;
            x1 -= leftGrow;
            x2 += rightGrow;
        }

        HPEN pen = CreatePen(PS_SOLID, CW_Scale(2), GetTextColor(hdc));
        HGDIOBJ oldPen = SelectObject(hdc, pen);
        MoveToEx(hdc, x1, y, NULL);
        LineTo(hdc, x2, y);
        SelectObject(hdc, oldPen);
        DeleteObject(pen);
    }

    if (oldFont)
        SelectObject(hdc, oldFont);
}