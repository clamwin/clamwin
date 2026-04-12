/*
 * ClamWin Free Antivirus — CWAboutDialog
 *
 * Modern About dialog with themed layout, logo panels,
 * and clickable links. No DB info shown (banner has it).
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

#include "cw_about_dialog.h"
#include "cw_dpi.h"
#include "cw_theme.h"
#include <commctrl.h>
#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <string>
#include <tchar.h>

#define STBI_NO_STDIO
#define STBI_ONLY_PNG
#define STBI_NO_FAILURE_STRINGS
#define STB_IMAGE_IMPLEMENTATION
#include "3rdparty/stb/stb_image.h"

#define STB_IMAGE_RESIZE_IMPLEMENTATION
#include "3rdparty/stb/stb_image_resize2.h"

struct CWPngImage
{
    unsigned char* pixels; /* RGBA, stbi-allocated */
    int w, h;
};

#define IDC_LINK_WEB      4001
#define IDC_LINK_CLAMAV   4002
#define IDC_LINK_NETFARM  4003
#define IDC_LOGO_CLAMWIN  4101
#define IDC_LOGO_CLAMAV   4102
#define IDC_LOGO_NETFARM  4103

/* ─── Version info helpers ───────────────────────────────────── */

static std::string getFileVersion(const std::string& filePath)
{
    DWORD dummy;
    DWORD infoSize = GetFileVersionInfoSizeA(filePath.c_str(), &dummy);
    if (infoSize == 0)
        return "";

    std::vector<BYTE> infoData(infoSize);
    if (!GetFileVersionInfoA(filePath.c_str(), dummy, infoSize, infoData.data()))
        return "";

    struct LANGANDCODEPAGE {
        WORD wLanguage;
        WORD wCodePage;
    } *lpTranslate;
    UINT cbTranslate;

    if (!VerQueryValueA(infoData.data(), "\\VarFileInfo\\Translation", (LPVOID*)&lpTranslate, &cbTranslate) || cbTranslate < sizeof(LANGANDCODEPAGE))
        return "";

    char subBlock[256];
    snprintf(subBlock, sizeof(subBlock), "\\StringFileInfo\\%04x%04x\\FileVersion",
             lpTranslate[0].wLanguage, lpTranslate[0].wCodePage);

    char* lpBuffer = NULL;
    UINT cbBufSize = 0;
    if (!VerQueryValueA(infoData.data(), subBlock, (LPVOID*)&lpBuffer, &cbBufSize) || cbBufSize == 0)
        return "";

    /* Normalize "1,5,2,1" -> "1.5.2.1" (up to 4 components, dot-separated) */
    std::string raw = lpBuffer;
    std::string result;
    int nparts = 0;
    size_t start = 0;
    for (size_t i = 0; i <= raw.size() && nparts < 4; ++i)
    {
        if (i == raw.size() || raw[i] == ',' || raw[i] == '.')
        {
            if (!result.empty()) result += '.';
            while (start < i && raw[start] == ' ') ++start;
            result += raw.substr(start, i - start);
            start = i + 1;
            ++nparts;
        }
    }
    return result;
}

/* ─── PNG resource loader via stb_image ─────────────────────── */

void* CWAboutDialog::loadPngResource(int resourceId)
{
    HRSRC hRes = FindResource(GetModuleHandle(NULL), MAKEINTRESOURCE(resourceId), RT_RCDATA);
    if (!hRes) return NULL;

    HGLOBAL hLoad = LoadResource(GetModuleHandle(NULL), hRes);
    if (!hLoad) return NULL;

    const BYTE* data = (const BYTE*)LockResource(hLoad);
    DWORD size = SizeofResource(GetModuleHandle(NULL), hRes);
    if (!data || size == 0) return NULL;

    int w, h, channels;
    unsigned char* pixels = stbi_load_from_memory(data, (int)size, &w, &h, &channels, 4);
    if (!pixels) return NULL;

    CWPngImage* img = new CWPngImage;
    img->pixels = pixels;
    img->w = w;
    img->h = h;
    return img;
}

/* ─── Constructor / Destructor ──────────────────────────────── */

