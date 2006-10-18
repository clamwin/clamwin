/*-----------------------------------------------------------------------------
# Name:        BalloonHelp.cpp
# Product:     ClamWin Antivirus
#
# Licence:
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#-----------------------------------------------------------------------------

# 11 May 2004 Alch - Converted the class to pure win32 api - no MFC
*/

// ******************************************************************************

// BalloonHelp.cpp : implementation file
// Copyright 2001-2002, Joshua Heyer
//  You are free to use this code for whatever you want, provided you
// give credit where credit is due.  (I seem to get a lot of questions
// about that statement...  All i mean is, don't copy huge bits of code
// and then claim you wrote it.  You don't have to put my name in an about
// box or anything.  Though i'm not going to stop you if that's really what
// you want :~) )
//  I'm providing this code in the hope that it is useful to someone, as i have
// gotten much use out of other peoples code over the years.
//  If you see value in it, make some improvements, etc., i would appreciate it
// if you sent me some feedback.
//
// ******************************************************************************

#include "stdafx.h"
#include "BalloonHelp.h"

// allow multimonitor-aware code on Win95 systems
// comment out the first line if you have already define it in another file
// comment out both lines if you don't care about Win95
//#define COMPILE_MULTIMON_STUBS
//#include "multimon.h"


//
// constants that may not be defined if you don't have the latest SDK
// (but i like to use them anyway)
//

#ifndef DFCS_HOT
#define DFCS_HOT 0x1000
#endif

#ifndef AW_HIDE
#define AW_HIDE 0x00010000
#define AW_BLEND 0x00080000
#endif

#ifndef CS_DROPSHADOW
#define CS_DROPSHADOW   0x00020000
#endif

#ifndef SPI_GETDROPSHADOW
#define SPI_GETDROPSHADOW  0x1024
#endif

#ifndef SPI_GETTOOLTIPANIMATION
#define SPI_GETTOOLTIPANIMATION 0x1016
#endif

#ifndef SPI_GETTOOLTIPFADE
#define SPI_GETTOOLTIPFADE 0x1018
#endif

/////////////////////////////////////////////////////////////////////////////
// CBalloonHelp

// option constants (bits)
const unsigned int   CBalloonHelp::unCLOSE_ON_LBUTTON_UP    = 0x0001;
const unsigned int   CBalloonHelp::unCLOSE_ON_MBUTTON_UP    = 0x0002;
const unsigned int   CBalloonHelp::unCLOSE_ON_RBUTTON_UP    = 0x0004;
const unsigned int   CBalloonHelp::unCLOSE_ON_LBUTTON_DOWN  = 0x0008;
const unsigned int   CBalloonHelp::unCLOSE_ON_MBUTTON_DOWN  = 0x0010;
const unsigned int   CBalloonHelp::unCLOSE_ON_RBUTTON_DOWN  = 0x0020;
const unsigned int   CBalloonHelp::unCLOSE_ON_MOUSE_MOVE    = 0x0040;
const unsigned int   CBalloonHelp::unCLOSE_ON_KEYPRESS      = 0x0080;
const unsigned int   CBalloonHelp::unCLOSE_ON_ANYTHING      = CBalloonHelp::unCLOSE_ON_MOUSE_MOVE|CBalloonHelp::unCLOSE_ON_RBUTTON_DOWN|CBalloonHelp::unCLOSE_ON_RBUTTON_DOWN|CBalloonHelp::unCLOSE_ON_MBUTTON_DOWN|CBalloonHelp::unCLOSE_ON_LBUTTON_DOWN|CBalloonHelp::unCLOSE_ON_RBUTTON_UP|CBalloonHelp::unCLOSE_ON_MBUTTON_UP|CBalloonHelp::unCLOSE_ON_LBUTTON_UP;
const unsigned int   CBalloonHelp::unDELAY_CLOSE            = 0x0100;
const unsigned int   CBalloonHelp::unDELETE_THIS_ON_CLOSE   = 0x0200;
const unsigned int   CBalloonHelp::unSHOW_CLOSE_BUTTON      = 0x0400;
const unsigned int   CBalloonHelp::unSHOW_INNER_SHADOW      = 0x0800;
const unsigned int   CBalloonHelp::unSHOW_TOPMOST           = 0x1000;
const unsigned int   CBalloonHelp::unDISABLE_XP_SHADOW      = 0x2000;
const unsigned int   CBalloonHelp::unDISABLE_FADEIN         = 0x4000;
const unsigned int   CBalloonHelp::unDISABLE_FADEOUT        = 0x8000;
const unsigned int   CBalloonHelp::unDISABLE_FADE           = CBalloonHelp::unDISABLE_FADEIN|CBalloonHelp::unDISABLE_FADEOUT;

// layout constants (should prolly be configurable, but who's really gonna care?)
const int            CBalloonHelp::nTIP_TAIL             = 20;
const int            CBalloonHelp::nTIP_MARGIN           = 8;
// class atom (why don't i do this the MFC way?  Drop shadows!)
ATOM                 CBalloonHelp::s_ClassAtom           = 0;
ATOM                 CBalloonHelp::s_ClassAtomShadowed   = 0;

// Kill timer
#define ID_TIMER_CLOSE  1

extern HINSTANCE g_hInstance;

//
// The launchers
//
//
// Show a help balloon on screen
// Parameters:
//    strTitle    |  Title of balloon
//    unTitle     |  Title of balloon (id of string resource)
//    strContent  |  Content of balloon
//    unContent   |  Content of balloon (id of string resource)
//    ptAnchor    |  point tail of balloon will be "anchor"ed to
//    szIcon      |  One of:
//                   IDI_APPLICATION
//                   IDI_INFORMATION IDI_ASTERISK (same)
//                   IDI_ERROR IDI_HAND (same)
//                   IDI_EXCLAMATION IDI_WARNING (same)
//                   IDI_QUESTION
//                   IDI_WINLOGO
//                   NULL (no icon)
//    unIconID    |  ID of icon to display (loaded from resources)
//    unOptions   |  One or more of:
//                :     unCLOSE_ON_LBUTTON_UP   |  closes window on WM_LBUTTON_UP
//                :     unCLOSE_ON_MBUTTON_UP   |  closes window on WM_MBUTTON_UP
//                :     unCLOSE_ON_RBUTTON_UP   |  closes window on WM_RBUTTON_UP
//                :     unCLOSE_ON_LBUTTON_DOWN |  closes window on WM_LBUTTON_DOWN
//                :     unCLOSE_ON_MBUTTON_DOWN |  closes window on WM_MBUTTON_DOWN
//                :     unCLOSE_ON_RBUTTON_DOWN |  closes window on WM_RBUTTON_DOWN
//                :     unCLOSE_ON_MOUSE_MOVE   |  closes window when user moves mouse past threshhold
//                :     unCLOSE_ON_KEYPRESS     |  closes window on the next keypress message sent to this thread.
//                :     unCLOSE_ON_ANYTHING     |  all of the above.
//                :     unDELAY_CLOSE           |  when a user action triggers the close, begins timer.  closes when timer expires.
//                :     unSHOW_CLOSE_BUTTON     |  shows close button in upper right
//                :     unSHOW_INNER_SHADOW     |  draw inner shadow in balloon
//                :     unSHOW_TOPMOST          |  place balloon above all other windows
//                :     unDISABLE_XP_SHADOW     |  disable Windows XP's drop-shadow effect (overrides system and user settings)
//                :     unDISABLE_FADE          |  disable the fade-in/fade-out effects (overrides system and user settings)
//                :     unDISABLE_FADEIN        |  disable the fade-in effect
//                :     unDISABLE_FADEOUT       |  disable the fade-out effect
//    pParentWnd  |  Parent window.  If NULL will be set to AfxGetMainWnd(), and anchor to screen
//    strURL      |  If not empty, when the balloon is clicked ShellExecute() will
//                |  be called, with strURL passed in.
//    unTimeout   |  If not 0, balloon will automatically close after unTimeout milliseconds.
//
void CBalloonHelp::LaunchBalloon(const CStdString& strTitle, const CStdString& strContent,
               POINT& ptAnchor,
               LPCTSTR szIcon /*= IDI_EXCLAMATION*/,
               unsigned int unOptions /*= unSHOW_CLOSE_BUTTON*/,
               HWND hParentWnd /*= NULL*/,
               const CStdString strURL /*= ""*/,
               unsigned int unTimeout /*= 10000*/)
{
   CBalloonHelp* pbh = new CBalloonHelp;
   if ( NULL != szIcon )
   {
      // Note: Since i'm scaling the icon anyway, i'll allow it to become larger
      // than the standard small icon if the close button is.
      SIZE sizeIcon = {max(::GetSystemMetrics(SM_CXSIZE), ::GetSystemMetrics(SM_CXSMICON)), max(::GetSystemMetrics(SM_CYSIZE), ::GetSystemMetrics(SM_CYSMICON))};
      HICON hIcon = (HICON)::LoadImage(NULL, szIcon, IMAGE_ICON, sizeIcon.cx, sizeIcon.cy, LR_SHARED);
      if (NULL != hIcon)
         pbh->SetIconScaled(hIcon, sizeIcon.cx, sizeIcon.cy);
   }
   pbh->Create(strTitle, strContent, ptAnchor, unOptions|unDELETE_THIS_ON_CLOSE,
               hParentWnd, strURL, unTimeout, NULL);
}


