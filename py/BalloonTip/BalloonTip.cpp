/*-----------------------------------------------------------------------------
# Name:        BalloonTip.cpp
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
// BalloonTip.cpp : Defines the initialization routines for the DLL.
//

#include "stdafx.h"
#include <Python.h>
#include "BalloonHelp.h"
HINSTANCE g_hInstance = NULL; // Handle to this DLL itself.

extern "C" int APIENTRY DllMain(HINSTANCE hInstance, DWORD dwReason, LPVOID lpReserved)
{
	if (dwReason == DLL_PROCESS_ATTACH)
	{
		g_hInstance = hInstance;
	}

	return 1;   // ok
}


// Parse parameters and dispatch to the actual function.
PyObject *BalloonTip_ShowBalloonTip(PyObject *pSelf, PyObject *pArgs) {
	LPTSTR szTitle, szContent, szURL;
	PyObject *pPointTuple;
	INT x, y;
	INT nOptions, nTimeout, hParentWnd, nIcon;
	if(!PyArg_ParseTuple(pArgs, "ssOiiisi", &szTitle, &szContent, &pPointTuple,
								&nIcon, &nOptions, &hParentWnd, &szURL, &nTimeout)) {
		PyErr_SetString(PyExc_StandardError, "ShowBalloonTip() takes 8 parameters");
		return NULL;
	}

	if(!PyArg_ParseTuple(pPointTuple, "ii", &x, &y)){
		PyErr_SetString(PyExc_StandardError, "ShowBalloon() third parameter must be tuple with 2 integers representing tooltip coordinates: (x, y)");
		return NULL;
	}
	POINT pt = {x, y};
	CBalloonHelp::LaunchBalloon(szTitle, szContent,
               pt, (LPCTSTR)nIcon, nOptions,
					(HWND)hParentWnd, szURL, nTimeout);

	Py_INCREF(Py_None);
	return Py_None;
}

extern "C"  __declspec(dllexport) void LaunchBalloon(LPCTSTR strTitle, LPCTSTR strContent,
               POINT& ptAnchor,
               LPCTSTR szIcon,
               unsigned int unOptions,
               HWND hParentWnd,
               LPCTSTR strURL,
               unsigned int unTimeout)
{

	CBalloonHelp::LaunchBalloon(strTitle, strContent,
               ptAnchor, szIcon, unOptions,
					(HWND)hParentWnd, strURL, unTimeout);
}

static PyMethodDef BalloonTipMethods[] = {
	{"ShowBalloonTip", BalloonTip_ShowBalloonTip, METH_VARARGS, "Display the Balloon Tooltip at given location"},
	{NULL, NULL, 0, NULL}
};

// Initialize the BalloonTip module.
extern "C"  __declspec(dllexport) void initBalloonTip(void)
{
	PyObject *module = Py_InitModule("BalloonTip", BalloonTipMethods);
	PyModule_AddIntConstant(module, "CLOSE_ON_LBUTTON_UP", CBalloonHelp::unCLOSE_ON_LBUTTON_UP);
	PyModule_AddIntConstant(module, "CLOSE_ON_MBUTTON_UP", CBalloonHelp::unCLOSE_ON_MBUTTON_UP);
	PyModule_AddIntConstant(module, "CLOSE_ON_RBUTTON_UP", CBalloonHelp::unCLOSE_ON_RBUTTON_UP);
	PyModule_AddIntConstant(module, "CLOSE_ON_LBUTTON_DOWN", CBalloonHelp::unCLOSE_ON_LBUTTON_DOWN);
	PyModule_AddIntConstant(module, "CLOSE_ON_MBUTTON_DOWN", CBalloonHelp::unCLOSE_ON_MBUTTON_DOWN);
	PyModule_AddIntConstant(module, "CLOSE_ON_RBUTTON_DOWN", CBalloonHelp::unCLOSE_ON_RBUTTON_DOWN);
	PyModule_AddIntConstant(module, "CLOSE_ON_MOUSE_MOVE", CBalloonHelp::unCLOSE_ON_MOUSE_MOVE);
	PyModule_AddIntConstant(module, "CLOSE_ON_KEYPRESS", CBalloonHelp::unCLOSE_ON_KEYPRESS);
	PyModule_AddIntConstant(module, "CLOSE_ON_ANYTHING", CBalloonHelp::unCLOSE_ON_ANYTHING);
	PyModule_AddIntConstant(module, "DELAY_CLOSE", CBalloonHelp::unDELAY_CLOSE);
	//PyModule_AddIntConstant(module, "unDELETE_THIS_ON_CLOSE", CBalloonHelp::unDELETE_THIS_ON_CLOSE);
	PyModule_AddIntConstant(module, "SHOW_CLOSE_BUTTON", CBalloonHelp::unSHOW_CLOSE_BUTTON);
	PyModule_AddIntConstant(module, "SHOW_INNER_SHADOW", CBalloonHelp::unSHOW_INNER_SHADOW);
	PyModule_AddIntConstant(module, "SHOW_TOPMOST", CBalloonHelp::unSHOW_TOPMOST);
	PyModule_AddIntConstant(module, "DISABLE_XP_SHADOW", CBalloonHelp::unDISABLE_XP_SHADOW);
	PyModule_AddIntConstant(module, "DISABLE_FADEIN", CBalloonHelp::unDISABLE_FADEIN);
	PyModule_AddIntConstant(module, "DISABLE_FADEOUT", CBalloonHelp::unDISABLE_FADEOUT);
	PyModule_AddIntConstant(module, "DISABLE_FADE", CBalloonHelp::unDISABLE_FADE);
	PyModule_AddStringConstant(module, "SHADOWED_CLASS", "BalloonHelpClassDS");
	PyModule_AddStringConstant(module, "SHADOWLESS_CLASS", "BalloonHelpClass");
}