CWAboutDialog::CWAboutDialog(CWConfig& cfg)
    : m_cfg(cfg)
    , m_hFontTitle(NULL), m_hFontSection(NULL)
    , m_hFontNormal(NULL), m_hFontSmall(NULL), m_hFontLink(NULL)
    , m_hwndBtnOk(NULL)
    , m_hwndLinkWeb(NULL), m_hwndLinkClamAV(NULL), m_hwndLinkNetfarm(NULL)
    , m_pImgClamAV(NULL), m_pImgClamWin(NULL), m_pImgNetfarm(NULL)
{
}

CWAboutDialog::~CWAboutDialog()
{
    destroyFonts();
    destroyImages();
}

void CWAboutDialog::createFonts()
{
    m_hFontTitle = CreateFont(-CW_Scale(20), 0, 0, 0, FW_BOLD, 0, 0, 0,
                               DEFAULT_CHARSET, 0, 0, CLEARTYPE_QUALITY, 0, TEXT("Segoe UI"));
    if (!m_hFontTitle)
        m_hFontTitle = CreateFont(-CW_Scale(20), 0, 0, 0, FW_BOLD, 0, 0, 0,
                                   DEFAULT_CHARSET, 0, 0, DEFAULT_QUALITY, 0, TEXT("Tahoma"));

    m_hFontSection = CreateFont(-CW_Scale(13), 0, 0, 0, FW_SEMIBOLD, 0, 0, 0,
                                 DEFAULT_CHARSET, 0, 0, CLEARTYPE_QUALITY, 0, TEXT("Segoe UI"));
    if (!m_hFontSection)
        m_hFontSection = CreateFont(-CW_Scale(13), 0, 0, 0, FW_SEMIBOLD, 0, 0, 0,
                                     DEFAULT_CHARSET, 0, 0, DEFAULT_QUALITY, 0, TEXT("Tahoma"));

    m_hFontNormal = CreateFont(-CW_Scale(12), 0, 0, 0, FW_NORMAL, 0, 0, 0,
                                DEFAULT_CHARSET, 0, 0, CLEARTYPE_QUALITY, 0, TEXT("Segoe UI"));
    if (!m_hFontNormal)
        m_hFontNormal = CreateFont(-CW_Scale(12), 0, 0, 0, FW_NORMAL, 0, 0, 0,
                                    DEFAULT_CHARSET, 0, 0, DEFAULT_QUALITY, 0, TEXT("Tahoma"));

    m_hFontSmall = CreateFont(-CW_Scale(11), 0, 0, 0, FW_NORMAL, 0, 0, 0,
                               DEFAULT_CHARSET, 0, 0, CLEARTYPE_QUALITY, 0, TEXT("Segoe UI"));
    if (!m_hFontSmall)
        m_hFontSmall = CreateFont(-CW_Scale(11), 0, 0, 0, FW_NORMAL, 0, 0, 0,
                                   DEFAULT_CHARSET, 0, 0, DEFAULT_QUALITY, 0, TEXT("Tahoma"));

    m_hFontLink = CreateFont(-CW_Scale(12), 0, 0, 0, FW_NORMAL, TRUE, 0, 0,
                              DEFAULT_CHARSET, 0, 0, CLEARTYPE_QUALITY, 0, TEXT("Segoe UI"));
    if (!m_hFontLink)
        m_hFontLink = CreateFont(-CW_Scale(12), 0, 0, 0, FW_NORMAL, TRUE, 0, 0,
                                  DEFAULT_CHARSET, 0, 0, DEFAULT_QUALITY, 0, TEXT("Tahoma"));
}

void CWAboutDialog::destroyFonts()
{
    auto del = [](HFONT& hf) {
        if (hf) { DeleteObject(hf); hf = NULL; }
    };
    del(m_hFontTitle);
    del(m_hFontSection);
    del(m_hFontNormal);
    del(m_hFontSmall);
    del(m_hFontLink);
}

void CWAboutDialog::destroyImages()
{
    auto del = [](void*& ptr) {
        if (ptr)
        {
            CWPngImage* img = static_cast<CWPngImage*>(ptr);
            stbi_image_free(img->pixels);
            delete img;
            ptr = NULL;
        }
    };
    del(m_pImgClamAV);
    del(m_pImgClamWin);
    del(m_pImgNetfarm);
}

/* ─── Control helpers ───────────────────────────────────────── */

