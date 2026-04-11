/*
 * ClamWin Free Antivirus — CWUpdateChecker implementation
 *
 * Uses libcurl + static OpenSSL for an HTTPS GET to the GitHub Releases API,
 * mirroring the stack used by clamav-win32's freshclam for database updates.
 * OpenSSL provides TLS 1.2 independently of the Windows SChannel, so this
 * works on all supported platforms including Windows XP and Win98.
 *
 * Parses the "tag_name" field from the JSON response for a semantic
 * version comparison.
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

#include "cw_update_checker.h"
#include "cw_gui_shared.h"   /* CLAMWIN_VERSION_STR */
#include "cw_log_utils.h"    /* CW_DebugLog */

/* curl must be included before windows.h to avoid winsock conflicts */
#include <curl/curl.h>

#include <windows.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

/* ─── Hardcoded endpoints ───────────────────────────────────── */

static const char* CW_GITHUB_API_URL = "https://api.github.com/repos/clamwin/clamwin/releases/latest";
static const char* CW_DOWNLOAD_PAGE  = "https://www.clamwin.com/download";

/* User-Agent string sent with every request. */
static const char* CW_USER_AGENT     = "ClamWin/" CLAMWIN_VERSION_STR;

/* ─── CA bundle path ─────────────────────────────────────────── *
 * On XP and Win98 OpenSSL cannot reach the Windows cert store.  *
 * Locate curl-ca-bundle.crt next to the executable at runtime.  */

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
    , m_debugEnabled(false)
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

void CWUpdateChecker::startCheck(HWND hwndTarget, bool debugEnabled, const std::string& debugLogPath)
{
    if (m_hThread)
    {
        DWORD waitRc = WaitForSingleObject(m_hThread, 0);
        if (waitRc == WAIT_OBJECT_0)
        {
            CloseHandle(m_hThread);
            m_hThread = NULL;
        }
        else
        {
            if (debugEnabled)
                CW_DebugLog(debugLogPath, "[UpdateChecker] Request ignored because a check is already running");
            return;   /* already in flight */
        }
    }

    m_hwndTarget = hwndTarget;
    m_debugEnabled = debugEnabled;
    m_debugLogPath = debugLogPath;
    if (m_debugEnabled)
        CW_DebugLog(m_debugLogPath, "[UpdateChecker] Starting version check: url=%s", CW_GITHUB_API_URL);
    DWORD tid = 0; /* Win98 requires a valid lpThreadId pointer, NULL is not accepted */
    m_hThread = CreateThread(NULL, 0, threadProc, this, 0, &tid);
    if (!m_hThread && m_debugEnabled)
        CW_DebugLog(m_debugLogPath, "[UpdateChecker] Failed to create worker thread (GetLastError=%lu)", GetLastError());
}

DWORD WINAPI CWUpdateChecker::threadProc(LPVOID param)
{
    CWUpdateChecker* self = static_cast<CWUpdateChecker*>(param);
    if (self)
        self->doCheck();
    return 0;
}

/* ─── curl response-body accumulator ───────────────────────── */

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

    /* cap the total response size at 64 KB (real GitHub response is ~5 KB) */
    const size_t MAX_BODY = 65536;
    if (buf->used >= MAX_BODY)
        return bytes;   /* silently discard the rest but report success */

    size_t toWrite = bytes;
    if (buf->used + toWrite > MAX_BODY)
        toWrite = MAX_BODY - buf->used;

    if (buf->used + toWrite + 1 > buf->cap)
    {
        size_t newCap = buf->used + toWrite + 1;
        char* grown = (char*)realloc(buf->data, newCap);
        if (!grown)
            return 0;   /* signal error to curl */
        buf->data = grown;
        buf->cap  = newCap;
    }

    memcpy(buf->data + buf->used, ptr, toWrite);
    buf->used += toWrite;
    buf->data[buf->used] = '\0';
    return bytes;
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

/* ─── The actual HTTPS check (curl + OpenSSL) ───────────────── */

