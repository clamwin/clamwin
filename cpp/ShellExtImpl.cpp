//-----------------------------------------------------------------------------
// Name:        ShellExtImpl.cpp
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

#include <windows.h>
#include <tchar.h>
#include <stdio.h>
#include <shlobj.h>
#include "ShellExt.h"
#include <stdlib.h>
#define _(str) gettext(str)
#define ResultFromShort(i)  ResultFromScode(MAKE_SCODE(SEVERITY_SUCCESS, 0, (USHORT)(i)))


extern HINSTANCE	g_hmodThisDll;	// Handle to this DLL itself.

static int dyn_libintl_init(void);

static HINSTANCE hLibintlDLL = 0;

static char *null_libintl_gettext(const char *);
static char *null_libintl_textdomain(const char *);
static char *null_libintl_bindtextdomain(const char *, const char *);
static char *null_libintl_bind_textdomain_codeset(const char *, const char *);

static char *(*dyn_libintl_gettext)(const char *) = null_libintl_gettext;
static char *(*dyn_libintl_textdomain)(const char *) = null_libintl_textdomain;
static char *(*dyn_libintl_bindtextdomain)(const char *, const char *) = null_libintl_bindtextdomain;
static char *(*dyn_libintl_bind_textdomain_codeset)(const char *, const char *) = null_libintl_bind_textdomain_codeset;

TCHAR szClamWinPath[MAX_PATH] = _T("");


void setClamWinPath() {

    DWORD dwType, cbData;
    // get path to ClamWin
    // Try registry first
    HKEY hKey;
    DWORD len;

    // try in hkey_current_user
    if (ERROR_SUCCESS == RegOpenKeyEx(HKEY_CURRENT_USER, _T("Software\\ClamWin"), 0, KEY_READ, &hKey))
    {
        cbData = sizeof(szClamWinPath);
        RegQueryValueEx(hKey, _T("Path"), NULL, &dwType, (PBYTE)szClamWinPath, &cbData);
        CloseHandle(hKey);
    }
    // try in hkey_local_machine if failed
    if (!_tcslen(szClamWinPath) &&
        (ERROR_SUCCESS == RegOpenKeyEx(HKEY_LOCAL_MACHINE, _T("Software\\ClamWin"), 0, KEY_READ, &hKey)))

    {
        cbData = sizeof(szClamWinPath);
        RegQueryValueEx(hKey, _T("Path"), NULL, &dwType, (PBYTE)szClamWinPath, &cbData);
        CloseHandle(hKey);
    }

    if(!_tcslen(szClamWinPath))
    {
        // could not retrieve from registry
        // try in the same folder as the shell extension
        TCHAR szModule[MAX_PATH];
        if(GetModuleFileName(NULL, szModule, sizeof(szModule)))
        {
            // get folder name
            _tsplitpath(szModule, NULL, szClamWinPath, NULL, NULL);
        }
    }

}    

