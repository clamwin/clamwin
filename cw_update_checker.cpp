/*
 * ClamWin Free Antivirus — CWUpdateChecker implementation
 *
 * Uses WinINet (InternetOpenA / HttpOpenRequestA) for HTTPS GET to
 * the GitHub Releases API.  Parses the "tag_name" field from the
 * JSON response for a semantic version comparison.
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

#include "cw_update_checker.h"
#include "cw_gui_shared.h"   /* CLAMWIN_VERSION_STR */
#include "cw_text_conv.h"

#include <wininet.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#pragma comment(lib, "wininet.lib")

/* ─── Hardcoded endpoints ───────────────────────────────────── */

static const char* CW_GITHUB_API_HOST      = "api.github.com";
static const char* CW_GITHUB_API_PATH      = "/repos/clamwin/clamwin/releases/latest";
static const char* CW_LEGACY_UPDATE_HOST   = "www.clamwin.com";
static const char* CW_LEGACY_UPDATE_PATH   = "/latest-version.txt";
static const char* CW_DOWNLOAD_PAGE         = "https://www.clamwin.com/download";

/* GitHub API requires modern TLS; skip check on legacy OS families (Win9x/XP). */
static bool canUseGithubTlsOnThisOs()
{
    OSVERSIONINFO osv;
    memset(&osv, 0, sizeof(osv));
    osv.dwOSVersionInfoSize = sizeof(osv);

    if (!GetVersionEx(&osv))
        return true; /* If detection fails, keep behavior unchanged. */

    return osv.dwMajorVersion >= 6;
}

static bool extractVersionToken(const char* text, int textLen, char* out, int outCap)
{
    if (!text || textLen <= 0 || !out || outCap <= 0)
        return false;

    for (int i = 0; i < textLen; ++i)
    {
        int j = i;
        if (text[j] == 'v' || text[j] == 'V')
            ++j;

        if (j >= textLen || text[j] < '0' || text[j] > '9')
            continue;

        int k = j;
        bool sawDot = false;
        while (k < textLen)
        {
            char c = text[k];
            if ((c >= '0' && c <= '9') || c == '.')
            {
                if (c == '.')
                    sawDot = true;
                ++k;
                continue;
            }
            break;
        }

        if (!sawDot)
            continue;

        int n = k - i;
        if (n <= 0 || n >= outCap)
            continue;

        memcpy(out, text + i, n);
        out[n] = '\0';
        return true;
    }

    return false;
}

const char* CWUpdateChecker::apiUrl()
{
    return "https://api.github.com/repos/clamwin/clamwin/releases/latest";
}

const char* CWUpdateChecker::downloadUrl()
{
    return CW_DOWNLOAD_PAGE;
}

/* ─── Version parsing / comparison ──────────────────────────── */

bool CWUpdateChecker::parseVersion(const char* str, int& major, int& minor, int& patch)
{
    if (!str)
        return false;

    /* Skip leading 'v' or 'V' (common in Git tags like "v1.2.3") */
    if (*str == 'v' || *str == 'V')
        ++str;

    /* Skip legacy epoch prefix like "0:" */
    const char* colon = strchr(str, ':');
    if (colon)
        str = colon + 1;

    major = minor = patch = 0;
    int n = sscanf(str, "%d.%d.%d", &major, &minor, &patch);
    return n >= 2;  /* at least major.minor */
}

bool CWUpdateChecker::isNewerVersion(const char* remote)
{
    int rMaj = 0, rMin = 0, rPat = 0;
    int lMaj = 0, lMin = 0, lPat = 0;

    if (!parseVersion(remote, rMaj, rMin, rPat))
        return false;
    if (!parseVersion(CLAMWIN_VERSION_STR, lMaj, lMin, lPat))
        return false;

    if (rMaj != lMaj) return rMaj > lMaj;
    if (rMin != lMin) return rMin > lMin;
    return rPat > lPat;
}

/* ─── Constructor / Destructor ──────────────────────────────── */

CWUpdateChecker::CWUpdateChecker()
    : m_hThread(NULL)
    , m_hwndTarget(NULL)
{
}

CWUpdateChecker::~CWUpdateChecker()
{
    waitForThread();
}

void CWUpdateChecker::waitForThread()
{
    if (m_hThread)
    {
        WaitForSingleObject(m_hThread, INFINITE);
        CloseHandle(m_hThread);
        m_hThread = NULL;
    }
}

/* ─── Start background check ───────────────────────────────── */

void CWUpdateChecker::startCheck(HWND hwndTarget)
{
    if (m_hThread)
        return;   /* already in flight */

    m_hwndTarget = hwndTarget;
    DWORD tid = 0; /* Win98 requires a valid lpThreadId pointer, NULL is not accepted */
    m_hThread = CreateThread(NULL, 0, threadProc, this, 0, &tid);
}

DWORD WINAPI CWUpdateChecker::threadProc(LPVOID param)
{
    CWUpdateChecker* self = static_cast<CWUpdateChecker*>(param);
    if (self)
        self->doCheck();
    return 0;
}

/* ─── Minimal JSON extraction ───────────────────────────────── *
 * We only need the "tag_name" value from the GitHub response.
 * A full JSON parser is overkill — we search for the key and
 * extract the quoted string value that follows it.
 */