//
//  The class
//

CBalloonHelp::CBalloonHelp()
:  CWnd(g_hInstance),
	m_fnAnimateWindow(NULL),
   m_unOptions(0),
   m_unTimeout(0),
   m_unTimerClose(0),
   m_strURL(""),
	m_hilIcon(NULL),
   m_hwndAnchor(NULL),
	m_hrgnComplete(NULL),
   m_strContent(""),
   m_nMouseMoveTolerance(3),     // later retrieved from system
   m_uCloseState(0),
   m_hTitleFont(NULL),
   m_hContentFont(NULL),
   m_crForeground(::GetSysColor(COLOR_INFOTEXT)),
   m_crBackground(::GetSysColor(COLOR_INFOBK)),
   m_hKeyboardHook(NULL),
   m_hMouseHook(NULL),
   m_hCallWndRetHook(NULL)
{
	m_ptAnchor.x = m_ptAnchor.y = 0;
	m_ptMouseOrig.x = m_ptMouseOrig.y = 0;
	m_screenRect.top = m_screenRect.left = m_screenRect.bottom = m_screenRect.right = 0;

   // retrieve window animation API if available
   HMODULE hUser32 = GetModuleHandle(_T("USER32.DLL"));
   // can't imagine why that would fail, but might as well *look* safe...  ;~)
   if ( NULL != hUser32 )
      m_fnAnimateWindow = (FN_ANIMATE_WINDOW)GetProcAddress(hUser32, _T("AnimateWindow"));
   else
      m_fnAnimateWindow = NULL;

   // get system tolerance values
   int nTol = 0;
   if ( ::SystemParametersInfo(SPI_GETMOUSEHOVERWIDTH, 0, &nTol, 0) && nTol > 0 )
      m_nMouseMoveTolerance = nTol;

   // setup hook procedures
   BHKeybHookThunk<CBalloonHelp>::InitThunk((TMFP)&CBalloonHelp::KeyboardHookProc, this);
   BHMouseHookThunk<CBalloonHelp>::InitThunk((TMFP)&CBalloonHelp::MouseHookProc, this);
   BHCallWndRetHookThunk<CBalloonHelp>::InitThunk((TMFP)&CBalloonHelp::CallWndRetProc, this);
}

CBalloonHelp::~CBalloonHelp()
{
   if ( NULL != m_hTitleFont )
      ::DeleteObject(m_hTitleFont);
   m_hTitleFont = NULL;
   if ( NULL != m_hContentFont )
      ::DeleteObject(m_hContentFont);
   m_hContentFont = NULL;
	if ( NULL != m_hrgnComplete )
      ::DeleteObject(m_hrgnComplete);
   m_hrgnComplete = NULL;
	if ( NULL != m_hilIcon )
		::ImageList_Destroy(m_hilIcon);
	m_hilIcon = NULL;
}


// Sets the font used for drawing the balloon title.  Deleted by balloon, do not use CFont* after passing to this function.
void CBalloonHelp::SetTitleFont(HFONT hFont)
{
   if ( NULL != m_hTitleFont )
      ::DeleteObject(m_hTitleFont);
   m_hTitleFont = hFont;
   // if already visible, resize & move
   if ( NULL != m_hWnd )
      PositionWindow();
}

// Sets the font used for drawing the balloon content.  Deleted by balloon, do not use CFont* after passing to this function.
void CBalloonHelp::SetContentFont(HFONT hFont)
{
   if ( NULL != m_hContentFont )
      ::DeleteObject(m_hContentFont);
   m_hContentFont = hFont;
   // if already visible, resize & move
   if ( NULL != m_hWnd )
      PositionWindow();
}

// Sets the icon displayed in the top left of the balloon (pass NULL to hide icon)
void CBalloonHelp::SetIcon(HICON hIcon)
{
   if ( NULL != m_hilIcon )
		::ImageList_Destroy(m_hilIcon);

   ICONINFO iconinfo;
   if ( NULL != hIcon && ::GetIconInfo(hIcon, &iconinfo) )
   {
      SetIcon(iconinfo.hbmColor, iconinfo.hbmMask);
      ::DeleteObject(iconinfo.hbmColor);
      ::DeleteObject(iconinfo.hbmMask);
   }
   // if already visible, resize & move (icon size may have changed)
   if ( NULL != m_hWnd )
      PositionWindow();
}

// Sets the icon displayed in the top left of the balloon (pass NULL to hide icon)
void CBalloonHelp::SetIconScaled(HICON hIcon, int cx, int cy)
{
   // i now have two device contexts and two bitmaps.
   // i will select a bitmap in each device context,
   // draw the icon into the first one,
   // scale it into the second one,
   // and set the second one as the balloon icon.
   // This is a rather long process to get a scaled icon,
   // but ensures maximum compatibility between different
   // versions of Windows, while producing the best possible
   // results on each version (quite good in WinNT and better, sorta ok in Win9x).
   ICONINFO iconinfo;
   if ( NULL != hIcon && ::GetIconInfo(hIcon, &iconinfo) )
   {
      BITMAP bm;
      if (::GetObject(iconinfo.hbmColor, sizeof(bm),(LPVOID)&bm))
      {
         HDC dc;
         HDC dcTmp1;
         HDC dcTmp2;
         HBITMAP bmpIcon;
         HBITMAP bmpIconScaled;
         dc = ::GetDC(NULL);
         dcTmp1 = ::CreateCompatibleDC(dc);
         dcTmp2 = ::CreateCompatibleDC(dc);
         bmpIcon = ::CreateCompatibleBitmap(dc, bm.bmWidth, bm.bmHeight);
         bmpIconScaled = CreateCompatibleBitmap(dc, cx, cy);
         ::ReleaseDC(NULL, dc);

         HBITMAP pbmpOld1 = (HBITMAP)SelectObject(dcTmp1, bmpIcon);
         HBITMAP pbmpOld2 = (HBITMAP)SelectObject(dcTmp2, bmpIconScaled);
			HBRUSH hBrush = ::CreateSolidBrush(m_crBackground);
			RECT rc = {0,0,bm.bmWidth,bm.bmHeight};
			::FillRect(dcTmp1,&rc,hBrush);
			::DeleteObject(hBrush);
         ::DrawIconEx(dcTmp1, 0,0,hIcon,bm.bmWidth,bm.bmHeight,0,NULL,DI_NORMAL);
         ::SetStretchBltMode(dcTmp2, HALFTONE);
         ::StretchBlt(dcTmp2, 0,0,cx,cy,dcTmp1, 0,0,bm.bmWidth,bm.bmHeight,SRCCOPY);
         ::SelectObject(dcTmp1, pbmpOld1);
         ::SelectObject(dcTmp2, pbmpOld2);
         SetIcon(bmpIconScaled, m_crBackground);
         ::ReleaseDC(m_hWnd, dcTmp1);
         ::ReleaseDC(m_hWnd, dcTmp2);
			::DeleteObject(dcTmp1);
			::DeleteObject(dcTmp2);
         ::DeleteObject(bmpIcon);
         ::DeleteObject(bmpIconScaled);
      }
      ::DeleteObject(iconinfo.hbmColor);
      ::DeleteObject(iconinfo.hbmMask);
   }
}