void getI18NString() {

    setClamWinPath();
    PTCHAR szLibIntlPath;

	//FILE* fp = fopen("c:\\shellextimpl.log", "w+");

	szLibIntlPath = new TCHAR[MAX_PATH];
	szLibIntlPath[0] = _T('\0');

    _tcsncat(szLibIntlPath, szClamWinPath, MAX_PATH);
    _tcsncat(szLibIntlPath, _T("\\libintl-1.dll"), MAX_PATH);

	hLibintlDLL = LoadLibrary(szLibIntlPath);

	//if (! hLibintlDLL) {
	//	fprintf(fp, "Could not load libintl dll\n");
	//} else {
	//	fprintf(fp, "Successfully loaded libintl dll\n");
	//}

	FARPROC* bindtextdomainPtr        = (FARPROC*)&dyn_libintl_bindtextdomain;
	FARPROC* textdomainPtr            = (FARPROC*)&dyn_libintl_textdomain;
	FARPROC* gettextPtr               = (FARPROC*)&dyn_libintl_gettext;
	FARPROC* bindtextdomaincodesetPtr = (FARPROC*)&dyn_libintl_bind_textdomain_codeset;

	*bindtextdomainPtr        = GetProcAddress(hLibintlDLL, "bindtextdomain");
	*textdomainPtr            = GetProcAddress(hLibintlDLL, "textdomain");
	*gettextPtr               = GetProcAddress(hLibintlDLL, "gettext");
	*bindtextdomaincodesetPtr = GetProcAddress(hLibintlDLL, "bind_textdomain_codeset");

	//if (bindtextdomaincodesetPtr == NULL) {
	//	fprintf(fp, "Could not resolve bindtexdomaincodeset\n");
	//} else {
	//	fprintf(fp, "Successfully resolved bindtextdomaincodeset\n");
	//}

    DWORD len;

	char szLangVar[20];
	char szLanguage[5];
	char szCountry[5];

	len = GetLocaleInfo(LOCALE_USER_DEFAULT, LOCALE_SABBREVLANGNAME, (LPTSTR)szLanguage, 5);
	if (len > 2) {
		szLanguage[2] = 0;
	}
	strlwr(szLanguage);
	len = GetLocaleInfo(LOCALE_USER_DEFAULT, LOCALE_SABBREVCTRYNAME, (LPTSTR)szCountry, 5);
	if (len > 2) {
		szCountry[2] = 0;
	}
	strcpy(szLangVar, "LANGUAGE=");
	strcat(szLangVar, szLanguage);
	strcat(szLangVar, "_");
	strcat(szLangVar, szCountry);

	//fprintf(fp, "[%s]", szLangVar);

	putenv(szLangVar);

    PTCHAR szLocalePath;
	szLocalePath = new TCHAR[MAX_PATH];
	szLocalePath[0] = _T('\0');

    _tcsncat(szLocalePath, szClamWinPath, MAX_PATH);
    _tcsncat(szLocalePath, _T("\\..\\locale"), MAX_PATH);
	//fprintf(fp, "Locale directory [%s]", szLocalePath);

	dyn_libintl_bindtextdomain("ShellExtImpl", szLocalePath);
	dyn_libintl_bind_textdomain_codeset("ShellExtImpl", "UTF-8");
	dyn_libintl_textdomain("ShellExtImpl");

	//fprintf(fp, dyn_libintl_gettext("Scan For Viruses With ClamWin"));
	//fclose(fp);

    delete [] szLibIntlPath;
    szLibIntlPath = NULL;

    delete [] szLocalePath;
    szLocalePath = NULL;

}

static char *null_libintl_gettext(const char *msgid)
{
    return (char *)msgid;
}

static char *null_libintl_bindtextdomain(const char *domainname, const char *dirname)
{
    return NULL;
}

static char *null_libintl_bind_textdomain_codeset(const char *domainname, const char *dirname)
{
    return NULL;
}

static char *null_libintl_textdomain(const char* domainname)
{
    return NULL;
}








int _tcsreplace(LPTSTR sz, TCHAR chr,  TCHAR repl_chr)
{
    int count = 0;

    for (; *sz!=_T('\0'); sz++)
        if (*sz == chr) {
            *sz = repl_chr;
            count++;
        }
    return count;
}

//
//  FUNCTION: CShellExt::Initialize(LPCITEMIDLIST, LPDATAOBJECT, HKEY)
//
//  PURPOSE: Called by the shell when initializing a context menu or property
//           sheet extension.
//
//  PARAMETERS:
//    pIDFolder - Specifies the parent folder
//    pDataObj  - Spefifies the set of items selected in that folder.
//    hRegKey   - Specifies the type of the focused item in the selection.
//
//  RETURN VALUE:
//
//    NOERROR in all cases.
//
//  COMMENTS:   Note that at the time this function is called, we don't know
//              (or care) what type of shell extension is being initialized.
//              It could be a context menu or a property sheet.
//