HWND CWAboutDialog::addLabel(LPCTSTR text, int x, int y, int w, int h, HFONT font, int id)
{
    HWND hw = CreateWindowEx(0, TEXT("STATIC"), text,
                              WS_CHILD | WS_VISIBLE | SS_NOPREFIX,
                              x, y, w, h, m_hwnd,
                              id ? (HMENU)(INT_PTR)id : NULL,
                              GetModuleHandle(NULL), NULL);
    if (hw && font) SendMessage(hw, WM_SETFONT, (WPARAM)font, 0);
    return hw;
}

HWND CWAboutDialog::addLink(LPCTSTR text, int x, int y, int w, int h, HFONT font, int id)
{
    HWND hw = CreateWindowEx(0, TEXT("STATIC"), text,
                              WS_CHILD | WS_VISIBLE | SS_NOPREFIX | SS_NOTIFY,
                              x, y, w, h, m_hwnd,
                              (HMENU)(INT_PTR)id,
                              GetModuleHandle(NULL), NULL);
    if (hw && font) SendMessage(hw, WM_SETFONT, (WPARAM)font, 0);
    return hw;
}

HWND CWAboutDialog::addBitmap(int id, int x, int y, int w, int h)
{
    HWND hw = CreateWindowEx(0, TEXT("STATIC"), NULL,
                              WS_CHILD | WS_VISIBLE | SS_OWNERDRAW,
                              x, y, w, h, m_hwnd,
                              (HMENU)(INT_PTR)id, GetModuleHandle(NULL), NULL);
    return hw;
}

/* ─── onInit ────────────────────────────────────────────────── */

