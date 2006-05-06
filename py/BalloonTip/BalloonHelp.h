/*-----------------------------------------------------------------------------
# Name:        BalloonHelp.h
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
// BalloonHelp.cpp : header file
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
// ?/??/02 - Release #3: incomplete
//
//    Minor changes, bug fixes.
// I fixed an ugly bug where deallocated memory was accessed when using the
// strURL parameter to open a file or location when the balloon was clicked.
// I also fixed a minor but very visible bug in the demo.
// Added a couple of new options: 
//    unDELAY_CLOSE works in tandem with a timeout value to delay the action
// caused by the other unCLOSE_* options.  This allows you to keep a balloon
// active indefinately, until the user gets back from coffee break, etc., and
// has time to take a look at it.  For long timeout values, i'd advise also
// using unSHOW_CLOSE_BUTTON so the user can get rid of it quickly if need be.
//    unDISABLE_XP_SHADOW is exactly what it sounds like: if set, that cool
// dropshadow XP uses for tooltips and menus isn't shown.  Note that the user
// can also disable dropshadows globally, in which case this option has no effect.
// ---
// 5/30/02 - Release #2: i begin versioning
//
//    I suppose i should have kept a progress log for this.
// But i didn't, so you'll just have to assume it was mostly right to begin with.
// And i'll further confuse this by versioning it R2, even though it's the 
// fourth release (?) (i haven't been keeping track, heheh).
// I will, however, thank several people who have shown me better ways to do
// things, and thus improved the class greatly.
//
// Thanks to:
// Jan van den Baard for showing me the right way to use AnimateWindow(),
//    and for demonstrating how WM_NCHITTEST can be used to provide hot tracking.
//    Check out his ClassLib library on CP!
// Maximilian Hänel for his WTL port, and for demonstrating therein a
//    nicer way to handle message hooks.
// Mustafa Demirhan for the original idea and code for using keyboard hooks.
// All the other people who have provided suggestions, feeback, and code on the
// CP forums.  This class would not be half as useful as it is without you all.
//
// Ported from MFC to native win32 by Alch <alch at users dot sourceforge dot net
// ******************************************************************************

#ifndef _BALLOON_HELP_H_INCLUDED_
#define _BALLOON_HELP_H_INCLUDED_

// This was introduced to me by Maximilian Hänel in his WTL port.  Cool, eh?
////////////////////////////////////////////////////////////////////////////////
// The class _ThunkImpl is a renamed version of Andrew Nosenko CAuxThunk implementation.
// Thanks Andrew, it's a fantastic class!
//
// Copyright (c) 1997-2001 by Andrew Nosenko <andien@nozillium.com>,
// (c) 1997-1998 by Computer Multimedia System, Inc.,
// (c) 1998-2001 by Mead & Co Limited
//
// http://www.nozillium.com/atlaux/
// Version: 1.10.0021
//
#ifndef _M_IX86
	#pragma message("_ThunkImpl/ is implemented for X86 only!")
#endif

#pragma pack(push, 1)

template <class T>
class _ThunkImpl
{
private:

	BYTE	m_mov;			// mov ecx, %pThis
	DWORD	m_this; 		//
	BYTE	m_jmp;			// jmp func
	DWORD	m_relproc;		// relative jmp

protected:
	
	typedef LRESULT (T::*TMFP)(int, unsigned int, long int);
	void InitThunk(TMFP method, const T* pThis)
	{
		union { DWORD func; TMFP method; } addr;
		addr.method = (TMFP)method;
		m_mov  = 0xB9;
		m_this = (DWORD)pThis;
		m_jmp  = 0xE9;
		m_relproc = addr.func - (DWORD)(this+1);

		::FlushInstructionCache(GetCurrentProcess(), this, sizeof(*this));
	}
	FARPROC GetThunk() const 
   {
#ifdef _MSC_VER
		_ASSERTE(m_mov == 0xB9);
#endif
		return (FARPROC)this; 
   }
};
#pragma pack(pop) // _ThunkImpl


// we need these three dummy classes so we can 
// derive more than once from _ThunkImpl
template <class T>
class BHMouseHookThunk: public _ThunkImpl<T> {};

template <class T>
class BHKeybHookThunk: public _ThunkImpl<T> {};

template <class T>
class BHCallWndRetHookThunk: public _ThunkImpl<T> {};

class CBalloonHelp : public CWnd,
                     public BHKeybHookThunk<CBalloonHelp>,
                     public BHMouseHookThunk<CBalloonHelp>,
                     public BHCallWndRetHookThunk<CBalloonHelp>
{
public:
	CBalloonHelp();
	virtual ~CBalloonHelp();

   // options
   static const unsigned int unCLOSE_ON_LBUTTON_UP;   // closes window on WM_LBUTTON_UP
   static const unsigned int unCLOSE_ON_MBUTTON_UP;   // closes window on WM_MBUTTON_UP
   static const unsigned int unCLOSE_ON_RBUTTON_UP;   // closes window on WM_RBUTTON_UP
   static const unsigned int unCLOSE_ON_LBUTTON_DOWN; // closes window on WM_LBUTTON_DOWN
   static const unsigned int unCLOSE_ON_MBUTTON_DOWN; // closes window on WM_MBUTTON_DOWN
   static const unsigned int unCLOSE_ON_RBUTTON_DOWN; // closes window on WM_RBUTTON_DOWN
   static const unsigned int unCLOSE_ON_MOUSE_MOVE;   // closes window when user moves mouse past threshhold
   static const unsigned int unCLOSE_ON_KEYPRESS;     // closes window on the next keypress message sent to this thread.
   static const unsigned int unCLOSE_ON_ANYTHING;     // all of the above
   static const unsigned int unDELAY_CLOSE;           // when a user action triggers the close, begins timer.  closes when timer expires.
   static const unsigned int unDELETE_THIS_ON_CLOSE;  // deletes object when window is closed.  Used by LaunchBalloon(), use with care
   static const unsigned int unSHOW_CLOSE_BUTTON;     // shows close button in upper right
   static const unsigned int unSHOW_INNER_SHADOW;     // draw inner shadow in balloon
   static const unsigned int unSHOW_TOPMOST;          // place balloon above all other windows
   static const unsigned int unDISABLE_XP_SHADOW;     // disable Windows XP's drop-shadow effect (overrides system and user settings)
   static const unsigned int unDISABLE_FADEIN;        // disable the fade-in effect (overrides system and user settings)
   static const unsigned int unDISABLE_FADEOUT;       // disable the fade-out effect (overrides system and user settings)
   static const unsigned int unDISABLE_FADE;          // disable the fade-in/fade-out effects (overrides system and user settings)

   BOOL Create(const CStdString& strTitle,         // title of balloon
               const CStdString& strContent,       // content of balloon
               POINT& ptAnchor,          // anchor (tail position) of balloon
               unsigned int unOptions,          // options (see above)
               HWND hParentWnd = NULL,         // parent window (NULL == MFC main window)
               const CStdString strURL = "",       // URL to open (ShellExecute()) when clicked
               unsigned int unTimeout = 0,      // delay before closing automatically (milliseconds)
               HICON hIcon = NULL);             // icon to display

   // Show a help balloon on screen.
   static void LaunchBalloon(const CStdString& strTitle, const CStdString& strContent, 
               POINT& ptAnchor, 
               LPCTSTR szIcon = IDI_EXCLAMATION,
               unsigned int unOptions = unSHOW_CLOSE_BUTTON|CBalloonHelp::unSHOW_INNER_SHADOW|CBalloonHelp::unSHOW_TOPMOST,
               HWND hParentWnd = NULL, 
               const CStdString strURL = "",
               unsigned int unTimeout = 10000);

   // Sets the font used for drawing the balloon title.  Deleted by balloon, do not use CFont* after passing to this function.
   void SetTitleFont(HFONT hFont);
   // Sets the font used for drawing the balloon content.  Deleted by balloon, do not use CFont* after passing to this function.
   void SetContentFont(HFONT hFont);
   // Sets the icon displayed in the top left of the balloon (pass NULL to hide icon)
   void SetIcon(HICON hIcon);
   // Sets the icon displayed in the top left of the balloon (pass NULL to hide icon)
   void SetIconScaled(HICON hIcon, int cx, int cy);
   // Sets the icon displayed in the top left of the balloon (pass NULL hBitmap to hide icon)
   void SetIcon(HBITMAP hBitmap, COLORREF crMask);
   // Sets the icon displayed in the top left of the balloon
   void SetIcon(HBITMAP hBitmap, HBITMAP hMask);
   // Set icon displayed in the top left of the balloon to image # nIconIndex from pImageList
   void SetIcon(HIMAGELIST hImageList, int nIconIndex);
   // Sets the URL to be opened when balloon is clicked.  Pass "" to disable.
   void SetURL(const CStdString& strURL);
   // Sets the number of milliseconds the balloon can remain open.  Set to 0 to disable timeout.
   void SetTimeout(unsigned int unTimeout);
   // Sets the distance the mouse must move before the balloon closes when the unCLOSE_ON_MOUSE_MOVE option is set.
   void SetMouseMoveTolerance(int nTolerance);
   // Sets the point to which the balloon is "anchored"
   void SetAnchorPoint(POINT& ptAnchor, HWND hWndAnchor = NULL);
   // Sets the title of the balloon
   void SetTitle(const CStdString& strTitle);
   // Sets the content of the balloon (plain text only)
   void SetContent(const CStdString& strContent);
   // Sets the forground (text and border) color of the balloon
   void SetForegroundColor(COLORREF crForeground);
   // Sets the background color of the balloon
   void SetBackgroundColor(COLORREF crBackground);   
protected:
	// message handler
	LRESULT CALLBACK WinMsgHandler(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);

   // layout constants
   static const int nTIP_TAIL;
   static const int nTIP_MARGIN;

   // calculate anchor position (adjust for client coordinates if used)
   POINT GetAnchorPoint();

   // determine bounds of screen anchor is on (Multi-Monitor compatibility)
   void GetAnchorScreenBounds(RECT& rect);

   // determine section of the screen balloon is on
   enum BALLOON_QUADRANT { BQ_TOPRIGHT, BQ_TOPLEFT, BQ_BOTTOMRIGHT, BQ_BOTTOMLEFT };
   BALLOON_QUADRANT GetBalloonQuadrant();

   // Draw the non-client area
   virtual void DrawNonClientArea(HDC hDC);
   // Draw the client area
   virtual void DrawClientArea(HDC hDC);
   // Calculate the dimensions and draw the balloon header
   virtual SIZE DrawHeader(HDC hDC, bool bDraw = TRUE);
   // Calculate the dimensions and draw the balloon contents
   virtual SIZE DrawContent(HDC hDC, int nTop, bool bDraw = TRUE);
   // Calculate the dimensions required to draw the balloon header
   SIZE CalcHeaderSize(HDC hDC) { return DrawHeader(hDC, FALSE); }
   // Calculate the dimensions required to draw the balloon content
   SIZE CalcContentSize(HDC hDC) { return DrawContent(hDC, 0, FALSE); }
   // Calculate the total size needed by the balloon window
	SIZE CalcWindowSize();
   // Calculate the total size needed by the client area of the balloon window
	SIZE CalcClientSize();
   // Size and position the balloon window on the screen.
	void PositionWindow();

   // Displays the balloon on the screen, performing fade-in if enabled.
   void ShowBalloon(void);
   // Removes the balloon from the screen, performing the fade-out if enabled
   void HideBalloon(void);

   // Returns the class ATOM for a BalloonHelp control.  Registers the class first, if necessary.
   static ATOM GetClassAtom(BOOL bShadowed);

	// message handlers
   
   LRESULT OnPrint(HWND hwnd, WPARAM wParam, LPARAM lParam);
   LRESULT OnPrintClient(HWND hwnd, WPARAM wParam, LPARAM lParam);
	static void OnClose(HWND hwnd);
	static void OnDestroy(HWND hwnd);
	static BOOL OnEraseBkgnd(HWND hwnd, HDC hdc);
	static void OnLButtonDown(HWND hwnd, BOOL fDoubleClick, int x, int y, UINT keyFlags);
	static void OnLButtonUp(HWND hwnd, int x, int y, UINT keyFlags);
	static void OnMouseMove(HWND hwnd, int x, int y, UINT keyFlags);
	static UINT OnNCCalcSize(HWND hwnd, BOOL fCalcValidRects, NCCALCSIZE_PARAMS * lpcsp);
	static void OnNCDestroy(HWND hwnd);
	static UINT OnNCHitTest(HWND hwnd, int x, int y);
	static void OnNCPaint(HWND hwnd, HRGN hrgn);
	static void OnPaint(HWND hwnd);
	static void OnShowWindow(HWND hwnd, BOOL fShow, UINT status);
	static void OnTimer(HWND hwnd, UINT id);

	
private:
   // Keyboard hook
   void SetKeyboardHook();
   void RemoveKeyboardHook();
   // Mouse hook
   void SetMouseHook();
   void RemoveMouseHook();
   // Call Window Return hook
   void SetCallWndRetHook();
   void RemoveCallWndRetHook();

   // Keyboard hook callback
   LRESULT KeyboardHookProc( int code, WPARAM wParam, LPARAM lParam);
   // Mouse hook callback
	LRESULT MouseHookProc(int code, WPARAM wParam, LPARAM lParam);
   // Call Window Return hook callback (automatic following)
	LRESULT CallWndRetProc(int code, WPARAM wParam, LPARAM lParam);

   // animate window API, if available
   typedef BOOL (WINAPI* FN_ANIMATE_WINDOW)(HWND,DWORD,DWORD);
   FN_ANIMATE_WINDOW m_fnAnimateWindow;

   // hook handles, if set
   HHOOK          m_hKeyboardHook;
   HHOOK          m_hMouseHook;
   HHOOK          m_hCallWndRetHook;

   unsigned int   m_unOptions;
   unsigned int   m_unTimeout;      // max time to show, in milliseconds
   unsigned int   m_unTimerClose;   // ID of kill timer
   CStdString     m_strContent;     // text to show in content area
   CStdString     m_strURL;         // url to open, if clicked.
   HWND           m_hwndAnchor;     // window to anchor to (can be NULL for desktop anchor)
   POINT          m_ptAnchor;       // "anchor" (point of tail)
	HIMAGELIST     m_hilIcon;         // icon

   HFONT          m_hTitleFont;     // font to use for title
   HFONT          m_hContentFont;   // font to use for content
   
   COLORREF       m_crBackground;   // Background color for balloon   
   COLORREF       m_crForeground;   // Foreground color for balloon
   
   RECT           m_screenRect;     // bounds of screen anchor is on
   HRGN           m_hrgnComplete;    // Clipping / Drawing region
   POINT          m_ptMouseOrig;    // original mouse position; for hiding on mouse move
   UINT           m_uCloseState;    // current state of the close button
   int            m_nMouseMoveTolerance;  // distance mouse has to move before balloon will close.

   // class atoms (shadowed/not shadowed)
   static ATOM    s_ClassAtom;
   static ATOM    s_ClassAtomShadowed;
};

#endif // _BALLOON_HELP_H_INCLUDED_