STDMETHODIMP CShellExt::Initialize(LPCITEMIDLIST pIDFolder,
                                   LPDATAOBJECT pDataObj,
                                   HKEY hRegKey)
{
	HRESULT hres = E_FAIL;
	STGMEDIUM medium;
	FORMATETC fmte = {CF_HDROP, NULL, DVASPECT_CONTENT, -1, TYMED_HGLOBAL};
	TCHAR szPath[MAX_PATH];
	INT numFiles;
	size_t len;


	// Initialize can be called more than once
	if (m_pDataObj)
		m_pDataObj->Release();

	// duplicate the object pointer and registry handle
	if (pDataObj)
	{
		m_pDataObj = pDataObj;
		pDataObj->AddRef();
	}

	// use the given IDataObject to get a list of filenames (CF_HDROP)
	hres = pDataObj->GetData(&fmte, &medium);

	if(FAILED(hres))
		return E_FAIL;

	// find out how many files the user selected
	// not more than 250 though, otherwise explorer crashes
	numFiles = DragQueryFile((HDROP)medium.hGlobal, (UINT)-1, NULL, 0);
	if(numFiles > 250)
		return E_FAIL;

	// free old path (just in case)
	if(m_szPath)
	{
        delete [] m_szPath;
 	    m_szPath = NULL;
    }
	// allocate memory for our combined path
	// add length of [ --path=""]
	INT cbPath = (MAX_PATH + 10) * numFiles;
	m_szPath = new TCHAR[cbPath];
	m_szPath[0] = _T('\0');
	for(int i = 0; i < numFiles; i++)
	{
		DragQueryFile((HDROP)medium.hGlobal, i, szPath, sizeof(szPath));
		// check the long path validity for a unicode build
#if defined UNICODE || defined _UNICODE
		{
			CHAR atemp[MAX_PATH];			
			BOOL invalid;
			if(!WideCharToMultiByte(CP_OEMCP, WC_NO_BEST_FIT_CHARS, szPath, -1, 
      		  atemp, sizeof(atemp), NULL, &invalid) || invalid)
    		{
    			WCHAR wtemp[MAX_PATH];
    			// unicode name is not directly tranleatable to ascii, use the shortname instead        		 
       		if(GetShortPathNameW(szPath, wtemp, sizeof(wtemp)) > 0)
   	  			wcscpy(szPath, wtemp);
    		}    		
		}
#endif
		// convert \ to / so cygwin doesn't go crazy (particularly over UNC names)
		_tcsreplace(szPath, _T('\\'), _T('/'));
		len = _tcslen(szPath);
		// remove last slash from the scanning path
        if(szPath[len-1] == _T('/'))
            szPath[len-1] = _T('\0');
        _tcsncat(m_szPath, " --path=\"", cbPath);
        _tcsncat(m_szPath, szPath, cbPath);
        _tcsncat(m_szPath, "\"", cbPath);
	}
	::ReleaseStgMedium(&medium);

	return NOERROR;
}


//
//  FUNCTION: CShellExt::QueryContextMenu(HMENU, UINT, UINT, UINT, UINT)
//
//  PURPOSE: Called by the shell just before the context menu is displayed.
//           This is where you add your specific menu items.
//
//  PARAMETERS:
//    hMenu      - Handle to the context menu
//    indexMenu  - Index of where to begin inserting menu items
//    idCmdFirst - Lowest value for new menu ID's
//    idCmtLast  - Highest value for new menu ID's
//    uFlags     - Specifies the context of the menu event
//
//  RETURN VALUE:
//
//
//  COMMENTS:
//
// The menu text
STDMETHODIMP CShellExt::QueryContextMenu(HMENU hMenu,UINT indexMenu,UINT idCmdFirst,UINT idCmdLast,UINT uFlags)
{

	UINT			idCmd = idCmdFirst;
	HRESULT		hr = E_INVALIDARG;
	getI18NString();

	// Seperator
	::InsertMenu(hMenu, indexMenu++, MF_SEPARATOR|MF_BYPOSITION, 0, NULL);
	//::InsertMenu(hMenu, indexMenu++, MF_STRING|MF_BYPOSITION, idCmd++, dyn_libintl_gettext("Scan For Viruses With ClamWin"));
	::InsertMenu(hMenu, indexMenu++, MF_STRING|MF_BYPOSITION, idCmd++, dyn_libintl_gettext("Scan with ClamWin Free Antivirus"));
	// ::InsertMenu(hMenu, indexMenu++, MF_STRING|MF_BYPOSITION, idCmd++, _T(_("Scan with ClamWin Free Antivirus")));
	// Seperator
	::InsertMenu(hMenu, indexMenu++, MF_SEPARATOR|MF_BYPOSITION, 0, NULL);

	return ResultFromShort(idCmd-idCmdFirst);	//Must return number of menu
	//items we added.
}