// Sets the icon displayed in the top left of the balloon (pass NULL hBitmap to hide icon)
void CBalloonHelp::SetIcon(HBITMAP hBitmap, COLORREF crMask)
{
   if ( NULL != m_hilIcon )
		::ImageList_Destroy(m_hilIcon);

   if ( NULL != hBitmap )
   {
      BITMAP bm;
      if (::GetObject(hBitmap, sizeof(bm),(LPVOID)&bm))
      {
         m_hilIcon = ::ImageList_Create(bm.bmWidth, bm.bmHeight, ILC_COLOR24|ILC_MASK,1,0);
         ::ImageList_AddMasked(m_hilIcon, hBitmap, crMask);
      }
   }
   // if already visible, resize & move (icon size may have changed)
   if ( NULL != m_hWnd )
      PositionWindow();
}

// Sets the icon displayed in the top left of the balloon
void CBalloonHelp::SetIcon(HBITMAP hBitmap, HBITMAP hMask)
{
    if ( NULL != m_hilIcon )
		::ImageList_Destroy(m_hilIcon);

   ASSERT(NULL != hBitmap);
   ASSERT(NULL != hMask);

   BITMAP bm;
   if (::GetObject(hBitmap, sizeof(bm),(LPVOID)&bm))
   {
      m_hilIcon = ::ImageList_Create(bm.bmWidth, bm.bmHeight, ILC_COLOR24|ILC_MASK,1,0);
      ::ImageList_Add(m_hilIcon, hBitmap, hMask);
   }
   // if already visible, resize & move (icon size may have changed)
   if ( NULL != m_hWnd )
      PositionWindow();
}

// Set icon displayed in the top left of the balloon to image # nIconIndex from pImageList
void CBalloonHelp::SetIcon(HIMAGELIST hImageList, int nIconIndex)
{
   // sanity checks
   ASSERT(hImageList);
   ASSERT(nIconIndex >= 0 && nIconIndex < ::ImageList_GetImageCount(hImageList));

   HICON hIcon = NULL;
   if ( NULL != hImageList && nIconIndex >= 0 && nIconIndex < ::ImageList_GetImageCount(hImageList) )
       ::ImageList_ExtractIcon(&hIcon, hImageList, nIconIndex);
   SetIcon(hIcon);
   if ( NULL != hIcon )
      ::DestroyIcon(hIcon);
   // if already visible, resize & move (icon size may have changed)
   if ( NULL != m_hWnd )
      PositionWindow();
}

// Sets the URL to be opened when balloon is clicked.  Pass "" to disable.
void CBalloonHelp::SetURL(const CStdString& strURL)
{
   m_strURL = strURL;
}

// Sets the number of milliseconds the balloon can remain open.  Set to 0 to disable timeout.
void CBalloonHelp::SetTimeout(unsigned int unTimeout)
{
   m_unTimeout = unTimeout;
   // if timer is already set, reset.
   if ( NULL != m_hWnd )
   {
      if ( m_unTimeout > 0 )
      {
         m_unTimerClose = ::SetTimer(m_hWnd, ID_TIMER_CLOSE, m_unTimeout, NULL);
      }
      else
      {
         ::KillTimer(m_hWnd, m_unTimerClose);
      }
   }
}

// Sets the point to which the balloon is "anchored"
void CBalloonHelp::SetAnchorPoint(POINT& ptAnchor, HWND hWndAnchor /*= NULL*/)
{
   m_ptAnchor = ptAnchor;
   m_hwndAnchor = hWndAnchor;

   // if we're anchored to a window, set hook
   if ( NULL != m_hwndAnchor )
      SetCallWndRetHook();
   else
      RemoveCallWndRetHook();

   // if already visible, move
   if ( NULL != m_hWnd )
   {
      // reposition
      PositionWindow();
   }
}

// Sets the title of the balloon
void CBalloonHelp::SetTitle(const CStdString& strTitle)
{
   ::SetWindowText(m_hWnd, strTitle);
   // if already visible, resize & move
   if ( NULL != m_hWnd )
      PositionWindow();
}

// Sets the content of the balloon (plain text only)
void CBalloonHelp::SetContent(const CStdString& strContent)
{
   m_strContent = strContent;
   // if already visible, resize & move
   if ( NULL != m_hWnd )
      PositionWindow();
}

// Sets the forground (text and border) color of the balloon
void CBalloonHelp::SetForegroundColor(COLORREF crForeground)
{
   m_crForeground = crForeground;
   // repaint if visible
   if ( NULL != m_hWnd )
      ::InvalidateRect(m_hWnd, NULL, FALSE);
}

// Sets the background color of the balloon
void CBalloonHelp::SetBackgroundColor(COLORREF crBackground)
{
   m_crBackground = crBackground;
   // repaint if visible
   if ( NULL != m_hWnd )
      ::InvalidateRect(m_hWnd, NULL, FALSE);
}

// Sets the distance the mouse must move before the balloon closes when the unCLOSE_ON_MOUSE_MOVE option is set.
void CBalloonHelp::SetMouseMoveTolerance(int nTolerance)
{
   m_nMouseMoveTolerance = nTolerance;
}