static bool extractTagName(const char* json, int jsonLen, char* out, int outCap)
{
    if (!json || jsonLen <= 0 || !out || outCap <= 0)
        return false;

    const char* key = "\"tag_name\"";
    const char* pos = NULL;

    /* Search safely within the known length */
    for (int i = 0; i <= jsonLen - 10; ++i)
    {
        if (strncmp(json + i, key, 10) == 0)
        {
            pos = json + i + 10;
            break;
        }
    }
    if (!pos)
        return false;

    /* Skip whitespace and colon */
    const char* end = json + jsonLen;
    while (pos < end && (*pos == ' ' || *pos == ':' || *pos == '\t' || *pos == '\n' || *pos == '\r'))
        ++pos;

    if (pos >= end || *pos != '"')
        return false;
    ++pos;  /* skip opening quote */

    int i = 0;
    while (pos < end && *pos != '"')
    {
        if (i >= outCap - 1)
            return false;
        out[i++] = *pos++;
    }

    if (pos >= end || *pos != '"')
        return false;

    out[i] = '\0';
    return i > 0;
}

/* ─── The actual HTTPS check ────────────────────────────────── */

void CWUpdateChecker::doCheck()
{
    CWVersionResult* result = new CWVersionResult();
    memset(result, 0, sizeof(*result));

    HINTERNET hInet = NULL;
    HINTERNET hConn = NULL;
    HINTERNET hReq  = NULL;

    do
    {
        hInet = InternetOpen(CW_ToT("ClamWin/" CLAMWIN_VERSION_STR).c_str(),
                              INTERNET_OPEN_TYPE_PRECONFIG,
                              NULL, NULL, 0);
        if (!hInet)
            break;

        /* Set a reasonable timeout so we don't block forever */
        DWORD timeout = 15000;
        InternetSetOption(hInet, INTERNET_OPTION_CONNECT_TIMEOUT, &timeout, sizeof(timeout));
        InternetSetOption(hInet, INTERNET_OPTION_RECEIVE_TIMEOUT, &timeout, sizeof(timeout));

        const bool modernTls = canUseGithubTlsOnThisOs();
        const char* host = modernTls ? CW_GITHUB_API_HOST : CW_LEGACY_UPDATE_HOST;
        const char* path = modernTls ? CW_GITHUB_API_PATH : CW_LEGACY_UPDATE_PATH;
        INTERNET_PORT port = modernTls ? INTERNET_DEFAULT_HTTPS_PORT : INTERNET_DEFAULT_HTTP_PORT;
        DWORD reqFlags = INTERNET_FLAG_NO_CACHE_WRITE | INTERNET_FLAG_RELOAD | INTERNET_FLAG_NO_UI;
        if (modernTls)
            reqFlags |= INTERNET_FLAG_SECURE;

        hConn = InternetConnect(hInet, CW_ToT(host).c_str(),
                                 port,
                                 NULL, NULL,
                                 INTERNET_SERVICE_HTTP, 0, 0);
        if (!hConn)
            break;

        std::basic_string<TCHAR> acceptTypeValue = CW_ToT(modernTls ? "application/json" : "text/plain");
        const TCHAR* acceptTypes[] = { acceptTypeValue.c_str(), NULL };
        hReq = HttpOpenRequest(hConn, TEXT("GET"), CW_ToT(path).c_str(),
                                NULL, NULL, acceptTypes,
                                reqFlags,
                                0);
        if (!hReq)
            break;

        if (!HttpSendRequest(hReq, NULL, 0, NULL, 0))
            break;

        /* Check HTTP status code */
        DWORD statusCode = 0;
        DWORD statusSize = sizeof(statusCode);
        if (!HttpQueryInfo(hReq, HTTP_QUERY_STATUS_CODE | HTTP_QUERY_FLAG_NUMBER,
                            &statusCode, &statusSize, NULL))
            break;
        if (statusCode != 200)
            break;

        /* Read response body (capped at 32 KB — the real response is ~5 KB) */
        const int MAX_RESPONSE = 32768;
        char* body = (char*)malloc(MAX_RESPONSE + 1);
        if (!body)
            break;

        int totalRead = 0;
        DWORD bytesRead = 0;
        while (totalRead < MAX_RESPONSE)
        {
            if (!InternetReadFile(hReq, body + totalRead,
                                  MAX_RESPONSE - totalRead, &bytesRead))
                break;
            if (bytesRead == 0)
                break;
            totalRead += (int)bytesRead;
        }
        body[totalRead] = '\0';

        char remoteVersion[64] = "";
        bool parsed = false;
        if (modernTls)
            parsed = extractTagName(body, totalRead, remoteVersion, sizeof(remoteVersion));
        else
            parsed = extractVersionToken(body, totalRead, remoteVersion, sizeof(remoteVersion));

        if (parsed)
        {
            if (isNewerVersion(remoteVersion))
            {
                result->available = true;
                parseVersion(remoteVersion, result->major, result->minor, result->patch);
                _snprintf(result->versionStr, sizeof(result->versionStr), "%s", remoteVersion);
                result->versionStr[sizeof(result->versionStr) - 1] = '\0';
            }
        }

        free(body);

    } while (false);

    if (hReq)  InternetCloseHandle(hReq);
    if (hConn) InternetCloseHandle(hConn);
    if (hInet) InternetCloseHandle(hInet);

    /* Post result to the UI thread */
    if (m_hwndTarget && IsWindow(m_hwndTarget))
    {
        PostMessage(m_hwndTarget, WM_CW_VERSION_RESULT,
                     (WPARAM)(result->available ? 1 : 0),
                     (LPARAM)result);
    }
    else
    {
        delete result;
    }
}
