//-----------------------------------------------------------------------------
// Name:        ShellExt.cpp
// Product:     ClamWin Antivirus
//
// Author:      alch [alch at users dot sourceforge dot net]
//
// Created:     2004/19/03
// Copyright:   Copyright alch (c) 2004
// Licence:
//   This program is free software; you can redistribute it and/or modify
//   it under the terms of the GNU General Public License as published by
//   the Free Software Foundation; either version 2 of the License, or
//   (at your option) any later version.
//
//   This program is distributed in the hope that it will be useful,
//   but WITHOUT ANY WARRANTY; without even the implied warranty of
//   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//   GNU General Public License for more details.
//
//   You should have received a copy of the GNU General Public License
//   along with this program; if not, write to the Free Software
//   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

//-----------------------------------------------------------------------------

//
// Initialize GUIDs (should be done only and at-least once per DLL/EXE)
//
#include <windows.h>
#include <shlobj.h>
#define INITGUID
#include <initguid.h>
#include <shlguid.h>
#include "ShellExt.h"


//
// Global variables
//
UINT      g_cRefThisDll = 0;    // Reference count of this DLL.
HINSTANCE g_hmodThisDll = NULL; // Handle to this DLL itself.

extern "C" int APIENTRY DllMain(HINSTANCE hInstance, DWORD dwReason, LPVOID lpReserved)
{
	if (dwReason == DLL_PROCESS_ATTACH)
		g_hmodThisDll = hInstance;

	return TRUE;   // ok
}

//---------------------------------------------------------------------------
// DllCanUnloadNow
//---------------------------------------------------------------------------
STDAPI  DllCanUnloadNow(void)
{
	return (g_cRefThisDll == 0 ? S_OK : S_FALSE);
}

//---------------------------------------------------------------------------
// DllGetClassObject
//---------------------------------------------------------------------------
STDAPI DllGetClassObject(REFCLSID rclsid, REFIID riid, LPVOID *ppvOut)
{
	*ppvOut = NULL;

	if (IsEqualIID(rclsid, CLSID_ShellExtension))
	{
		CShellExtClassFactory *pcf = new CShellExtClassFactory;

		return pcf->QueryInterface(riid, ppvOut);
	}

	return CLASS_E_CLASSNOTAVAILABLE;
}

//---------------------------------------------------------------------------
// CShellExtClassFactory::CShellExtClassFactory
//---------------------------------------------------------------------------

CShellExtClassFactory::CShellExtClassFactory()
{
	m_cRef = 0L;

	g_cRefThisDll++;
}

//---------------------------------------------------------------------------
// CShellExtClassFactory::~CShellExtClassFactory
//---------------------------------------------------------------------------

CShellExtClassFactory::~CShellExtClassFactory()
{
	g_cRefThisDll--;
}

//---------------------------------------------------------------------------
// CShellExtClassFactory::QueryInterface
//---------------------------------------------------------------------------

STDMETHODIMP CShellExtClassFactory::QueryInterface(REFIID riid,
                                                   LPVOID FAR *ppv)
{
	*ppv = NULL;

	// Any interface on this object is the object pointer

	if (IsEqualIID(riid, IID_IUnknown) || IsEqualIID(riid, IID_IClassFactory))
	{
		*ppv = (LPCLASSFACTORY)this;

		AddRef();

		return NOERROR;
	}

	return E_NOINTERFACE;
}

//---------------------------------------------------------------------------
// CShellExtClassFactory::AddRef
//---------------------------------------------------------------------------

STDMETHODIMP_(ULONG) CShellExtClassFactory::AddRef()
{
	return ++m_cRef;
}

//---------------------------------------------------------------------------
// CShellExtClassFactory::Release
//---------------------------------------------------------------------------

STDMETHODIMP_(ULONG) CShellExtClassFactory::Release()
{
	if (--m_cRef)
		return m_cRef;

	delete this;

	return 0L;
}

//---------------------------------------------------------------------------
// CShellExtClassFactory::CreateInstance
//---------------------------------------------------------------------------

STDMETHODIMP CShellExtClassFactory::CreateInstance(LPUNKNOWN pUnkOuter,
																	REFIID riid,
																	LPVOID *ppvObj)
{
	*ppvObj = NULL;

	// Shell extensions typically don't support aggregation (inheritance)

	if (pUnkOuter)
		return CLASS_E_NOAGGREGATION;

	// Create the main shell extension object.  The shell will then call
	// QueryInterface with IID_IShellExtInit--this is how shell extensions are
	// initialized.

	LPCSHELLEXT pShellExt = new CShellExt();  //Create the CShellExt object

	if (NULL == pShellExt)
		return E_OUTOFMEMORY;

	return pShellExt->QueryInterface(riid, ppvObj);
}

//---------------------------------------------------------------------------
// CShellExtClassFactory::LockServer
//---------------------------------------------------------------------------

STDMETHODIMP CShellExtClassFactory::LockServer(BOOL fLock)
{
	return NOERROR;
}

// *********************** CShellExt *************************

//---------------------------------------------------------------------------
// CShellExt::CShellExt
//---------------------------------------------------------------------------

CShellExt::CShellExt()
{
	m_cRef = 0L;
	m_pDataObj = NULL;
	m_szPath = NULL;

	g_cRefThisDll++;
}

//---------------------------------------------------------------------------
// CShellExt::~CShellExt
//---------------------------------------------------------------------------

CShellExt::~CShellExt()
{
    if (m_szPath)
        delete [] m_szPath;
	if (m_pDataObj)
		m_pDataObj->Release();

	g_cRefThisDll--;
}

//---------------------------------------------------------------------------
// CShellExt::QueryInterface
//---------------------------------------------------------------------------

STDMETHODIMP CShellExt::QueryInterface(REFIID riid, LPVOID FAR *ppv)
{
	*ppv = NULL;

	if (IsEqualIID(riid, IID_IShellExtInit) || IsEqualIID(riid, IID_IUnknown))
		*ppv = (LPSHELLEXTINIT)this;
	else if (IsEqualIID(riid, IID_IContextMenu))
		*ppv = (LPCONTEXTMENU)this;
	if (*ppv)
	{
		AddRef();
		return NOERROR;
	}
	return E_NOINTERFACE;
}

//---------------------------------------------------------------------------
// CShellExt::AddRef
//---------------------------------------------------------------------------

STDMETHODIMP_(ULONG) CShellExt::AddRef()
{
	return ++m_cRef;
}

//---------------------------------------------------------------------------
// CShellExt::Release
//---------------------------------------------------------------------------

STDMETHODIMP_(ULONG) CShellExt::Release()
{
	if (--m_cRef)
		return m_cRef;

	delete this;

	return 0L;
}