//
// creates a new balloon window
// Parameters:
//    strTitle    |  Title of balloon
//    strContent  |  Content of balloon
//    ptAnchor    |  point tail of balloon will be "anchor"ed to
//    unOptions   |  One or more of:
//                :     unCLOSE_ON_LBUTTON_UP   |  closes window on WM_LBUTTON_UP
//                :     unCLOSE_ON_MBUTTON_UP   |  closes window on WM_MBUTTON_UP
//                :     unCLOSE_ON_RBUTTON_UP   |  closes window on WM_RBUTTON_UP
//                :     unCLOSE_ON_LBUTTON_DOWN |  closes window on WM_LBUTTON_DOWN
//                :     unCLOSE_ON_MBUTTON_DOWN |  closes window on WM_MBUTTON_DOWN
//                :     unCLOSE_ON_RBUTTON_DOWN |  closes window on WM_RBUTTON_DOWN
//                :     unCLOSE_ON_MOUSE_MOVE   |  closes window when user moves mouse past threshhold
//                :     unCLOSE_ON_KEYPRESS     |  closes window on the next keypress message sent to this thread.
//                :     unCLOSE_ON_ANYTHING     |  all of the above.
//                :     unDELAY_CLOSE           |  when a user action triggers the close, begins timer.  closes when timer expires.
//                :     unDELETE_THIS_ON_CLOSE  |  deletes object when window is closed.  Used by LaunchBalloon(), use with care
//                :     unSHOW_CLOSE_BUTTON     |  shows close button in upper right
//                :     unSHOW_INNER_SHADOW     |  draw inner shadow in balloon
//                :     unSHOW_TOPMOST          |  place balloon above all other windows
//                :     unDISABLE_XP_SHADOW     |  disable Windows XP's drop-shadow effect (overrides system and user settings)
//                :     unDISABLE_FADE          |  disable the fade-in/fade-out effects (overrides system and user settings)
//                :     unDISABLE_FADEIN        |  disable the fade-in effect
//                :     unDISABLE_FADEOUT       |  disable the fade-out effect
//    pParentWnd  |  Parent window.  If NULL will be set to AfxGetMainWnd() and anchor to screen
//    strURL      |  If not empty, when the balloon is clicked ShellExecute() will
//                |  be called, with strURL passed in.
//    unTimeout   |  If not 0, balloon will automatically close after unTimeout milliseconds.
//    hIcon       |  If not NULL, the icon indicated by hIcon will be displayed at top-left of the balloon.
//
// Returns:
//    TRUE if successful, else FALSE
//
BOOL CBalloonHelp::Create(const CStdString& strTitle, const CStdString& strContent,
               POINT& ptAnchor, unsigned int unOptions,
               HWND hParentWnd /*=NULL*/,
               const CStdString strURL /*= ""*/,
               unsigned int unTimeout /*= 0*/,
               HICON hIcon /*= NULL*/)
{
   m_strContent   = strContent;
   SetAnchorPoint(ptAnchor, hParentWnd);
   m_unOptions    = unOptions;
   m_strURL       = strURL;
   m_unTimeout    = unTimeout;

   if ( NULL != hIcon )
      SetIcon(hIcon);


   // if no fonts set, use defaults
   if ( NULL == m_hContentFont )
   {
      m_hContentFont = (HFONT)::GetStockObject(DEFAULT_GUI_FONT);
      if ( NULL == m_hContentFont )
         return FALSE;
   }

   // title font defaults to bold version of content font
   if ( NULL == m_hTitleFont )
   {
      LOGFONT LogFont;
      m_hTitleFont = (HFONT)::GetObject(m_hContentFont, sizeof(LOGFONT), &LogFont);
      LogFont.lfWeight = FW_BOLD;
		m_hTitleFont = ::CreateFontIndirect(&LogFont);
      if ( NULL == m_hTitleFont )
         return FALSE;
   }

   ATOM wndClass = GetClassAtom(!(m_unOptions&unDISABLE_XP_SHADOW));
   if ( 0 == wndClass )  // couldn't register class
      return FALSE;

   // check system settings: if fade effects are disabled or unavailable, disable here too
   BOOL bFade = FALSE;
   ::SystemParametersInfo(SPI_GETTOOLTIPANIMATION, 0, &bFade, 0);
   if (bFade)
      ::SystemParametersInfo(SPI_GETTOOLTIPFADE, 0, &bFade, 0);
   if (!bFade || NULL == m_fnAnimateWindow)
      m_unOptions |= unDISABLE_FADE;

   // create invisible at arbitrary position; then position, set region, and finally show

   // the idea with WS_EX_TOOLWINDOW is, you can't switch to this using alt+tab
   DWORD dwExStyle = WS_EX_TOOLWINDOW;
   if ( m_unOptions&unSHOW_TOPMOST )      // make topmost, if requested
      dwExStyle |= WS_EX_TOPMOST;
	RECT rc = {0,0,10,10};
   if ( !CreateEx(dwExStyle, (LPCTSTR)wndClass, strTitle, WS_POPUP, rc, hParentWnd, 0, NULL) )
      return FALSE;
   PositionWindow();

   if ( (m_unOptions&unCLOSE_ON_MOUSE_MOVE)
      ||(m_unOptions&unCLOSE_ON_LBUTTON_UP)
      ||(m_unOptions&unCLOSE_ON_LBUTTON_DOWN)
      ||(m_unOptions&unCLOSE_ON_MBUTTON_UP)
      ||(m_unOptions&unCLOSE_ON_MBUTTON_DOWN)
      ||(m_unOptions&unCLOSE_ON_RBUTTON_UP)
      ||(m_unOptions&unCLOSE_ON_RBUTTON_DOWN) )
   {
      ::GetCursorPos(&m_ptMouseOrig);
      SetMouseHook();
   }

   // these need to take effect even if the window receiving them
   // is not owned by this process.  So, if this process does not
   // already have the mouse captured, capture it!
   if ( (m_unOptions&unCLOSE_ON_LBUTTON_UP)
      ||(m_unOptions&unCLOSE_ON_MBUTTON_UP)
      ||(m_unOptions&unCLOSE_ON_RBUTTON_UP) )
   {
      // no, i don't particularly need or want to deal with a situation
      // where a balloon is being created and another program has captured
      // the mouse.  If you need it, it shouldn't be too hard, just do it here.
      if ( NULL == ::GetCapture() )
         ::SetCapture(m_hWnd);
   }

   if ( m_unOptions&unCLOSE_ON_KEYPRESS )
      SetKeyboardHook();

   ShowBalloon();
   return TRUE;
}

// calculate anchor position (adjust for client coordinates if used)
POINT CBalloonHelp::GetAnchorPoint()
{
   POINT ptAnchor = m_ptAnchor;
   // assume if window was given, point is in client coords
   if ( NULL != m_hwndAnchor )
      ::ClientToScreen(m_hwndAnchor, &ptAnchor);
   return ptAnchor;
}

// determine bounds of screen anchor is on (Multi-Monitor compatibility)
void CBalloonHelp::GetAnchorScreenBounds(RECT& rect)
{
   if ( ::IsRectEmpty(&rect) )
   {
      // get the nearest monitor to the anchor
      HMONITOR hMonitor = MonitorFromPoint(GetAnchorPoint(), MONITOR_DEFAULTTONEAREST);

      // get the monitor bounds
      MONITORINFO mi;
      mi.cbSize = sizeof(mi);
      GetMonitorInfo(hMonitor, &mi);

      // work area (area not obscured by task bar, etc.)
      m_screenRect = mi.rcWork;
   }
   rect = m_screenRect;
}

// calculates the area of the screen the balloon falls into
// this determins which direction the tail points
CBalloonHelp::BALLOON_QUADRANT CBalloonHelp::GetBalloonQuadrant()
{
   RECT rectDesktop;
   GetAnchorScreenBounds(rectDesktop);
   POINT ptAnchor = GetAnchorPoint();

   if ( ptAnchor.y < rectDesktop.top + (rectDesktop.bottom - rectDesktop.top)/2 )
   {
      if ( ptAnchor.x < rectDesktop.left + (rectDesktop.right - rectDesktop.left)/2 )
      {
         return BQ_TOPLEFT;
      }
      else
      {
         return BQ_TOPRIGHT;
      }
   }
   else
   {
      if ( ptAnchor.x < rectDesktop.left + (rectDesktop.right - rectDesktop.left)/2 )
      {
         return BQ_BOTTOMLEFT;
      }
      else
      {
         return BQ_BOTTOMRIGHT;
      }
   }

   // unreachable
}

// Draw the non-client area
void CBalloonHelp::DrawNonClientArea(HDC hDC)
{
   RECT rect;
   ::GetWindowRect(m_hWnd, &rect);
	POINT pt = {rect.left, rect.top};
   ::ScreenToClient(m_hWnd, &pt);
	rect.left = pt.x; rect.top = pt.y;
	pt.x = rect.right; pt.y=rect.bottom;
   ::ScreenToClient(m_hWnd, &pt);
	rect.right = pt.x; rect.bottom = pt.y;
   RECT rectClient;
   ::GetClientRect(m_hWnd, &rectClient);
   ::OffsetRect(&rectClient, -rect.left, -rect.top);
   ::OffsetRect(&rect, -rect.left, -rect.top);
   ::ExcludeClipRect(hDC, rectClient.left, rectClient.top, rectClient.right, rectClient.bottom);
	HBRUSH hBrush = ::CreateSolidBrush(m_crBackground);
   ::FillRect(hDC, &rect, hBrush);
	::DeleteObject(hBrush);
	::SelectClipRgn(hDC, NULL);

   ASSERT(NULL != m_hrgnComplete);
   HBRUSH  brushFg = ::CreateSolidBrush(m_crForeground);
   if ( m_unOptions & unSHOW_INNER_SHADOW )
   {
      HBRUSH    brushHL;
      // slightly lighter color
      int red = 170 + GetRValue(m_crBackground)/3;
      int green = 170 + GetGValue(m_crBackground)/3;
      int blue = 170 + GetBValue(m_crBackground)/3;
      brushHL = ::CreateSolidBrush(RGB(red,green,blue));
      ::OffsetRgn(m_hrgnComplete, 1,1);
      ::FrameRgn(hDC, m_hrgnComplete, brushHL, 2, 2);
      // slightly darker color
      red = GetRValue(m_crForeground)/3 + GetRValue(m_crBackground)/3*2;
      green = GetGValue(m_crForeground)/3 + GetGValue(m_crBackground)/3*2;
      blue = GetBValue(m_crForeground)/3 + GetBValue(m_crBackground)/3*2;
      ::DeleteObject(brushHL);
      ::OffsetRgn(m_hrgnComplete, -2,-2);
      brushHL = ::CreateSolidBrush(RGB(red,green,blue));
      ::FrameRgn(hDC, m_hrgnComplete, brushHL, 2, 2);
      ::OffsetRgn(m_hrgnComplete, 1,1);
		::DeleteObject(brushHL);
   }
   // outline
   FrameRgn(hDC, m_hrgnComplete, brushFg, 1, 1);
	::DeleteObject(brushFg);
}

