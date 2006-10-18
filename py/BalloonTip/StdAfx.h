/*-----------------------------------------------------------------------------
# Name:        stdafx.h
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
*/

// stdafx.h : include file for standard system include files,
//  or project specific include files that are used frequently, but
//      are changed infrequently
//

#if !defined(AFX_STDAFX_H__2A73A595_B196_4929_B806_D1E2641919D0__INCLUDED_)
#define AFX_STDAFX_H__2A73A595_B196_4929_B806_D1E2641919D0__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
#define _WIN32_WINNT 0x0400
#define WIN32_LEAN_AND_MEAN		// Exclude rarely-used stuff from Windows headers#define WIN32_LEAN_AND_MEAN		// Exclude rarely-used stuff from Windows headers
#include <windows.h>
#include <windowsx.h>
#include <commctrl.h>
#include <Shellapi.h>
#include "StdString.h"
#include "CWnd.h"
#endif // !defined(AFX_STDAFX_H__2A73A595_B196_4929_B806_D1E2641919D0__INCLUDED_)
