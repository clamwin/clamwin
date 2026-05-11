/*
 * ClamWin Free Antivirus — CWDashboard
 *
 * Main dashboard window: status banner + action cards.
 * Inherits CWWindow for Win32 message dispatch.
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

#pragma once
#include "cw_window.h"
#include "cw_gui_shared.h"   /* CW_Config, IDC_CARD_*, IDM_*, CW_DBInfo, CW_ProtectionStatus */
#include <tchar.h>
#include <vector>

class CWDashboard : public CWWindow
{
public:
    explicit CWDashboard(CWConfig& config);
    virtual ~CWDashboard();

    /* Create and show the window. Returns false on failure. */
    bool open(HWND parent = NULL);

    /* Refresh status banner (call after update completes). */
    void refreshStatus();

    /* Set when a newer ClamWin version is available (from CWUpdateChecker). */
    void setUpdateAvailable(const char* versionStr);
    void setLatestInstalled(const char* versionStr);
    void setVersionCheckFailed();

protected:
    /* CWWindow overrides */
    virtual bool onCreate();
    virtual void onPaint(HDC hdc);
    virtual void onCommand(int id, HWND src);
    virtual LRESULT onMessage(UINT msg, WPARAM wp, LPARAM lp);
    virtual void fillWndClass(WNDCLASS& wc);

private:
    enum VersionBannerState {
        VERSION_BANNER_NONE = 0,
        VERSION_BANNER_UPDATE_AVAILABLE,
        VERSION_BANNER_LATEST_INSTALLED,
        VERSION_BANNER_CHECK_FAILED
    };

    struct CardInfo {
        int          id;
        const TCHAR* title;
        const TCHAR* desc;
    };

    static const CardInfo s_cards[];
    static const int      s_cardCount;

    CWConfig&           m_config;
    CW_ProtectionStatus m_status;
    CW_DBInfo           m_dbInfo;
    int                 m_hoverCard;   /* -1 = none */
    bool                m_showMnemonics;
    HWND                m_hwndTooltip;
    VersionBannerState  m_versionBannerState;
    bool                m_versionBannerLayoutAdjusted;
    TCHAR               m_versionText[64];

    /* Fonts — owned, cleaned up in onDestroy */
    HFONT m_fontTitle;
    HFONT m_fontDesc;
    HFONT m_fontBanner;
    HFONT m_fontBannerSub;
    HFONT m_fontStatus;

    void createFonts();
    void destroyFonts();
    void getCardRect(int index, const RECT& client, RECT& out) const;
    bool hasVersionBanner() const { return m_versionBannerState != VERSION_BANNER_NONE; }
    void applyVersionBannerState(VersionBannerState state, const char* versionStr);
    void paintBanner(HDC hdc, const RECT& client);
    void paintCards(HDC hdc, const RECT& client);
    void paintStatusBar(HDC hdc, const RECT& client);
    void paintVersionBanner(HDC hdc, const RECT& client);
    int  cardAtPoint(POINT pt) const;
    void initCardTooltips();
    void updateCardTooltipRects();
    void destroyCardTooltips();
    void postTrayCommand(int menuId);
};