void CWUpdateChecker::doCheck()
{
    CWVersionResult* result = new CWVersionResult();
    memset(result, 0, sizeof(*result));

    CURL*       hCurl = NULL;
    curl_slist* hdrs  = NULL;
    CurlBuffer  body  = { NULL, 0, 0 };
    char        errbuf[CURL_ERROR_SIZE] = {0};

    do
    {
        hCurl = curl_easy_init();
        if (!hCurl)
        {
            if (m_debugEnabled)
                CW_DebugLog(m_debugLogPath, "[UpdateChecker] curl_easy_init failed");
            break;
        }

        curl_easy_setopt(hCurl, CURLOPT_URL, CW_GITHUB_API_URL);

        /* GitHub API requires a non-empty User-Agent */
        curl_easy_setopt(hCurl, CURLOPT_USERAGENT, CW_USER_AGENT);

        /* Accept header so GitHub returns JSON */
        hdrs = curl_slist_append(hdrs, "Accept: application/vnd.github+json");
        if (hdrs)
            curl_easy_setopt(hCurl, CURLOPT_HTTPHEADER, hdrs);

        curl_easy_setopt(hCurl, CURLOPT_WRITEFUNCTION, curlWriteCb);
        curl_easy_setopt(hCurl, CURLOPT_WRITEDATA,     &body);

        curl_easy_setopt(hCurl, CURLOPT_CONNECTTIMEOUT, 15L);
        curl_easy_setopt(hCurl, CURLOPT_TIMEOUT,        30L);

        curl_easy_setopt(hCurl, CURLOPT_FOLLOWLOCATION, 1L);
        curl_easy_setopt(hCurl, CURLOPT_MAXREDIRS,      5L);

        /* TLS peer/host verification — mandatory */
        curl_easy_setopt(hCurl, CURLOPT_SSL_VERIFYPEER, 1L);
        curl_easy_setopt(hCurl, CURLOPT_SSL_VERIFYHOST, 2L);

        /* On XP/Win98 OpenSSL cannot reach the Windows cert store.
         * Use the bundled CA bundle if it exists next to the executable. */
        char caBundle[MAX_PATH + 32];
        if (getCaBundlePath(caBundle, sizeof(caBundle)))
            curl_easy_setopt(hCurl, CURLOPT_CAINFO, caBundle);

        curl_easy_setopt(hCurl, CURLOPT_ERRORBUFFER, errbuf);

        CURLcode rc = curl_easy_perform(hCurl);
        if (rc != CURLE_OK) {
            if (m_debugEnabled) {
                CW_DebugLog(m_debugLogPath, "[UpdateChecker] cURL error %d: %s",
                            (int)rc, errbuf[0] ? errbuf : curl_easy_strerror(rc));
            }
            break;
        }

        long httpStatus = 0;
        curl_easy_getinfo(hCurl, CURLINFO_RESPONSE_CODE, &httpStatus);
        if (httpStatus != 200) {
            if (m_debugEnabled) {
                CW_DebugLog(m_debugLogPath, "[UpdateChecker] HTTP status %ld", httpStatus);
            }
            break;
        }

        if (!body.data)
        {
            if (m_debugEnabled)
                CW_DebugLog(m_debugLogPath, "[UpdateChecker] Empty response body");
            break;
        }

        char remoteVersion[64] = "";
        if (!extractTagName(body.data, (int)body.used, remoteVersion, sizeof(remoteVersion)))
        {
            if (m_debugEnabled)
                CW_DebugLog(m_debugLogPath, "[UpdateChecker] Failed to parse tag_name from response");
            break;
        }

        if (isNewerVersion(remoteVersion))
        {
            result->available = true;
            parseVersion(remoteVersion, result->major, result->minor, result->patch);
            _snprintf(result->versionStr, sizeof(result->versionStr), "%s", remoteVersion);
            result->versionStr[sizeof(result->versionStr) - 1] = '\0';
            if (m_debugEnabled)
                CW_DebugLog(m_debugLogPath, "[UpdateChecker] Newer version available: remote=%s local=%s", remoteVersion, CLAMWIN_VERSION_STR);
        }
        else if (m_debugEnabled)
        {
            CW_DebugLog(m_debugLogPath, "[UpdateChecker] No update available: remote=%s local=%s", remoteVersion, CLAMWIN_VERSION_STR);
        }

    } while (false);

    if (hdrs)      curl_slist_free_all(hdrs);
    if (hCurl)     curl_easy_cleanup(hCurl);
    if (body.data) free(body.data);

    /* Post result to the UI thread */
    if (m_hwndTarget && IsWindow(m_hwndTarget))
    {
        if (m_debugEnabled)
            CW_DebugLog(m_debugLogPath, "[UpdateChecker] Posting result: available=%d", result->available ? 1 : 0);
        PostMessage(m_hwndTarget, WM_CW_VERSION_RESULT,
                     (WPARAM)(result->available ? 1 : 0),
                     (LPARAM)result);
    }
    else
    {
        if (m_debugEnabled)
            CW_DebugLog(m_debugLogPath, "[UpdateChecker] Target window is not valid; dropping result");
        delete result;
    }
}