// Draw the client area
void CBalloonHelp::DrawClientArea(HDC hDC)
{
   SIZE sizeHeader = DrawHeader(hDC);
   DrawContent(hDC, sizeHeader.cy+nTIP_MARGIN);
}

// Calculate the dimensions and draw the balloon header
SIZE CBalloonHelp::DrawHeader(HDC hDC, bool bDraw)
{
   SIZE sizeHdr = {0,0};
   RECT rectClient;
   ::GetClientRect(m_hWnd, &rectClient);   // use this for positioning when drawing
                                 // else if content is wider than title, centering wouldn't work

   // calc & draw icon
   if ( NULL != m_hilIcon)
   {
      int x = 0;
      int y = 0;
      ImageList_GetIconSize(m_hilIcon, &x, &y);
      sizeHdr.cx += x;
      sizeHdr.cy = max(sizeHdr.cy, y);
      ImageList_SetBkColor(m_hilIcon, m_crBackground);
      if (bDraw)
         ImageList_Draw(m_hilIcon, 0, hDC, 0, 0, ILD_NORMAL);//ILD_TRANSPARENT);
      rectClient.left += x;
   }

   // calc & draw close button
   if ( m_unOptions & unSHOW_CLOSE_BUTTON )
   {
      int nBtnWidth = ::GetSystemMetrics(SM_CXSIZE);
      // if something is already in the header (icon) leave space
      if ( sizeHdr.cx > 0 )
         sizeHdr.cx += nTIP_MARGIN;
      sizeHdr.cx += nBtnWidth;
      sizeHdr.cy = max(sizeHdr.cy, ::GetSystemMetrics(SM_CYSIZE));
      if (bDraw)
		{
			RECT rc = {rectClient.right-nBtnWidth,0,rectClient.right,::GetSystemMetrics(SM_CYSIZE)};
         ::DrawFrameControl(hDC, &rc, DFC_CAPTION, DFCS_CAPTIONCLOSE|DFCS_FLAT);
		}
      rectClient.right -= nBtnWidth;
   }

   // calc title size
	CStdString strTitle;
   ::GetWindowText(m_hWnd, strTitle.GetBuffer(MAX_PATH), MAX_PATH);
	strTitle.ReleaseBuffer();
   if ( !strTitle.IsEmpty() )
   {
      HFONT hOldFont = (HFONT) SelectObject(hDC, m_hTitleFont);

      // if something is already in the header (icon or close button) leave space
      if ( sizeHdr.cx > 0 )
         sizeHdr.cx += nTIP_MARGIN;
      RECT rectTitle = {0,0,0,0};
      ::DrawText(hDC, strTitle, strTitle.GetLength(), &rectTitle, DT_CALCRECT | DT_NOPREFIX | DT_EXPANDTABS | DT_SINGLELINE);
      sizeHdr.cx += rectTitle.right - rectTitle.left ;
      sizeHdr.cy = max(sizeHdr.cy, rectTitle.bottom - rectTitle.top);

      // draw title
      if ( bDraw )
      {
         ::SetBkMode(hDC, TRANSPARENT);
         ::SetTextColor(hDC, m_crForeground);
         ::DrawText(hDC, strTitle, strTitle.GetLength(), &rectClient, DT_CENTER | DT_NOPREFIX  | DT_EXPANDTABS | DT_SINGLELINE);
      }

      // cleanup
      SelectObject(hDC, hOldFont);
   }

   return sizeHdr;
}

// Calculate the dimensions and draw the balloon contents
SIZE CBalloonHelp::DrawContent(HDC hDC, int nTop, bool bDraw)
{
	RECT rectContent;
   GetAnchorScreenBounds(rectContent);
   ::OffsetRect(&rectContent, -rectContent.left, -rectContent.top);
   rectContent.top = nTop;

   // limit to half screen width
   rectContent.right -= (rectContent.right - rectContent.left)/2;

   // calc size
   HFONT hOldFont = (HFONT)SelectObject(hDC,m_hContentFont);
   if ( !m_strContent.IsEmpty() )
      ::DrawText(hDC, m_strContent, m_strContent.GetLength(), &rectContent, DT_CALCRECT | DT_LEFT | DT_NOPREFIX | DT_EXPANDTABS | DT_WORDBREAK);
   else
      ::SetRectEmpty(&rectContent);   // don't want to leave half the screen for empty strings ;)

   // draw
   if (bDraw)
   {
      ::SetBkMode(hDC, TRANSPARENT);
      ::SetTextColor(hDC, m_crForeground);
      ::DrawText(hDC, m_strContent, m_strContent.GetLength(), &rectContent, DT_LEFT | DT_NOPREFIX | DT_WORDBREAK | DT_EXPANDTABS);
   }

   // cleanup
   ::SelectObject(hDC, hOldFont);
	SIZE ret = {rectContent.right - rectContent.left, rectContent.bottom - rectContent.top};
   return ret;
}

// calculates the client size necessary based on title and content
SIZE CBalloonHelp::CalcClientSize()
{
   ASSERT(NULL != m_hWnd);
   HDC dc = ::GetWindowDC(m_hWnd);

   SIZE sizeHeader = CalcHeaderSize(dc);
   SIZE sizeContent = CalcContentSize(dc);
	::ReleaseDC(m_hWnd, dc);
	SIZE ret = {max(sizeHeader.cx,sizeContent.cx), sizeHeader.cy + nTIP_MARGIN + sizeContent.cy};
   return ret;
}

// calculates the size for the entire window based on content size
SIZE CBalloonHelp::CalcWindowSize()
{
   SIZE size = CalcClientSize();
   size.cx += nTIP_MARGIN*2;
   size.cy += nTIP_TAIL+nTIP_MARGIN*2;
   //size.cx = max(size.cx, nTIP_MARGIN*2+nTIP_TAIL*4);
   return size;
}