BOOL CShellExt::Scan(HWND hwnd)
{
    size_t len;
    if(!m_szPath || !_tcslen(m_szPath))
    {
        MessageBox(hwnd, _T("Error: Unable to retrieve Path."), _T("ClamWin Free Antivirus"), MB_OK | MB_ICONERROR);
        return FALSE;
    }

    DWORD dwType, cbData;
    size_t szCmdSize = MAX_PATH*3 + _tcslen(m_szPath);
    PTCHAR szCmd = new TCHAR[szCmdSize];
    TCHAR szClamWinPath[MAX_PATH] = _T("");
    TCHAR szParams[MAX_PATH*2] = _T("");
    TCHAR szPathExpanded[MAX_PATH], szParamsExpanded[MAX_PATH*2];
    // get path to ClamWin
    // Try registry first
    HKEY hKey;
    // try in hkey_current_user
    if (ERROR_SUCCESS == RegOpenKeyEx(HKEY_CURRENT_USER, _T("Software\\ClamWin"), 0, KEY_READ, &hKey))
    {
        cbData = sizeof(szClamWinPath);
        RegQueryValueEx(hKey, _T("Path"), NULL, &dwType, (PBYTE)szClamWinPath, &cbData);
        CloseHandle(hKey);
    }
    // try in hkey_local_machine if failed
    if (!_tcslen(szClamWinPath) &&
    		(ERROR_SUCCESS == RegOpenKeyEx(HKEY_LOCAL_MACHINE, _T("Software\\ClamWin"), 0, KEY_READ, &hKey)))

    {
        cbData = sizeof(szClamWinPath);
        RegQueryValueEx(hKey, _T("Path"), NULL, &dwType, (PBYTE)szClamWinPath, &cbData);
        CloseHandle(hKey);
    }

    if(!_tcslen(szClamWinPath))
    {
        // could not retrieve from registry
        // try in the same folder as the shell extension
        TCHAR szModule[MAX_PATH];
        if(GetModuleFileName(NULL, szModule, sizeof(szModule)))
        {
            // get folder name
            _tsplitpath(szModule, NULL, szClamWinPath, NULL, NULL);
        }
    }
    len = _tcslen(szClamWinPath);
    if(!len)
    {
        MessageBox(hwnd, _T("Error: Unable to retrieve path to ClamWin. Please reinstall ClamWin Free Antivirus"), _T("ClamWin Free Antivirus"), MB_OK | MB_ICONERROR);
        delete [] szCmd;
        return FALSE;
    }
    // Expand Env
    ExpandEnvironmentStrings(szClamWinPath, szPathExpanded, sizeof(szPathExpanded));
    len = _tcslen(szPathExpanded);
    // remove trailing slash
    if(szPathExpanded[len-1] == _T('\\'))
        szPathExpanded[len-1] = _T('\0');
    _sntprintf(szCmd, szCmdSize, _T("\"%s\\%s\" --mode=scanner %s"),
                szPathExpanded, _T("ClamWin.exe"), m_szPath);

    // read  optional params from registry
    if (ERROR_SUCCESS == RegOpenKeyEx(HKEY_CURRENT_USER,
                _T("Classes\\CLSID\\{65713842-C410-4f44-8383-BFE01A398C90}\\InProcServer32"), 0, KEY_READ, &hKey) ||
        ERROR_SUCCESS == RegOpenKeyEx(HKEY_LOCAL_MACHINE,
                _T("Classes\\CLSID\\{65713842-C410-4f44-8383-BFE01A398C90}\\InProcServer32"), 0, KEY_READ, &hKey))
    {
        cbData = sizeof(szParams);
        RegQueryValueEx(hKey, _T("params"), NULL, &dwType, (PBYTE)szParams, &cbData);
        CloseHandle(hKey);
        // append params if exist
        if (szParams[0] != _T('\0'))
        {
            // Expand Env
            ExpandEnvironmentStrings(szParams, szParamsExpanded, sizeof(szParamsExpanded));
            _tcsncat(szCmd, _T(" "), sizeof(szCmd));
            _tcsncat(szCmd, szParamsExpanded, sizeof(szCmd));
        }
    }

    STARTUPINFO si;
    PROCESS_INFORMATION pi;

    ZeroMemory( &si, sizeof(si) );
    si.cb = sizeof(si);

    ZeroMemory( &pi, sizeof(pi) );

    // Start the child process.
    if( !CreateProcess( NULL, // No module name (use command line).
        szCmd,            // Command line.
        NULL,             // Process handle not inheritable.
        NULL,             // Thread handle not inheritable.
        FALSE,            // Set handle inheritance to FALSE.
        0,                // No creation flags.
        NULL,             // Use parent's environment block.
        NULL,             // Use parent's starting directory.
        &si,              // Pointer to STARTUPINFO structure.
        &pi )             // Pointer to PROCESS_INFORMATION structure.
    )
    {
        TCHAR szMsg[MAX_PATH*2];
        _sntprintf(szMsg, sizeof(szMsg), _T("Error: Unable to execute command %s."), szCmd);
        MessageBox(hwnd, szMsg, _T("ClamWin Free Antivirus"), MB_OK | MB_ICONERROR);        
        delete [] szCmd;
        return FALSE;
    }
    delete [] szCmd;

    // Close process and thread handles.
    CloseHandle( pi.hProcess );
    CloseHandle( pi.hThread );

    return TRUE;
}
//
//  FUNCTION: CShellExt::InvokeCommand(LPCMINVOKECOMMANDINFO)
//
//  PURPOSE: Called by the shell after the user has selected on of the
//           menu items that was added in QueryContextMenu().
//
//  PARAMETERS:
//    lpcmi - Pointer to an CMINVOKECOMMANDINFO structure
//
//  RETURN VALUE: HRESULT code signifying success or failure;NOERROR if no error
//
//
//  COMMENTS:
//
STDMETHODIMP CShellExt::InvokeCommand(LPCMINVOKECOMMANDINFO lpcmi)
{
	HRESULT			hr = E_INVALIDARG;

	//If HIWORD(lpcmi->lpVerb) then we have been called programmatically
	//and lpVerb is a command that should be invoked.  Otherwise, the shell
	//has called us, and LOWORD(lpcmi->lpVerb) is the menu ID the user has
	//selected.  Actually, it's (menu ID - idCmdFirst) from QueryContextMenu().
	if (!HIWORD(lpcmi->lpVerb))
	{
		UINT idCmd = LOWORD(lpcmi->lpVerb);
		switch (idCmd)
		{
		case 0:
		    Scan(lpcmi->hwnd);
			break;
		}
		hr = NOERROR;
	}
	return hr;
}


//
//  FUNCTION: CShellExt::GetCommandString(UINT idCmd,UINT uFlags,UINT FAR *reserved,LPSTR pszName,UINT cchMax)
//
//  PURPOSE: Called by the shell to retreive the cononical command name
//			 or help text for a menu item added by a context menu extension handler
//
//  PARAMETERS:
//	  idCmd - Menu item ID offset
//    uFlags - Value specifying the type of information to retreive
//    *reserved - Pointer to reserved value
//    pszName - Pointer to buffer to receive name string or help text
//    cchMax - Buffer size
//
//  RETURN VALUE: HRESULT code signifying success or failure;NOERROR if no error
//
//
//  COMMENTS:
//
STDMETHODIMP CShellExt::GetCommandString(UINT_PTR idCmd, UINT uType, UINT *pwReserved, LPSTR pszName, UINT cchMax)
{

	switch (idCmd)
	{
	case 0:
		if (GCS_HELPTEXTW == uType)
			wcsncpy((LPWSTR)pszName, L"ClamWin Free Antivirus", cchMax);	
		else if (GCS_HELPTEXTA == uType)
			strncpy(pszName, "ClamWin Free Antivirus", cchMax);
		break;
   }
	return NOERROR;
}
