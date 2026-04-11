/*
 * ClamWin Free Antivirus — CWUpdateChecker implementation
 *
 * Two TLS back-ends for the HTTPS version check:
 *
 *   Vista+ (dwMajorVersion >= 6) — WinINet + native SChannel TLS 1.2.
 *     Lightweight, uses the OS certificate store, no extra dependencies.
 *
 *   XP / legacy (dwMajorVersion < 6) — libcurl + static OpenSSL, the same
 *     stack clamav-win32's freshclam uses for database updates.  OpenSSL
 *     provides TLS 1.2 independently of the OS.
 *
 * Both paths hit the same GitHub Releases API endpoint and parse
 * the "tag_name" field for a semantic version comparison.
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

#include "cw_update_checker.h"
#include "cw_gui_shared.h"   /* CLAMWIN_VERSION_STR */
#include "cw_text_conv.h"

/* curl must be included before windows.h to avoid winsock conflicts */
#include <curl/curl.h>

#include <wininet.h>
#include <windows.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#pragma comment(lib, "wininet.lib")

/* ─── Hardcoded endpoints ───────────────────────────────────── */

static const char* CW_GITHUB_API_HOST = "api.github.com";
static const char* CW_GITHUB_API_PATH = "/repos/clamwin/clamwin/releases/latest";
static const char* CW_GITHUB_API_URL  = "https://api.github.com/repos/clamwin/clamwin/releases/latest";
static const char* CW_DOWNLOAD_PAGE   = "https://www.clamwin.com/download";

/* User-Agent string sent with every request. */
static const char* CW_USER_AGENT      = "ClamWin/" CLAMWIN_VERSION_STR;

/* ─── OS detection: can the native TLS stack do TLS 1.2? ───── */

static bool canUseNativeTls()
{
    OSVERSIONINFO osv;
    memset(&osv, 0, sizeof(osv));
    osv.dwOSVersionInfoSize = sizeof(osv);

    if (!GetVersionEx(&osv))
        return true; /* assume modern if detection fails */

    /* WinINet/SChannel TLS 1.2 is enabled by default from Windows 8 (6.2).
     * Vista (6.0) has no TLS 1.2 client support at all.
     * Windows 7 (6.1) has TLS 1.2 compiled in but disabled by default.
     * Both of those require curl+OpenSSL since GitHub mandates TLS 1.2. */
    DWORD maj = osv.dwMajorVersion;
    DWORD min = osv.dwMinorVersion;
    return (maj > 6) || (maj == 6 && min >= 2);
}

/* ─── CA bundle path (XP curl path only) ─────────────────────── *
 * Locate curl-ca-bundle.crt next to the executable at runtime.   */