// this routine calculates the size and position of the window relative
// to it's anchor point, and moves the window accordingly.  The region is also
// created and set here.
void CBalloonHelp::PositionWindow()
{
   SIZE sizeWnd = CalcWindowSize();

   POINT ptTail[3];
   POINT ptTopLeft = {0,0};
   POINT ptBottomRight = {sizeWnd.cx, sizeWnd.cy};

   // force recalculation of desktop
   ::SetRectEmpty(&m_screenRect);

   switch (GetBalloonQuadrant())
   {
   case BQ_TOPLEFT:
      ptTopLeft.y = nTIP_TAIL;
      ptTail[0].x = (sizeWnd.cx-nTIP_TAIL)/4 + nTIP_TAIL;
      ptTail[0].y = nTIP_TAIL+1;
      ptTail[2].x = (sizeWnd.cx-nTIP_TAIL)/4;
      ptTail[2].y = ptTail[0].y;
      ptTail[1].x = ptTail[2].x;
      ptTail[1].y = 1;
      break;
   case BQ_TOPRIGHT:
      ptTopLeft.y = nTIP_TAIL;
      ptTail[0].x = (sizeWnd.cx-nTIP_TAIL)/4*3;
      ptTail[0].y = nTIP_TAIL+1;
      ptTail[2].x = (sizeWnd.cx-nTIP_TAIL)/4*3 + nTIP_TAIL;
      ptTail[2].y = ptTail[0].y;
      ptTail[1].x = ptTail[2].x;
      ptTail[1].y = 1;
      break;
   case BQ_BOTTOMLEFT:
      ptBottomRight.y = sizeWnd.cy-nTIP_TAIL;
      ptTail[0].x = (sizeWnd.cx-nTIP_TAIL)/4 + nTIP_TAIL;
      ptTail[0].y = sizeWnd.cy-nTIP_TAIL-2;
      ptTail[2].x = (sizeWnd.cx-nTIP_TAIL)/4;
      ptTail[2].y = ptTail[0].y;
      ptTail[1].x = ptTail[2].x;
      ptTail[1].y = sizeWnd.cy-2;
      break;
   case BQ_BOTTOMRIGHT:
      ptBottomRight.y = sizeWnd.cy-nTIP_TAIL;
      ptTail[0].x = (sizeWnd.cx-nTIP_TAIL)/4*3;
      ptTail[0].y = sizeWnd.cy-nTIP_TAIL-2;
      ptTail[2].x = (sizeWnd.cx-nTIP_TAIL)/4*3 + nTIP_TAIL;
      ptTail[2].y = ptTail[0].y;
      ptTail[1].x = ptTail[2].x;
      ptTail[1].y = sizeWnd.cy-2;
      break;
   }

   // adjust for very narrow balloons
   if ( ptTail[0].x < nTIP_MARGIN )
      ptTail[0].x = nTIP_MARGIN;
   if ( ptTail[0].x > sizeWnd.cx - nTIP_MARGIN )
      ptTail[0].x = sizeWnd.cx - nTIP_MARGIN;
   if ( ptTail[1].x < nTIP_MARGIN )
      ptTail[1].x = nTIP_MARGIN;
   if ( ptTail[1].x > sizeWnd.cx - nTIP_MARGIN )
      ptTail[1].x = sizeWnd.cx - nTIP_MARGIN;
   if ( ptTail[2].x < nTIP_MARGIN )
      ptTail[2].x = nTIP_MARGIN;
   if ( ptTail[2].x > sizeWnd.cx - nTIP_MARGIN )
      ptTail[2].x = sizeWnd.cx - nTIP_MARGIN;

   // get window position
   POINT ptAnchor = GetAnchorPoint();
   POINT ptOffs = {ptAnchor.x - ptTail[1].x, ptAnchor.y - ptTail[1].y};

   // adjust position so all is visible
   RECT rectScreen;
   GetAnchorScreenBounds(rectScreen);
   int nAdjustX = 0;
   int nAdjustY = 0;
   if ( ptOffs.x < rectScreen.left )
      nAdjustX = rectScreen.left-ptOffs.x;
   else if ( ptOffs.x + sizeWnd.cx >= rectScreen.right )
      nAdjustX = rectScreen.right - (ptOffs.x + sizeWnd.cx);
   if ( ptOffs.y + nTIP_TAIL < rectScreen.top )
      nAdjustY = rectScreen.top - (ptOffs.y + nTIP_TAIL);
   else if ( ptOffs.y + sizeWnd.cy - nTIP_TAIL >= rectScreen.bottom )
      nAdjustY = rectScreen.bottom - (ptOffs.y + sizeWnd.cy - nTIP_TAIL);

   // reposition tail
   // uncomment two commented lines below to move entire tail
   // instead of just anchor point

   //ptTail[0].x -= nAdjustX;
   ptTail[1].x -= nAdjustX;
   //ptTail[2].x -= nAdjustX;
   ptOffs.x    += nAdjustX;
   ptOffs.y    += nAdjustY;

   // place window
   ::MoveWindow(m_hWnd, ptOffs.x, ptOffs.y, sizeWnd.cx, sizeWnd.cy, TRUE);

   // apply region
   HRGN region = ::CreatePolygonRgn(&ptTail[0], 3, ALTERNATE);
   HRGN regionRound = ::CreateRoundRectRgn(ptTopLeft.x,ptTopLeft.y,ptBottomRight.x,ptBottomRight.y,nTIP_MARGIN*3,nTIP_MARGIN*3);
   HRGN regionComplete = ::CreateRectRgn(0,0,1,1);

   ::CombineRgn(regionComplete, region, regionRound, RGN_OR);

   if ( NULL == m_hrgnComplete)
      m_hrgnComplete = ::CreateRectRgn(0,0,1,1);

   if ( !::EqualRgn(m_hrgnComplete, regionComplete) )
   {
      ::CopyRgn(m_hrgnComplete, regionComplete);
      ::SetWindowRgn(m_hWnd, regionComplete, TRUE);

      // There is a bug with layered windows and NC changes in Win2k
      // As a workaround, redraw the entire window if the NC area changed.
      // Changing the anchor point is the ONLY thing that will change the
      // position of the client area relative to the window during normal
      // operation.
      ::RedrawWindow(m_hWnd, NULL, NULL, RDW_UPDATENOW| RDW_ERASE | RDW_INVALIDATE | RDW_FRAME | RDW_ALLCHILDREN);
   }
	else
		::DeleteObject(regionComplete);
	::DeleteObject(region);
	::DeleteObject(regionRound);
}



// Returns the class ATOM for a BalloonHelp control.  Registers the class first, if necessary.
ATOM CBalloonHelp::GetClassAtom(BOOL bShadowed)
{
   if ( 0 == s_ClassAtom )
   {
      WNDCLASSEX wcx;

      // Fill in the window class structure with parameters
      // that describe the main window.

      wcx.cbSize = sizeof(wcx);                 // size of structure
      wcx.style = CS_DBLCLKS|CS_SAVEBITS
         |CS_DROPSHADOW;                        // notify of double clicks, save screen under, show dropshadow
      wcx.lpfnWndProc = CWnd::stWinMsgHandler;             // points to window procedure
      wcx.cbClsExtra = 0;                       // no extra class memory
      wcx.cbWndExtra = 0;                       // no extra window memory
      wcx.hInstance = g_hInstance;   // handle to instance
      wcx.hIcon = NULL;                         // no app. icon
      wcx.hCursor = LoadCursor(NULL,IDC_ARROW); // predefined arrow
      wcx.hbrBackground = ::GetSysColorBrush(COLOR_WINDOW);                 // no background brush
      wcx.lpszMenuName =  NULL;                 // no menu resource
      wcx.lpszClassName = "BalloonHelpClassDS"; // name of window class
      wcx.hIconSm = NULL;                       // no small class icon

      // Register the window class (this may not work if dropshadows are not supported)
      s_ClassAtomShadowed = ::RegisterClassEx(&wcx);

      // Register shadow-less class
      wcx.style &= ~CS_DROPSHADOW;
      wcx.lpszClassName = "BalloonHelpClass";
      s_ClassAtom = ::RegisterClassEx(&wcx);
   }

   if ( bShadowed && 0 != s_ClassAtomShadowed )
      return s_ClassAtomShadowed;
   return s_ClassAtom;
}


// Displays the balloon on the screen, performing fade-in if enabled.
void CBalloonHelp::ShowBalloon(void)
{
   ::ShowWindow(m_hWnd, SW_SHOWNOACTIVATE);
   if ( !(m_unOptions&unDELAY_CLOSE) )
      SetTimeout(m_unTimeout);     // start close timer
}

// Removes the balloon from the screen, performing the fade-out if enabled
void CBalloonHelp::HideBalloon(void)
{
   if ( m_unOptions&unDELAY_CLOSE )
   {
      m_unOptions &= ~(unDELAY_CLOSE|unCLOSE_ON_ANYTHING);  // close only via timer or button
      SetTimeout(m_unTimeout);     // start close timer
      return;
   }
   ::ShowWindow(m_hWnd, SW_HIDE);
   if ( GetCapture() == m_hWnd )
      ReleaseCapture();
   ::DestroyWindow(m_hWnd);
}

//
// Keyboard hook
//

void CBalloonHelp::SetKeyboardHook()
{
   if ( NULL==m_hKeyboardHook )
   {
      m_hKeyboardHook = ::SetWindowsHookEx(WH_KEYBOARD,
         (HOOKPROC)BHKeybHookThunk<CBalloonHelp>::GetThunk(),
         NULL, ::GetCurrentThreadId());
   }
}

void CBalloonHelp::RemoveKeyboardHook()
{
   if ( NULL!=m_hKeyboardHook )
   {
      ::UnhookWindowsHookEx(m_hKeyboardHook);
      m_hKeyboardHook=NULL;
   }
}


//
// Mouse hook
//

void CBalloonHelp::SetMouseHook()
{
   if ( NULL==m_hMouseHook )
   {
      m_hMouseHook = ::SetWindowsHookEx(WH_MOUSE,
         (HOOKPROC)BHMouseHookThunk<CBalloonHelp>::GetThunk(),
         NULL, ::GetCurrentThreadId());
   }
}

void CBalloonHelp::RemoveMouseHook()
{
   if ( NULL!=m_hMouseHook )
   {
      ::UnhookWindowsHookEx(m_hMouseHook);
      m_hMouseHook=NULL;
   }
}

//
// Call Window Return hook
//

