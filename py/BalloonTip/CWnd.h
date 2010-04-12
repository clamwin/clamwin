/*-----------------------------------------------------------------------------
# Name:        CWnd.h
# Product:     ClamWin Antivirus
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
this code is based on the following article by Jason Henderson:
http://www.codeproject.com/win32/win32windowwrapperclass.asp

*/

#ifndef _CWND_H_
#define _CWND_H_
#include "StdString.h"
class CWnd
{
public:
	// many different ways to register
	virtual BOOL RegisterWindow();
	virtual BOOL RegisterWindow(UINT style, HICON hIcon, HCURSOR hCursor, HBRUSH hbrBackground,
		LPCTSTR lpszMenuName, LPCTSTR lpszClassName, HICON hIconSm);
	virtual BOOL RegisterWindow(CONST WNDCLASSEX* wcx);

	// static message handler to put in WNDCLASSEX structure
	static LRESULT CALLBACK stWinMsgHandler(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);

	// just so you can change the window caption...
	void SetWindowTitle(LPCTSTR lpszTitle)
	{
		m_sWindowTitle = lpszTitle;
	};

	// 3 ways to create
	virtual BOOL Create();
	virtual BOOL Create(DWORD dwStyles, RECT* rect);
	virtual BOOL CreateEx(DWORD dwExStyle, LPCTSTR lpszClassName,
								LPCTSTR lpszWindowName, DWORD dwStyle,
								RECT& rect, HWND hwndParent,
								HMENU nIDorHMenu, LPVOID lpParam = NULL );

	void SetIcon(HICON hIcon) { m_hIcon = hIcon; };

	//void MsgLoop();
	BOOL IsWindowClosed() { return m_bWindowClosed; };

protected:
	HINSTANCE m_hInstance;
	HWND m_hWnd;
	BOOL m_bWindowClosed;
	CStdString m_sClassName;
	CStdString m_sWindowTitle;
	HICON m_hIcon;

	//contructor
	CWnd(HINSTANCE hInst, CONST WNDCLASSEX* wcx = NULL)
		:m_hWnd(NULL),
		m_hInstance(NULL),
		m_hIcon(NULL),
		m_bWindowClosed(FALSE)
	{
		m_hInstance = hInst;
		if (wcx != NULL) RegisterWindow(wcx);
	};

	~CWnd()
	{
		if(m_hIcon != NULL)
			CloseHandle(m_hIcon);
		m_hIcon = NULL;
	}
	// the real message handler
	virtual LRESULT CALLBACK WinMsgHandler(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) = 0;

	// returns a pointer the window (stored as the WindowLong)
	inline static CWnd *GetObjectFromWindow(HWND hWnd)
	{
		return (CWnd *)GetWindowLong(hWnd, GWL_USERDATA);
	}
};

inline BOOL CWnd::RegisterWindow()
{
    WNDCLASSEX wcx;

    // Fill in the window class structure with default parameters

    wcx.cbSize = sizeof(WNDCLASSEX);							// size of structure
    wcx.style = CS_HREDRAW | CS_VREDRAW;						// redraw if size changes
    wcx.lpfnWndProc = CWnd::stWinMsgHandler;				// points to window procedure
    wcx.cbClsExtra = 0;											// no extra class memory
    wcx.cbWndExtra = 0;											// no extra window memory
    wcx.hInstance = m_hInstance;									// handle to instance
    wcx.hIcon = m_hIcon;				// predefined app. icon
    wcx.hCursor = LoadCursor(NULL, IDC_ARROW);					// predefined arrow
    wcx.hbrBackground = (HBRUSH)GetStockObject(WHITE_BRUSH);	// white background brush
    wcx.lpszMenuName = NULL;									// name of menu resource
    wcx.lpszClassName = "BaseWindow";							// name of window class
    wcx.hIconSm = LoadIcon(NULL, IDI_APPLICATION);				// small class icon

    // Register the window class.
    return RegisterWindow(&wcx);

}

inline BOOL CWnd::RegisterWindow(UINT style, HICON hIcon, HCURSOR hCursor, HBRUSH hbrBackground,
									LPCTSTR lpszMenuName, LPCTSTR lpszClassName, HICON hIconSm)
{
    WNDCLASSEX wcx;

    // Fill in the window class structure with default parameters

    wcx.cbSize = sizeof(WNDCLASSEX);				// size of structure
    wcx.style = style;								// redraw if size changes
    wcx.lpfnWndProc = CWnd::stWinMsgHandler;	// points to window procedure
    wcx.cbClsExtra = 0;								// no extra class memory
    wcx.cbWndExtra = 0;								// no extra window memory
    wcx.hInstance = m_hInstance;						// handle to instance
    wcx.hIcon = hIcon;								// predefined app. icon
    wcx.hCursor = hCursor;							// predefined arrow
    wcx.hbrBackground = hbrBackground;				// white background brush
    wcx.lpszMenuName = lpszMenuName;				// name of menu resource
    wcx.lpszClassName = lpszClassName;				// name of window class
    wcx.hIconSm = hIconSm;							// small class icon

    // Register the window class.
    return RegisterWindow(&wcx);
}

inline BOOL CWnd::RegisterWindow(CONST WNDCLASSEX* wcx)
{
	// Register the window class.
	m_sClassName = wcx->lpszClassName;

	if (RegisterClassEx(wcx) == 0)
		return FALSE;
	else
		return TRUE;
}

inline LRESULT CALLBACK CWnd::stWinMsgHandler(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
{
	CWnd* pWnd;

	if (uMsg == WM_NCCREATE)
	{
		// get the pointer to the window from lpCreateParams which was set in CreateWindow
		SetWindowLong(hwnd, GWL_USERDATA, (long)((LPCREATESTRUCT(lParam))->lpCreateParams));
	}

	// get the pointer to the window
	pWnd = GetObjectFromWindow(hwnd);

	// if we have the pointer, go to the message handler of the window
	// else, use DefWindowProc
	if (pWnd)
		return pWnd->WinMsgHandler(hwnd, uMsg, wParam, lParam);
	else
		return DefWindowProc(hwnd, uMsg, wParam, lParam);
}

inline BOOL CWnd::Create()
{
	// Create the window
	RECT rect;

	rect.top = 0;
	rect.left = 0;
	rect.right = 600;
	rect.bottom = 400;

	return Create(WS_OVERLAPPEDWINDOW | WS_VISIBLE, &rect);
}

inline BOOL CWnd::Create(DWORD dwStyles, RECT* rect)
{
	// Create the window

	// send the this pointer as the window creation parameter
	m_hWnd = CreateWindow(m_sClassName, m_sWindowTitle, dwStyles, rect->left, rect->top,
		rect->right - rect->left, rect->bottom - rect->top, NULL, NULL, m_hInstance,
		(void *)this);

	return (m_hWnd != NULL);
}

inline BOOL CWnd::CreateEx(DWORD dwExStyle, LPCTSTR lpszClassName,
									LPCTSTR lpszWindowName, DWORD dwStyle, RECT& rect,
									HWND hwndParent, HMENU nIDorHMenu, LPVOID lpParam)
{
	if(HIWORD(lpszClassName))
		m_sClassName = lpszClassName;
	m_sWindowTitle = lpszWindowName;
	m_hWnd = ::CreateWindowEx(dwExStyle, lpszClassName, lpszWindowName, dwStyle, rect.left, rect.top,
		rect.right - rect.left, rect.bottom - rect.top, hwndParent, nIDorHMenu, m_hInstance, (void *)this);
	return !!m_hWnd;
}

#endif