static bool getCaBundlePath(char* out, int outCap)
{
    char exePath[MAX_PATH];
    if (!GetModuleFileNameA(NULL, exePath, MAX_PATH))
        return false;

    char* sep = strrchr(exePath, '\\');
    if (!sep)
        sep = strrchr(exePath, '/');
    if (!sep)
        return false;
    *(sep + 1) = '\0';

    int n = _snprintf(out, outCap, "%scurl-ca-bundle.crt", exePath);
    if (n < 0 || n >= outCap)
        return false;
    out[outCap - 1] = '\0';

    DWORD attr = GetFileAttributesA(out);
    return (attr != INVALID_FILE_ATTRIBUTES && !(attr & FILE_ATTRIBUTE_DIRECTORY));
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

/* ─── Public URL accessors ──────────────────────────────────── */

const char* CWUpdateChecker::apiUrl()
{
    return CW_GITHUB_API_URL;
}

const char* CWUpdateChecker::downloadUrl()
{
    return CW_DOWNLOAD_PAGE;
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
 * We only need the "tag_name" value from the GitHub response.   *
 * A full JSON parser is overkill — search for the key and       *
 * extract the quoted string value that follows it.              */

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

/* ─── Post result to UI thread (shared by both paths) ──────── */

void CWUpdateChecker::postResult(CWVersionResult* result)
{
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

void CWUpdateChecker::fillResult(CWVersionResult* result, const char* remoteVersion)
{
    if (isNewerVersion(remoteVersion))
    {
        result->available = true;
        parseVersion(remoteVersion, result->major, result->minor, result->patch);
        _snprintf(result->versionStr, sizeof(result->versionStr), "%s", remoteVersion);
        result->versionStr[sizeof(result->versionStr) - 1] = '\0';
    }
}

/* ═══════════════════════════════════════════════════════════════
 *  Path A: WinINet + native SChannel TLS 1.2 (Vista+)
 * ═══════════════════════════════════════════════════════════════ */

void CWUpdateChecker::doCheckWinINet()
{
    CWVersionResult* result = new CWVersionResult();
    memset(result, 0, sizeof(*result));

    HINTERNET hInet = NULL;
    HINTERNET hConn = NULL;
    HINTERNET hReq  = NULL;

    do
    {
        hInet = InternetOpen(CW_ToT(CW_USER_AGENT).c_str(),
                              INTERNET_OPEN_TYPE_PRECONFIG,
                              NULL, NULL, 0);
        if (!hInet)
            break;

        DWORD timeout = 15000;
        InternetSetOption(hInet, INTERNET_OPTION_CONNECT_TIMEOUT, &timeout, sizeof(timeout));
        InternetSetOption(hInet, INTERNET_OPTION_RECEIVE_TIMEOUT, &timeout, sizeof(timeout));

        hConn = InternetConnect(hInet, CW_ToT(CW_GITHUB_API_HOST).c_str(),
                                 INTERNET_DEFAULT_HTTPS_PORT,
                                 NULL, NULL,
                                 INTERNET_SERVICE_HTTP, 0, 0);
        if (!hConn)
            break;

        DWORD reqFlags = INTERNET_FLAG_SECURE
                       | INTERNET_FLAG_NO_CACHE_WRITE
                       | INTERNET_FLAG_RELOAD
                       | INTERNET_FLAG_NO_UI;

        std::basic_string<TCHAR> acceptVal = CW_ToT("application/json");
        const TCHAR* acceptTypes[] = { acceptVal.c_str(), NULL };
        hReq = HttpOpenRequest(hConn, TEXT("GET"), CW_ToT(CW_GITHUB_API_PATH).c_str(),
                                NULL, NULL, acceptTypes,
                                reqFlags, 0);
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
        if (extractTagName(body, totalRead, remoteVersion, sizeof(remoteVersion)))
            fillResult(result, remoteVersion);

        free(body);

    } while (false);

    if (hReq)  InternetCloseHandle(hReq);
    if (hConn) InternetCloseHandle(hConn);
    if (hInet) InternetCloseHandle(hInet);

    postResult(result);
}

/* ═══════════════════════════════════════════════════════════════
 *  Path B: libcurl + static OpenSSL (XP / legacy)
 * ═══════════════════════════════════════════════════════════════ */

/* curl response-body accumulator */

struct CurlBuffer
{
    char*  data;
    size_t used;
    size_t cap;
};

static size_t curlWriteCb(char* ptr, size_t size, size_t nmemb, void* userdata)
{
    size_t bytes = size * nmemb;
    CurlBuffer* buf = static_cast<CurlBuffer*>(userdata);

    const size_t MAX_BODY = 65536;
    if (buf->used >= MAX_BODY)
        return bytes;

    size_t toWrite = bytes;
    if (buf->used + toWrite > MAX_BODY)
        toWrite = MAX_BODY - buf->used;

    if (buf->used + toWrite + 1 > buf->cap)
    {
        size_t newCap = buf->used + toWrite + 1;
        char* grown = (char*)realloc(buf->data, newCap);
        if (!grown)
            return 0;
        buf->data = grown;
        buf->cap  = newCap;
    }

    memcpy(buf->data + buf->used, ptr, toWrite);
    buf->used += toWrite;
    buf->data[buf->used] = '\0';
    return bytes;
}

void CWUpdateChecker::doCheckCurl()
{
    CWVersionResult* result = new CWVersionResult();
    memset(result, 0, sizeof(*result));

    CURL*       hCurl = NULL;
    curl_slist* hdrs  = NULL;
    CurlBuffer  body  = { NULL, 0, 0 };

    do
    {
        hCurl = curl_easy_init();
        if (!hCurl)
            break;

        curl_easy_setopt(hCurl, CURLOPT_URL, CW_GITHUB_API_URL);
        curl_easy_setopt(hCurl, CURLOPT_USERAGENT, CW_USER_AGENT);

        hdrs = curl_slist_append(hdrs, "Accept: application/vnd.github+json");
        if (hdrs)
            curl_easy_setopt(hCurl, CURLOPT_HTTPHEADER, hdrs);

        curl_easy_setopt(hCurl, CURLOPT_WRITEFUNCTION, curlWriteCb);
        curl_easy_setopt(hCurl, CURLOPT_WRITEDATA,     &body);

        curl_easy_setopt(hCurl, CURLOPT_CONNECTTIMEOUT, 15L);
        curl_easy_setopt(hCurl, CURLOPT_TIMEOUT,        30L);

        curl_easy_setopt(hCurl, CURLOPT_FOLLOWLOCATION, 1L);
        curl_easy_setopt(hCurl, CURLOPT_MAXREDIRS,      5L);

        curl_easy_setopt(hCurl, CURLOPT_SSL_VERIFYPEER, 1L);
        curl_easy_setopt(hCurl, CURLOPT_SSL_VERIFYHOST, 2L);

        /* On XP the OS cert store is not accessible to OpenSSL.
         * Use the bundled CA bundle if available. */
        char caBundle[MAX_PATH + 32];
        if (getCaBundlePath(caBundle, sizeof(caBundle)))
            curl_easy_setopt(hCurl, CURLOPT_CAINFO, caBundle);

        CURLcode rc = curl_easy_perform(hCurl);
        if (rc != CURLE_OK)
            break;

        long httpStatus = 0;
        curl_easy_getinfo(hCurl, CURLINFO_RESPONSE_CODE, &httpStatus);
        if (httpStatus != 200)
            break;

        if (!body.data)
            break;

        char remoteVersion[64] = "";
        if (extractTagName(body.data, (int)body.used, remoteVersion, sizeof(remoteVersion)))
            fillResult(result, remoteVersion);

    } while (false);

    if (hdrs)      curl_slist_free_all(hdrs);
    if (hCurl)     curl_easy_cleanup(hCurl);
    if (body.data) free(body.data);

    postResult(result);
}

/* ─── Dispatcher ────────────────────────────────────────────── */

void CWUpdateChecker::doCheck()
{
    if (canUseNativeTls())
        doCheckWinINet();
    else
        doCheckCurl();
}