void CBalloonHelp::SetCallWndRetHook()
{
   if ( NULL==m_hCallWndRetHook )
   {
      m_hCallWndRetHook = ::SetWindowsHookEx(WH_CALLWNDPROCRET,
         (HOOKPROC)BHCallWndRetHookThunk<CBalloonHelp>::GetThunk(),
         NULL, ::GetCurrentThreadId());
   }
}

void CBalloonHelp::RemoveCallWndRetHook()
{
   if ( NULL!=m_hCallWndRetHook )
   {
      ::UnhookWindowsHookEx(m_hCallWndRetHook);
      m_hCallWndRetHook=NULL;
   }
}

LRESULT CALLBACK CBalloonHelp::WinMsgHandler(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
{
	switch(uMsg)
	{
		HANDLE_MSG (hwnd, WM_CLOSE, CBalloonHelp::OnClose);
		HANDLE_MSG (hwnd, WM_DESTROY, CBalloonHelp::OnDestroy);
		HANDLE_MSG (hwnd, WM_ERASEBKGND, CBalloonHelp::OnEraseBkgnd);
		HANDLE_MSG (hwnd, WM_LBUTTONDOWN, CBalloonHelp::OnLButtonDown);
		HANDLE_MSG (hwnd, WM_LBUTTONUP, CBalloonHelp::OnLButtonUp);
		HANDLE_MSG (hwnd, WM_MOUSEMOVE, CBalloonHelp::OnMouseMove);
		HANDLE_MSG (hwnd, WM_NCCALCSIZE, CBalloonHelp::OnNCCalcSize);
		HANDLE_MSG (hwnd, WM_NCDESTROY, CBalloonHelp::OnNCDestroy);
		HANDLE_MSG (hwnd, WM_NCHITTEST, CBalloonHelp::OnNCHitTest);
		HANDLE_MSG (hwnd, WM_NCPAINT, CBalloonHelp::OnNCPaint);
		HANDLE_MSG (hwnd, WM_PAINT, CBalloonHelp::OnPaint);
		HANDLE_MSG (hwnd, WM_SHOWWINDOW, CBalloonHelp::OnShowWindow);
		HANDLE_MSG (hwnd, WM_TIMER, CBalloonHelp::OnTimer);
	case WM_PRINT: return CBalloonHelp::OnPrint(hwnd, wParam, lParam);
	case WM_PRINTCLIENT: return CBalloonHelp::OnPrintClient(hwnd, wParam, lParam);
	default: return DefWindowProc (hwnd, uMsg, wParam, lParam);
	}
}

#define MSGHANDLER_PROLOG_BOOL\
	CBalloonHelp *thisPtr = (CBalloonHelp*)GetObjectFromWindow(hwnd);\
	if(!thisPtr) \
		return FALSE;

#define MSGHANDLER_PROLOG\
	CBalloonHelp *thisPtr = (CBalloonHelp*)GetObjectFromWindow(hwnd);\
	if(!thisPtr) \
		return; \


#define MSGHANDLER_EPILOG

void CBalloonHelp::OnShowWindow(HWND hwnd, BOOL fShow, UINT status)
{
	MSGHANDLER_PROLOG
   if ( NULL != thisPtr->m_fnAnimateWindow )
   {
      if ( fShow && !(thisPtr->m_unOptions&unDISABLE_FADEIN) )
         thisPtr->m_fnAnimateWindow(thisPtr->m_hWnd, 200, AW_BLEND);
      else if ( !fShow && !(thisPtr->m_unOptions&unDISABLE_FADEOUT) )
         thisPtr->m_fnAnimateWindow(thisPtr->m_hWnd, 200, AW_HIDE | AW_BLEND );
   }
	MSGHANDLER_EPILOG
}

// Erase client area of balloon
BOOL CBalloonHelp::OnEraseBkgnd(HWND hwnd, HDC hdc)
{
	MSGHANDLER_PROLOG_BOOL
   RECT rect;
   GetClientRect(hwnd, &rect);
	HBRUSH hBrush = ::CreateSolidBrush(thisPtr->m_crBackground);
   ::FillRect(hdc, &rect, hBrush);
	::DeleteObject(hBrush);
	MSGHANDLER_EPILOG
   return TRUE;
}

// draw balloon client area (title & contents)
void CBalloonHelp::OnPaint(HWND hwnd)
{
	MSGHANDLER_PROLOG
	PAINTSTRUCT ps;
	HDC dc = ::BeginPaint(hwnd, &ps);
   thisPtr->DrawClientArea(dc);
	::EndPaint(hwnd, &ps);
	MSGHANDLER_EPILOG
}

// draw balloon shape & border
void CBalloonHelp::OnNCPaint(HWND hwnd, HRGN hrgn)
{
	MSGHANDLER_PROLOG
	HDC dc = ::GetWindowDC(hwnd);
   thisPtr->DrawNonClientArea(dc);
	::ReleaseDC(hwnd, dc);
	MSGHANDLER_EPILOG
}

// draw the window into the specified device context
LRESULT CBalloonHelp::OnPrint(HWND hwnd, WPARAM wParam, LPARAM lParam)
{
	MSGHANDLER_PROLOG_BOOL
   if ( lParam & PRF_NONCLIENT  )
      thisPtr->DrawNonClientArea((HDC)wParam);
	MSGHANDLER_EPILOG
	return ::DefWindowProc(hwnd, WM_PRINT, wParam, lParam);
}

// draw the client area into the specified device context
LRESULT CBalloonHelp::OnPrintClient(HWND hwnd, WPARAM wParam, LPARAM lParam)
{
	MSGHANDLER_PROLOG_BOOL
   if ( lParam & PRF_ERASEBKGND )
      ::SendMessage(hwnd, WM_ERASEBKGND, wParam, lParam );
   if ( lParam & PRF_CLIENT )
      thisPtr->DrawClientArea((HDC)wParam);
	MSGHANDLER_EPILOG
   return 0;
}


// Close button handler
void CBalloonHelp::OnLButtonDown(HWND hwnd, BOOL fDoubleClick, int x, int y, UINT keyFlags)
{
	MSGHANDLER_PROLOG
   if (thisPtr->m_unOptions & unSHOW_CLOSE_BUTTON)
   {
      RECT rect;
      ::GetClientRect(hwnd, &rect);
      rect.left = rect.right-::GetSystemMetrics(SM_CXSIZE);
      rect.bottom = rect.top+::GetSystemMetrics(SM_CYSIZE);
		POINT point = {x, y};
      if ( ::PtInRect(&rect, point) )
      {
         thisPtr->m_uCloseState |= DFCS_PUSHED;
         ::SetCapture(hwnd);
         CBalloonHelp::OnMouseMove(hwnd, x, y, keyFlags);
      }
   }
	MSGHANDLER_EPILOG
}

// Close button handler,
// URL handler
void CBalloonHelp::OnLButtonUp(HWND hwnd, int x, int y, UINT keyFlags)
{
	MSGHANDLER_PROLOG
   if ( (thisPtr->m_unOptions & unSHOW_CLOSE_BUTTON) && (thisPtr->m_uCloseState & DFCS_PUSHED))
   {
      ReleaseCapture();
      thisPtr->m_uCloseState &= ~DFCS_PUSHED;
      RECT rect;
      ::GetClientRect(hwnd, &rect);
      rect.left = rect.right-::GetSystemMetrics(SM_CXSIZE);
      rect.bottom = rect.top+::GetSystemMetrics(SM_CYSIZE);
		POINT point = {x, y};
      if ( ::PtInRect(&rect, point) )
         thisPtr->HideBalloon();
   }
   else if ( !thisPtr->m_strURL.IsEmpty() )
   {
      RECT rect;
      ::GetClientRect(hwnd, &rect);
		POINT point = {x, y};
      if ( ::PtInRect(&rect, point) )
      {
         ::ShellExecute(NULL, NULL, thisPtr->m_strURL, NULL, NULL, SW_SHOWNORMAL);
         thisPtr->HideBalloon();
      }
   }
	MSGHANDLER_EPILOG
}

//
// Ensure WM_MOUSEMOVE messages are sent for the entire window
//
UINT CBalloonHelp::OnNCHitTest(HWND hwnd, int x, int y)
{
   return HTCLIENT;
}

//
// do mouse tracking:
//   Tracking for close button;
//
void CBalloonHelp::OnMouseMove(HWND hwnd, int x, int y, UINT keyFlags)
{
	MSGHANDLER_PROLOG
   if (thisPtr->m_unOptions & unSHOW_CLOSE_BUTTON)
   {
      RECT rect;
      GetClientRect(hwnd, &rect);
      rect.left = rect.right-::GetSystemMetrics(SM_CXSIZE);
      rect.bottom = rect.top+::GetSystemMetrics(SM_CYSIZE);
      HDC dc = ::GetDC(hwnd);
      UINT uState = DFCS_CAPTIONCLOSE;
      BOOL bPushed = thisPtr->m_uCloseState&DFCS_PUSHED;
      thisPtr->m_uCloseState &= ~DFCS_PUSHED;
		POINT point = {x, y};
      if ( ::PtInRect(&rect, point) )
      {
         uState |= DFCS_HOT;
         if ( bPushed )
            uState |= DFCS_PUSHED;
      }
      else
      {
         uState |= DFCS_FLAT;
      }
      if ( uState != thisPtr->m_uCloseState )
      {
         ::DrawFrameControl(dc, &rect, DFC_CAPTION, uState);
         thisPtr->m_uCloseState = uState;
      }
      if ( bPushed )
         thisPtr->m_uCloseState |= DFCS_PUSHED;
		::ReleaseDC(hwnd, dc);
   }
	MSGHANDLER_EPILOG
}

// Ensures client area is the correct size relative to window size,
// presearves client contents if possible when moving.
UINT CBalloonHelp::OnNCCalcSize(HWND hwnd, BOOL fCalcValidRects, NCCALCSIZE_PARAMS * lpcsp)
{
	MSGHANDLER_PROLOG_BOOL
   // nTIP_MARGIN pixel margin on all sides
   ::InflateRect(&lpcsp->rgrc[0], -nTIP_MARGIN,-nTIP_MARGIN);

   // nTIP_TAIL pixel "tail" on side closest to anchor
   switch ( thisPtr->GetBalloonQuadrant() )
   {
   case BQ_TOPRIGHT:
   case BQ_TOPLEFT:
      lpcsp->rgrc[0].top += nTIP_TAIL;
      break;
   case BQ_BOTTOMRIGHT:
   case BQ_BOTTOMLEFT:
      lpcsp->rgrc[0].bottom -= nTIP_TAIL;
      break;
   }

   // sanity: ensure rect does not have negative size
   if ( lpcsp->rgrc[0].right < lpcsp->rgrc[0].left )
      lpcsp->rgrc[0].right = lpcsp->rgrc[0].left;
   if ( lpcsp->rgrc[0].bottom < lpcsp->rgrc[0].top )
      lpcsp->rgrc[0].bottom = lpcsp->rgrc[0].top;

   if ( fCalcValidRects )
   {
      // determine if client position has changed relative to the window position
      // if so, don't bother presearving anything.
      if ( !::EqualRect(&lpcsp->rgrc[0], &lpcsp->rgrc[2]) )
      {
         ::SetRectEmpty(&lpcsp->rgrc[2]);
      }
   }
	MSGHANDLER_EPILOG
	return 0;
}

// handle kill timer
void CBalloonHelp::OnTimer(HWND hwnd, UINT id)
{
	MSGHANDLER_PROLOG
   // really shouldn't be any other timers firing, but might as well make sure
   if ( id == ID_TIMER_CLOSE )
   {
      ::KillTimer(hwnd, thisPtr->m_unTimerClose);
      thisPtr->HideBalloon();
   }
	MSGHANDLER_EPILOG
}

// Called as the window is being destroyed.  Completes destruction after removing keyboard hook.
void CBalloonHelp::OnDestroy(HWND hwnd)
{
	MSGHANDLER_PROLOG
   // remove hooks
   thisPtr->RemoveMouseHook();
   thisPtr->RemoveKeyboardHook();
   thisPtr->RemoveCallWndRetHook();
	MSGHANDLER_EPILOG
}

// close the balloon, performing any set transition effect.
void CBalloonHelp::OnClose(HWND hwnd)
{
	MSGHANDLER_PROLOG
   thisPtr->HideBalloon();
	MSGHANDLER_EPILOG
}

// Called after window has been destroyed.  Destroys the object if option is set.
void CBalloonHelp::OnNCDestroy(HWND hwnd)
{
	MSGHANDLER_PROLOG
   // free object if requested
   // be careful with this one :D
   if ( thisPtr->m_unOptions & unDELETE_THIS_ON_CLOSE )
      delete thisPtr;
	MSGHANDLER_EPILOG
}

// Keyboard hook: used to implement the unCLOSE_ON_KEYPRESS option
LRESULT CBalloonHelp::KeyboardHookProc( int code, WPARAM wParam, LPARAM lParam)
{
   // Skip if the key was released or if it's a repeat
   // Bit 31:  Specifies the transition state. The value is 0 if the key
   //       is being pressed and 1 if it is being released (see MSDN).
   if ( code>=0 && !(lParam&0x80000000) && NULL != m_hWnd )
   {
      ::PostMessage(m_hWnd, WM_CLOSE, 0, 0);
   }
   return ::CallNextHookEx(m_hKeyboardHook, code, wParam, lParam);
}

// Mouse hook: used to implement un-obtrusive mouse tracking
LRESULT CBalloonHelp::MouseHookProc(int code, WPARAM wParam, LPARAM lParam)
{
   if (code>=0 && NULL != m_hWnd )
   {
      switch ( (UINT)wParam )
      {
      case WM_NCMOUSEMOVE:
      case WM_MOUSEMOVE:
         if ((m_unOptions & unCLOSE_ON_MOUSE_MOVE))
         {
            POINT pt;
            ::GetCursorPos(&pt);
            if ((abs(pt.x-m_ptMouseOrig.x) > m_nMouseMoveTolerance || abs(pt.y-m_ptMouseOrig.y) > m_nMouseMoveTolerance) )
               ::PostMessage(m_hWnd, WM_CLOSE, 0, 0);
         }
         break;
      case WM_NCLBUTTONDOWN:
      case WM_LBUTTONDOWN:
         if ((m_unOptions & unCLOSE_ON_LBUTTON_DOWN))
            ::PostMessage(m_hWnd, WM_CLOSE, 0, 0);
         break;
      case WM_NCMBUTTONDOWN:
      case WM_MBUTTONDOWN:
         if ((m_unOptions & unCLOSE_ON_MBUTTON_DOWN))
            ::PostMessage(m_hWnd, WM_CLOSE, 0, 0);
         break;
      case WM_NCRBUTTONDOWN:
      case WM_RBUTTONDOWN:
         if ((m_unOptions& unCLOSE_ON_RBUTTON_DOWN))
            ::PostMessage(m_hWnd, WM_CLOSE, 0, 0);
         break;
      case WM_NCLBUTTONUP:
      case WM_LBUTTONUP:
         if ((m_unOptions & unCLOSE_ON_LBUTTON_UP))
            ::PostMessage(m_hWnd, WM_CLOSE, 0, 0);
         break;
      case WM_NCMBUTTONUP:
      case WM_MBUTTONUP:
         if ((m_unOptions & unCLOSE_ON_MBUTTON_UP))
            ::PostMessage(m_hWnd, WM_CLOSE, 0, 0);
         break;
      case WM_NCRBUTTONUP:
      case WM_RBUTTONUP:
         if ((m_unOptions & unCLOSE_ON_RBUTTON_UP))
            ::PostMessage(m_hWnd, WM_CLOSE, 0, 0);
         break;
      }
   }
   return ::CallNextHookEx(m_hMouseHook, code, wParam, lParam);
}

// Window Return hook: used to implement window following
LRESULT CBalloonHelp::CallWndRetProc(int code, WPARAM wParam, LPARAM lParam)
{
   if (code>=0 && NULL != m_hWnd )
   {
      CWPRETSTRUCT* pcwpr = (CWPRETSTRUCT*)lParam;
      if ( WM_MOVE == pcwpr->message && pcwpr->hwnd == m_hwndAnchor )
         PositionWindow();
   }

   return ::CallNextHookEx(m_hCallWndRetHook, code, wParam, lParam);
}