bool CWAboutDialog::onInit()
{
    createFonts();

    /* Load logo images from embedded resources */
    m_pImgClamWin  = loadPngResource(IDB_CLAMWIN_LOGO);
    m_pImgClamAV   = loadPngResource(IDB_CLAMAV_LOGO);
    m_pImgNetfarm  = loadPngResource(IDB_NETFARM_LOGO);

    /* Set window icon to force left margin spacing in the title bar */
    HICON hIcon = LoadIcon(GetModuleHandle(NULL), MAKEINTRESOURCE(100)); // 100 is clamwin.ico in clamwin.rc
    if (hIcon)
    {
        SendMessage(m_hwnd, WM_SETICON, ICON_BIG, (LPARAM)hIcon);
        SendMessage(m_hwnd, WM_SETICON, ICON_SMALL, (LPARAM)hIcon);
    }

    const int dlgW = CW_Scale(520);
    const int pad = CW_Scale(32);
    
    /* Layout grid coordinates */
    const int iconSize = CW_Scale(64);
    const int textX = pad + iconSize + CW_Scale(20);
    const int contentW = dlgW - textX - pad;
    const int contentRight = dlgW - pad;

    int y = CW_Scale(20);

    /* Header block */
    int yClamWin = y;
    addLabel(TEXT("ClamWin Free Antivirus"), textX, y, contentW, CW_Scale(28), m_hFontTitle);
    y += CW_Scale(30);

    /* Retrieve ClamWin version from resources */
    char exePath[MAX_PATH];
    std::string exeDir;
    std::string versionStr = CLAMWIN_VERSION_STR;
    if (GetModuleFileNameA(NULL, exePath, MAX_PATH))
    {
        std::string ver = getFileVersion(exePath);
        if (!ver.empty())
            versionStr = ver;

        char* lastSlash = strrchr(exePath, '\\');
        if (lastSlash)
            exeDir = std::string(exePath, lastSlash + 1);
    }

    std::basic_string<TCHAR> verLabel = TEXT("Version ");
    verLabel += versionStr;
    addLabel(verLabel.c_str(), textX, y, contentW, CW_Scale(18), m_hFontNormal);
    y += CW_Scale(18);
    m_hwndLinkWeb = addLink(TEXT(CLAMWIN_WEBSITE), textX, y, contentW, CW_Scale(18),
                            m_hFontLink, IDC_LINK_WEB);
    y += CW_Scale(26); /* Increased from 20 for more space below text block */

    int hClamWin = y - yClamWin;
    addBitmap(IDC_LOGO_CLAMWIN, pad, yClamWin + (hClamWin - iconSize)/2, iconSize, iconSize);

    CreateWindowEx(0, TEXT("STATIC"), NULL, WS_CHILD | WS_VISIBLE | SS_ETCHEDHORZ,
                    pad, y, contentRight - pad, CW_Scale(1), m_hwnd,
                    NULL, GetModuleHandle(NULL), NULL);
    y += CW_Scale(18);

    /* Scanning Engine row */
    int yClamAV = y;
    addLabel(TEXT("Scanning Engine"), textX, y, contentW, CW_Scale(20), m_hFontSection);
    y += CW_Scale(20);
    std::string clamavLabel = "Powered by ClamAV";
    if (!exeDir.empty())
    {
        std::string clamavVer = getFileVersion(exeDir + "libclamav.dll");
        if (!clamavVer.empty())
            clamavLabel += " " + clamavVer;
    }
    clamavLabel += ", maintained by Cisco Talos";
    addLabel(clamavLabel.c_str(), textX, y, contentW, CW_Scale(18), m_hFontNormal);
    y += CW_Scale(18);
    m_hwndLinkClamAV = addLink(TEXT("https://www.clamav.net"), textX, y, contentW, CW_Scale(18),
                               m_hFontLink, IDC_LINK_CLAMAV);
    y += CW_Scale(26); /* Increased */

    int hClamAV = y - yClamAV;
    addBitmap(IDC_LOGO_CLAMAV, pad, yClamAV + (hClamAV - iconSize)/2, iconSize, iconSize);

    CreateWindowEx(0, TEXT("STATIC"), NULL, WS_CHILD | WS_VISIBLE | SS_ETCHEDHORZ,
                    pad, y, contentRight - pad, CW_Scale(1), m_hwnd,
                    NULL, GetModuleHandle(NULL), NULL);
    y += CW_Scale(18); /* Increased */

    /* Legacy port row */
    int yNetfarm = y;
    addLabel(TEXT("Legacy Windows Ports"), textX, y, contentW, CW_Scale(20), m_hFontSection);
    y += CW_Scale(20);
    addLabel(TEXT("Netfarm S.r.l."), textX, y, contentW, CW_Scale(18), m_hFontNormal);
    y += CW_Scale(18);
    m_hwndLinkNetfarm = addLink(TEXT("https://oss.netfarm.it/clamav/"), textX, y, contentW, CW_Scale(18),
                                m_hFontLink, IDC_LINK_NETFARM);
    y += CW_Scale(26); /* Increased */

    int hNetfarm = y - yNetfarm;
    
    /* Optically align Netfarm logo (which has no internal padding) to match ClamAV visual weight */
    const int netfarmSize = CW_Scale(46);
    const int netfarmX = pad + (iconSize - netfarmSize) / 2;
    addBitmap(IDC_LOGO_NETFARM, netfarmX, yNetfarm + (hNetfarm - netfarmSize)/2, netfarmSize, netfarmSize);

    CreateWindowEx(0, TEXT("STATIC"), NULL, WS_CHILD | WS_VISIBLE | SS_ETCHEDHORZ,
                    pad, y, contentRight - pad, CW_Scale(1), m_hwnd,
                    NULL, GetModuleHandle(NULL), NULL);
    y += CW_Scale(18); /* Increased */

    /* Authors row */
    addLabel(TEXT("Authors"), textX, y, contentW, CW_Scale(20), m_hFontSection);
    y += CW_Scale(20);
    addLabel(TEXT("Alex Cherney <alex@clamwin.com>"), textX, y, contentW, CW_Scale(18), m_hFontNormal);
    y += CW_Scale(18);
    addLabel("Gianluigi Tiesi <sherpya@gmail.com>", textX, y, contentW, CW_Scale(18), m_hFontNormal);
    y += CW_Scale(26); /* Increased */

    CreateWindowEx(0, TEXT("STATIC"), NULL, WS_CHILD | WS_VISIBLE | SS_ETCHEDHORZ,
                    pad, y, contentRight - pad, CW_Scale(1), m_hwnd,
                    NULL, GetModuleHandle(NULL), NULL);
    y += CW_Scale(18); /* Increased */

    /* Centered legal text */
    {
        HWND h = addLabel(TEXT("Copyright ClamWin Pty Ltd (c) 2004-2026\n"
                  "Portions Copyright Cisco Inc. (ClamAV)\n"
                  "ClamWin is not affiliated with ClamAV or Cisco Inc."), 
                          pad, y, contentRight - pad, CW_Scale(56), m_hFontSmall);
        if (h) {
            SetWindowLongPtr(h, GWL_STYLE, GetWindowLongPtr(h, GWL_STYLE) | SS_CENTER);
            SetWindowLongPtr(h, GWLP_ID, 4201);
        }
    }
    y += CW_Scale(60); 
    {
        HWND h = addLabel(TEXT("This program is free software; you can redistribute it and/or modify "
                  "it under the terms of the GNU General Public License (GPLv2)."),
                          pad, y, contentRight - pad, CW_Scale(40), m_hFontSmall); /* Increased height to 40 so it doesn't clip */
        if (h) {
            SetWindowLongPtr(h, GWL_STYLE, GetWindowLongPtr(h, GWL_STYLE) | SS_CENTER);
            SetWindowLongPtr(h, GWLP_ID, 4201);
        }
    }
    y += CW_Scale(46); /* Increased space explicitly above OK button to un-overlap it */

    /* ── OK button ──────────────────────────────────────────── */
    m_hwndBtnOk = CreateWindowEx(0, TEXT("BUTTON"), TEXT("&OK"),
                                  WS_CHILD | WS_VISIBLE | WS_TABSTOP | BS_DEFPUSHBUTTON | BS_OWNERDRAW,
                                  (dlgW - CW_Scale(96)) / 2, y,
                                  CW_Scale(96), CW_Scale(30),
                                  m_hwnd, (HMENU)IDOK, GetModuleHandle(NULL), NULL);
    SendMessage(m_hwndBtnOk, WM_SETFONT, (WPARAM)m_hFontNormal, 0);

    SetWindowText(m_hwnd, TEXT("About ClamWin Free Antivirus"));
    SetFocus(m_hwndBtnOk);
    return false; /* Did set focus ourselves */
}

