/*-----------------------------------------------------------------------------
# Name:        BalloonTip.h
# Product:     ClamWin Antivirus
# Author:      alch [alch at users dot sourceforge dot net]
#
# Created:     2004/11/05
# Copyright:   Copyright alch (c) 2004
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
// BalloonTip.h : main header file for the BALLOONTIP DLL
//

#if !defined(AFX_BALLOONTIP_H__5E25FB3F_95A6_47AC_AF18_4340F5A9CCEC__INCLUDED_)
#define AFX_BALLOONTIP_H__5E25FB3F_95A6_47AC_AF18_4340F5A9CCEC__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CBalloonTipApp
// See BalloonTip.cpp for the implementation of this class
//

class CBalloonTipApp : public CWinApp
{
public:
	CBalloonTipApp();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CBalloonTipApp)
	//}}AFX_VIRTUAL

	//{{AFX_MSG(CBalloonTipApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_BALLOONTIP_H__5E25FB3F_95A6_47AC_AF18_4340F5A9CCEC__INCLUDED_)