/* ─── onCommand ─────────────────────────────────────────────── */

bool CWAboutDialog::onCommand(int id, HWND src)
{
    (void)src;
    switch (id)
    {
        case IDOK:
        case IDCANCEL:
            endDialog(id);
            return true;

        case IDC_LINK_WEB:
            ShellExecute(m_hwnd, TEXT("open"), TEXT(CLAMWIN_WEBSITE), NULL, NULL, SW_SHOWNORMAL);
            return true;

        case IDC_LINK_CLAMAV:
            ShellExecute(m_hwnd, TEXT("open"), TEXT("https://www.clamav.net"), NULL, NULL, SW_SHOWNORMAL);
            return true;

        case IDC_LINK_NETFARM:
            ShellExecute(m_hwnd, TEXT("open"), TEXT("https://oss.netfarm.it/clamav/"), NULL, NULL, SW_SHOWNORMAL);
            return true;
    }
    return false;
}

/* ─── handleMessage — custom painting for links ─────────────── */

INT_PTR CWAboutDialog::handleMessage(UINT msg, WPARAM wp, LPARAM lp)
{
    switch (msg)
    {
        case WM_DRAWITEM:
        {
            DRAWITEMSTRUCT* dis = reinterpret_cast<DRAWITEMSTRUCT*>(lp);
            if (!dis || dis->CtlType != ODT_STATIC)
                break;

            void* ptrImg = NULL;
            if (dis->CtlID == IDC_LOGO_CLAMWIN) ptrImg = m_pImgClamWin;
            else if (dis->CtlID == IDC_LOGO_CLAMAV) ptrImg = m_pImgClamAV;
            else if (dis->CtlID == IDC_LOGO_NETFARM) ptrImg = m_pImgNetfarm;
            else break;

            CWTheme* theme = CW_GetTheme();
            COLORREF bg = theme ? theme->colorBg() : GetSysColor(COLOR_3DFACE);
            HBRUSH hBg = CreateSolidBrush(bg);
            FillRect(dis->hDC, &dis->rcItem, hBg);
            DeleteObject(hBg);

            if (ptrImg)
            {
                CWPngImage* img = static_cast<CWPngImage*>(ptrImg);

                const int rcW = dis->rcItem.right - dis->rcItem.left;
                const int rcH = dis->rcItem.bottom - dis->rcItem.top;

                float scaleX = (float)rcW / (float)img->w;
                float scaleY = (float)rcH / (float)img->h;
                float scale  = (scaleX < scaleY) ? scaleX : scaleY;
                if (scale > 1.0f) scale = 1.0f;

                int drawW = (int)(img->w * scale);
                int drawH = (int)(img->h * scale);
                if (drawW < 1) drawW = 1;
                if (drawH < 1) drawH = 1;

                int x = dis->rcItem.left + (rcW - drawW) / 2;
                int y = dis->rcItem.top  + (rcH - drawH) / 2;

                /* Resize to target dimensions with bicubic quality */
                unsigned char* resized = (unsigned char*)malloc((size_t)drawW * drawH * 4);
                if (resized)
                {
                    stbir_resize_uint8_linear(img->pixels, img->w, img->h, 0,
                                              resized, drawW, drawH, 0,
                                              STBIR_RGBA);

                    /* Pre-composite RGBA against solid background — no AlphaBlend needed */
                    int bgR = GetRValue(bg), bgG = GetGValue(bg), bgB = GetBValue(bg);

                    BITMAPINFOHEADER bih;
                    ZeroMemory(&bih, sizeof(bih));
                    bih.biSize        = sizeof(bih);
                    bih.biWidth       = drawW;
                    bih.biHeight      = -drawH; /* top-down */
                    bih.biPlanes      = 1;
                    bih.biBitCount    = 32;
                    bih.biCompression = BI_RGB;

                    void* dibBits = NULL;
                    HDC hdcMem = CreateCompatibleDC(dis->hDC);
                    HBITMAP hBmp = CreateDIBSection(dis->hDC,
                                                    (BITMAPINFO*)&bih,
                                                    DIB_RGB_COLORS,
                                                    &dibBits, NULL, 0);
                    if (hBmp && dibBits)
                    {
                        unsigned char* dst = (unsigned char*)dibBits;
                        const unsigned char* src = resized;
                        const int npix = drawW * drawH;
                        for (int i = 0; i < npix; ++i)
                        {
                            unsigned int a = src[3];
                            unsigned int ia = 255 - a;
                            dst[0] = (unsigned char)((src[2] * a + bgB * ia) / 255);
                            dst[1] = (unsigned char)((src[1] * a + bgG * ia) / 255);
                            dst[2] = (unsigned char)((src[0] * a + bgR * ia) / 255);
                            dst[3] = 0;
                            src += 4;
                            dst += 4;
                        }

                        HGDIOBJ old = SelectObject(hdcMem, hBmp);
                        BitBlt(dis->hDC, x, y, drawW, drawH, hdcMem, 0, 0, SRCCOPY);
                        SelectObject(hdcMem, old);
                        DeleteObject(hBmp);
                    }
                    if (hdcMem) DeleteDC(hdcMem);
                    free(resized);
                }
            }
            return TRUE;
        }

        case WM_CTLCOLORSTATIC:
        {
            HWND ctrl = (HWND)lp;
            HDC hdc = (HDC)wp;
            CWTheme* theme = CW_GetTheme();
            int ctlId = GetWindowLong(ctrl, GWL_ID);

            /* Color link controls blue */
            if (ctrl == m_hwndLinkWeb || ctrl == m_hwndLinkClamAV || ctrl == m_hwndLinkNetfarm)
            {
                SetBkMode(hdc, TRANSPARENT);
                SetTextColor(hdc, theme ? theme->colorAccent() : RGB(0, 102, 204));
                return (INT_PTR)(theme ? theme->brushBg() : GetStockObject(WHITE_BRUSH));
            }
            else if (ctlId == 4201) /* Muted text */
            {
                SetBkMode(hdc, TRANSPARENT);
                SetTextColor(hdc, theme ? theme->colorTextMuted() : RGB(128, 128, 128));
                return (INT_PTR)(theme ? theme->brushBg() : GetStockObject(WHITE_BRUSH));
            }
            break;
        }

        case WM_SETCURSOR:
        {
            HWND ctrl = (HWND)wp;
            if (ctrl == m_hwndLinkWeb || ctrl == m_hwndLinkClamAV || ctrl == m_hwndLinkNetfarm)
            {
                SetCursor(LoadCursor(NULL, IDC_HAND));
                return TRUE;
            }
            break;
        }
    }

    return CWDialog::handleMessage(msg, wp, lp);
}

/* ─── C Wrapper ─────────────────────────────────────────────── */
void CW_AboutDialogRun(HWND hwndParent, CWConfig *cfg)
{
    CWAboutDialog dlg(*cfg);
    dlg.runModal(hwndParent, 520, 515);
}
