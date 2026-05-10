/*
 * ClamWin Free Antivirus — CWConfig implementation
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

#include "cw_config.h"
#include "cw_gui_shared.h"   /* for CW_INI_SECTION_* defines */
#include "cw_text_conv.h"

#include <stdio.h>
#include <shlobj.h>
#include <string.h>

/* ─── Section names (same as legacy Python ClamWin) ─────────── */

static const TCHAR* SEC_CLAMAV   = TEXT("ClamAV");
static const TCHAR* SEC_UPDATES  = TEXT("Updates");
static const TCHAR* SEC_PROXY    = TEXT("Proxy");
static const TCHAR* SEC_SCHEDULE = TEXT("Schedule");
static const TCHAR* SEC_ALERTS   = TEXT("EmailAlerts");
static const TCHAR* SEC_UI       = TEXT("UI");

static std::string s_testInstallDirOverride;
static std::string s_testAppDataDirOverride;
static std::string s_testUserProfileDirOverride;
static std::string s_testCommonAppDataDirOverride;
static bool s_hasTestAppDataDirOverride = false;
static bool s_hasTestUserProfileDirOverride = false;
static bool s_hasTestCommonAppDataDirOverride = false;

static std::string normalizeFilterPatterns(const std::string& raw)
{
    if (raw == "*.dbx|CLAMWIN_SEP|bb|CLAMWIN_SEP|st")
        return "*.dbx|CLAMWIN_SEP|*.tbb|CLAMWIN_SEP|*.pst";
    return raw;
}

static std::string stripTrailingSlash(const std::string& path)
{
    if (path.empty())
        return path;

    size_t end = path.size();
    while (end > 0 && (path[end - 1] == '\\' || path[end - 1] == '/'))
        --end;
    return path.substr(0, end);
}

static std::string appendPath(const std::string& left, const std::string& right)
{
    if (left.empty())
        return right;
    if (right.empty())
        return left;

    std::string joined = stripTrailingSlash(left);
    joined += "\\";
    joined += right;
    return joined;
}

static std::string getEnvValue(LPCTSTR name)
{
    TCHAR value[MAX_PATH];
    DWORD len = GetEnvironmentVariable(name, value, MAX_PATH);
    if (len == 0 || len >= MAX_PATH)
        return std::string();
    return CW_ToNarrow(value);
}

static bool getSpecialFolderPathDynamic(int csidl, bool create, TCHAR* out, DWORD outChars)
{
    if (!out || outChars == 0)
        return false;

    out[0] = TEXT('\0');

    /* Resolve shell-folder APIs at runtime: Win98 builds must not carry a
     * hard import on SHGetFolderPath/SHGetSpecialFolderPath. */
    const LPCTSTR folderPathDlls[] = { TEXT("shfolder.dll"), TEXT("shell32.dll") };
    for (size_t i = 0; i < sizeof(folderPathDlls) / sizeof(folderPathDlls[0]); ++i)
    {
        HMODULE module = LoadLibrary(folderPathDlls[i]);
        if (!module)
            continue;

#ifdef UNICODE
        const char* procName = "SHGetFolderPathW";
#else
        const char* procName = "SHGetFolderPathA";
#endif
        typedef HRESULT (WINAPI *SHGetFolderPathFn)(HWND, int, HANDLE, DWORD, LPTSTR);
        SHGetFolderPathFn fn = (SHGetFolderPathFn)GetProcAddress(module, procName);
        if (fn)
        {
            HRESULT hr = fn(NULL, csidl, NULL, SHGFP_TYPE_CURRENT, out);
            out[outChars - 1] = TEXT('\0');
            FreeLibrary(module);
            return SUCCEEDED(hr) && out[0] != TEXT('\0');
        }

        FreeLibrary(module);
    }

    HMODULE shell32 = LoadLibrary(TEXT("shell32.dll"));
    if (shell32)
    {
#ifdef UNICODE
        const char* procName = "SHGetSpecialFolderPathW";
#else
        const char* procName = "SHGetSpecialFolderPathA";
#endif
        typedef BOOL (WINAPI *SHGetSpecialFolderPathFn)(HWND, LPTSTR, int, BOOL);
        SHGetSpecialFolderPathFn fn = (SHGetSpecialFolderPathFn)GetProcAddress(shell32, procName);
        if (fn)
        {
            BOOL ok = fn(NULL, out, csidl, create ? TRUE : FALSE);
            out[outChars - 1] = TEXT('\0');
            FreeLibrary(shell32);
            return ok && out[0] != TEXT('\0');
        }

        FreeLibrary(shell32);
    }

    return false;
}

static std::string getExecutableDir()
{
    if (!s_testInstallDirOverride.empty())
        return s_testInstallDirOverride;

    TCHAR exedir[MAX_PATH];
    GetModuleFileName(NULL, exedir, MAX_PATH);
    TCHAR* slash = _tcsrchr(exedir, TEXT('\\'));
    if (slash)
        *slash = TEXT('\0');
    return CW_ToNarrow(exedir);
}

static std::string getTemplateIniPath()
{
    return appendPath(getExecutableDir(), "ClamWin.conf");
}

static bool pathExists(const std::string& path)
{
    if (path.empty())
        return false;

    std::basic_string<TCHAR> tPath = CW_ToT(path);
    return GetFileAttributes(tPath.c_str()) != INVALID_FILE_ATTRIBUTES;
}

static std::string getParentDir(const std::string& path)
{
    size_t slash = path.find_last_of("\\/");
    if (slash == std::string::npos)
        return std::string();
    return path.substr(0, slash);
}

static bool ensureDirectoryExists(const std::string& path)
{
    if (path.empty())
        return false;

    std::basic_string<TCHAR> tPath = CW_ToT(path);
    if (CreateDirectory(tPath.c_str(), NULL) != 0)
        return true;

    DWORD attrs = GetFileAttributes(tPath.c_str());
    return attrs != INVALID_FILE_ATTRIBUTES && (attrs & FILE_ATTRIBUTE_DIRECTORY) != 0;
}

static bool isStandaloneTemplate(const std::string& path)
{
    if (!pathExists(path))
        return false;

    std::basic_string<TCHAR> tPath = CW_ToT(path);
    return GetPrivateProfileInt(SEC_UI, TEXT("Standalone"), 0, tPath.c_str()) == 1;
}

static bool iniHasKey(const std::string& iniPath, LPCTSTR section, LPCTSTR key)
{
    if (iniPath.empty())
        return false;

    TCHAR sentinel[] = TEXT("\x1");
    TCHAR buffer[4];
    std::basic_string<TCHAR> tIniPath = CW_ToT(iniPath);
    DWORD len = GetPrivateProfileString(section, key, sentinel, buffer, _countof(buffer), tIniPath.c_str());
    return !(len == 1 && buffer[0] == sentinel[0] && buffer[1] == TEXT('\0'));
}

static bool iniHasAnyKey(const std::string& iniPath,
                         const LPCTSTR section,
                         const LPCTSTR* keys,
                         size_t keyCount)
{
    for (size_t i = 0; i < keyCount; ++i)
    {
        if (iniHasKey(iniPath, section, keys[i]))
            return true;
    }
    return false;
}

static std::string normalizePriorityValue(const std::string& value)
{
    if (_stricmp(value.c_str(), "low") == 0)
        return "l";
    if (_stricmp(value.c_str(), "normal") == 0)
        return "n";
    return value;
}

static std::string getLegacyAppDataDir()
{
    if (s_hasTestAppDataDirOverride)
        return s_testAppDataDirOverride;

    TCHAR appData[MAX_PATH];
    if (getSpecialFolderPathDynamic(CSIDL_APPDATA, true, appData, _countof(appData)))
        return stripTrailingSlash(CW_ToNarrow(appData));

    return std::string();
}

static std::string getLegacyUserProfileDir()
{
    if (s_hasTestUserProfileDirOverride)
        return s_testUserProfileDirOverride;

    return stripTrailingSlash(getEnvValue(TEXT("USERPROFILE")));
}

static std::string getLegacyCommonAppDataDir()
{
    if (s_hasTestCommonAppDataDirOverride)
        return s_testCommonAppDataDirOverride;

    TCHAR commonAppData[MAX_PATH];
    if (getSpecialFolderPathDynamic(CSIDL_COMMON_APPDATA, false, commonAppData, _countof(commonAppData)))
        return stripTrailingSlash(CW_ToNarrow(commonAppData));

    return std::string();
}

static std::string getLegacyConfigPath(const std::string& rootDir)
{
    if (rootDir.empty())
        return std::string();

    return appendPath(appendPath(rootDir, ".clamwin"), "ClamWin.conf");
}

static bool readFileContents(const std::string& path, std::string& content)
{
    content.clear();

    FILE* fp = fopen(path.c_str(), "rb");
    if (!fp)
        return false;

    char buffer[512];
    size_t bytesRead = 0;
    while ((bytesRead = fread(buffer, 1, sizeof(buffer), fp)) > 0)
        content.append(buffer, bytesRead);

    bool ok = ferror(fp) == 0;
    fclose(fp);
    return ok;
}

static bool filesMatch(const std::string& leftPath, const std::string& rightPath)
{
    if (!pathExists(leftPath) || !pathExists(rightPath))
        return false;

    std::string leftContent;
    std::string rightContent;
    return readFileContents(leftPath, leftContent) &&
           readFileContents(rightPath, rightContent) &&
           leftContent == rightContent;
}

static std::string getPreferredLegacyIniPath()
{
    std::string userProfileIni = getLegacyConfigPath(getLegacyUserProfileDir());
    std::string commonProfileIni = getLegacyConfigPath(getLegacyCommonAppDataDir());

    if (pathExists(userProfileIni))
        return userProfileIni;
    if (pathExists(commonProfileIni))
        return commonProfileIni;

    return std::string();
}

static bool isPristineBootstrapCopy(const std::string& iniPath)
{
    std::string templatePath = getTemplateIniPath();
    if (iniPath.empty())
        return false;

    if (!templatePath.empty())
    {
        if (_stricmp(iniPath.c_str(), templatePath.c_str()) == 0)
            return false;

        if (filesMatch(iniPath, templatePath))
            return true;
    }

    const LPCTSTR seedClamAvKeys[] = { TEXT("ClamScan"), TEXT("FreshClam") };
    const LPCTSTR seedUpdateKeys[] = { TEXT("Time") };
    bool hasInstallerSeedMarker =
        iniHasAnyKey(iniPath, SEC_CLAMAV, seedClamAvKeys, _countof(seedClamAvKeys)) ||
        iniHasAnyKey(iniPath, SEC_UPDATES, seedUpdateKeys, _countof(seedUpdateKeys));

    if (!hasInstallerSeedMarker)
        return false;

    /* Older C++ installers seeded only tool/path defaults into ClamWin.conf.
     * A config saved by legacy Python or by this C++ runtime contains scan,
     * update, UI, proxy, email, or schedule preference keys. Treat only the
     * sparse installer seed shape as disposable so a real user config is not
     * bypassed just because another legacy config also exists. */
    const LPCTSTR userClamAvKeys[] = {
        TEXT("ScanRecursive"), TEXT("ScanArchives"), TEXT("ScanOle2"), TEXT("ScanMail"),
        TEXT("EnableMbox"), TEXT("InfectedAction"), TEXT("InfectedOnly"), TEXT("RemoveInfected"),
        TEXT("MoveInfected"), TEXT("MaxScanSize"), TEXT("MaxFileSize"), TEXT("MaxFiles"),
        TEXT("MaxRecursion"), TEXT("Priority"), TEXT("IncludePatterns"), TEXT("ExcludePatterns"),
        TEXT("ClamScanParams"), TEXT("FreshClamParams"), TEXT("Kill"), TEXT("Debug")
    };
    const LPCTSTR userUpdateKeys[] = {
        TEXT("Enable"), TEXT("Frequency"), TEXT("DBMirror"), TEXT("UpdateOnStartup"),
        TEXT("UpdateOnLogon"), TEXT("WarnOutOfDate"), TEXT("CheckVersion"), TEXT("CheckVersionURL")
    };
    const LPCTSTR userProxyKeys[] = { TEXT("Enabled"), TEXT("Host"), TEXT("User"), TEXT("Password") };
    const LPCTSTR userAlertKeys[] = { TEXT("Enabled"), TEXT("Enable"), TEXT("SMTP"), TEXT("SMTPHost"), TEXT("From"), TEXT("To") };
    const LPCTSTR userScheduleKeys[] = { TEXT("Path"), TEXT("ScanEnabled"), TEXT("UpdateEnabled"), TEXT("ScanHour"), TEXT("UpdateHour") };
    const LPCTSTR userUiKeys[] = { TEXT("TrayNotify"), TEXT("CloseOnExit"), TEXT("ReportInfected"), TEXT("Version") };

    return !iniHasAnyKey(iniPath, SEC_CLAMAV, userClamAvKeys, _countof(userClamAvKeys)) &&
           !iniHasAnyKey(iniPath, SEC_UPDATES, userUpdateKeys, _countof(userUpdateKeys)) &&
           !iniHasAnyKey(iniPath, SEC_PROXY, userProxyKeys, _countof(userProxyKeys)) &&
           !iniHasAnyKey(iniPath, SEC_ALERTS, userAlertKeys, _countof(userAlertKeys)) &&
           !iniHasAnyKey(iniPath, SEC_SCHEDULE, userScheduleKeys, _countof(userScheduleKeys)) &&
           !iniHasAnyKey(iniPath, SEC_UI, userUiKeys, _countof(userUiKeys));
}

static std::string getLegacyProfileRoot()
{
    if (isStandaloneTemplate(getTemplateIniPath()))
        return getExecutableDir();

    std::string appData = getLegacyAppDataDir();
    if (!appData.empty())
        return appendPath(appData, ".clamwin");

    std::string profile = getLegacyUserProfileDir();
    if (!profile.empty())
        return appendPath(profile, ".clamwin");

    return getExecutableDir();
}

static std::string resolveDefaultIniPathForLoad()
{
    std::string defaultPath = appendPath(getLegacyProfileRoot(), "ClamWin.conf");
    if (isStandaloneTemplate(getTemplateIniPath()))
        return defaultPath;

    std::string legacyPath = getPreferredLegacyIniPath();
    if (pathExists(defaultPath))
    {
        if (!legacyPath.empty() && isPristineBootstrapCopy(defaultPath))
            return legacyPath;
        return defaultPath;
    }

    if (!legacyPath.empty())
        return legacyPath;

    return defaultPath;
}

static void bootstrapLegacyProfile(const std::string& iniPath)
{
    if (iniPath.empty())
        return;

    std::string templatePath = getTemplateIniPath();
    if (templatePath.empty() || !pathExists(templatePath) || isStandaloneTemplate(templatePath))
        return;

    if (_stricmp(stripTrailingSlash(templatePath).c_str(), stripTrailingSlash(iniPath).c_str()) == 0)
        return;

    if (pathExists(iniPath))
        return;

    std::string profileDir = getParentDir(iniPath);
    if (!ensureDirectoryExists(profileDir))
        return;

    std::basic_string<TCHAR> tSource = CW_ToT(templatePath);
    std::basic_string<TCHAR> tDest = CW_ToT(iniPath);
    CopyFile(tSource.c_str(), tDest.c_str(), TRUE);
}

/* ─── Constructor: apply defaults ────────────────────────────── */

CWConfig::CWConfig()
{
    defaults();
}

/* ─── Defaults ──────────────────────────────────────────────── */

void CWConfig::defaults()
{
    std::string profileRoot = getLegacyProfileRoot();
    if (!profileRoot.empty())
    {
        databasePath   = appendPath(profileRoot, "db");
        quarantinePath = appendPath(profileRoot, "Quarantine");
        scanLogFile    = appendPath(profileRoot, "ClamScan.log");
        updateLogFile  = appendPath(profileRoot, "FreshClam.log");
    }
    else
    {
        std::string exedirStr = getExecutableDir();
        databasePath   = appendPath(exedirStr, "db");
        quarantinePath = appendPath(exedirStr, "Quarantine");
        scanLogFile    = appendPath(exedirStr, "ClamScan.log");
        updateLogFile  = appendPath(exedirStr, "FreshClam.log");
    }

    iniPath         = defaultIniPath();

    scanRecursive   = true;
    scanArchives    = true;
    scanOle2        = true;
    scanMail        = false;
    infectedAction  = 0;
    infectedOnly    = false;
    maxScanSizeMb   = 150;
    maxFileSizeMb   = 100;
    maxFiles        = 500;
    maxDepth        = 50;

    dbMirror        = "database.clamav.net";
    updateOnStartup = false;
    checkVersion    = true;

    proxyEnabled    = false;
    proxyHost       = "";
    proxyPort       = 3128;
    proxyUser       = "";
    proxyPass       = "";

    emailEnabled    = false;
    emailFrom = emailTo = emailSmtp = "";

    scanScheduled   = false;
    scanHour        = 22;
    scanMinute      = 0;
    scanFrequency   = 0;
    scanDay         = 0;
    scanPath        = "";
    scanDescription = "";
    scanMemory      = false;
    scanRunMissed   = true;
    scanLastRunTime = 0;
    updateScheduled = true;
    updateHour      = 4;
    updateMinute    = 0;
    updateFrequency = 0;
    updateRunMissed = true;
    updateLastRunTime = 0;
    debugEnabled  = false;

    closeOnExit     = false;
    trayNotify      = true;
    priority        = "n";

    includePatterns = "";
    excludePatterns = "*.dbx|CLAMWIN_SEP|*.tbb|CLAMWIN_SEP|*.pst";
}

/* ─── Default INI path ──────────────────────────────────────── */

std::string CWConfig::defaultIniPath()
{
    return appendPath(getLegacyProfileRoot(), "ClamWin.conf");
}

void CWConfig::setPathOverridesForTesting(const std::string& installDir,
                                          const std::string& appDataDir,
                                          const std::string& userProfileDir,
                                          const std::string& commonAppDataDir)
{
    s_testInstallDirOverride = stripTrailingSlash(installDir);
    s_testAppDataDirOverride = stripTrailingSlash(appDataDir);
    s_testUserProfileDirOverride = stripTrailingSlash(userProfileDir);
    s_testCommonAppDataDirOverride = stripTrailingSlash(commonAppDataDir);
    s_hasTestAppDataDirOverride = true;
    s_hasTestUserProfileDirOverride = true;
    s_hasTestCommonAppDataDirOverride = true;
}

void CWConfig::clearPathOverridesForTesting()
{
    s_testInstallDirOverride.clear();
    s_testAppDataDirOverride.clear();
    s_testUserProfileDirOverride.clear();
    s_testCommonAppDataDirOverride.clear();
    s_hasTestAppDataDirOverride = false;
    s_hasTestUserProfileDirOverride = false;
    s_hasTestCommonAppDataDirOverride = false;
}

/* ─── freshclam.conf path ────────────────────────────────────── */

std::string CWConfig::freshclamConfPath() const
{
    /* Same directory as iniPath, but with filename freshclam.conf */
    size_t slash = iniPath.rfind('\\');
    if (slash != std::string::npos)
        return iniPath.substr(0, slash + 1) + "freshclam.conf";
    return "freshclam.conf";
}

/* ─── Write freshclam.conf ───────────────────────────────────── */

bool CWConfig::writeFreshclamConf() const
{
    std::string path = freshclamConfPath();

    /* Ensure the parent directory exists */
    std::string dir = path;
    size_t slash = dir.rfind('\\');
    if (slash != std::string::npos)
    {
        dir.resize(slash);
        std::basic_string<TCHAR> tDir = CW_ToT(dir);
        CreateDirectory(tDir.c_str(), NULL);
    }

    FILE* f = fopen(path.c_str(), "w");
    if (!f)
        return false;

    fprintf(f, "# freshclam.conf — generated by ClamWin\n");
    fprintf(f, "# Do not edit: overwritten when preferences are saved.\n\n");

    /* Mirror */
    fprintf(f, "DatabaseMirror %s\n",
            dbMirror.empty() ? "database.clamav.net" : dbMirror.c_str());

    /* Database directory */
    if (!databasePath.empty())
        fprintf(f, "DatabaseDirectory %s\n", databasePath.c_str());

    /* Update log */
    if (!updateLogFile.empty())
        fprintf(f, "UpdateLogFile %s\n", updateLogFile.c_str());

    /* Proxy */
    if (proxyEnabled && !proxyHost.empty())
    {
        fprintf(f, "HTTPProxyServer %s\n", proxyHost.c_str());
        fprintf(f, "HTTPProxyPort %d\n",   proxyPort);
        if (!proxyUser.empty())
            fprintf(f, "HTTPProxyUsername %s\n", proxyUser.c_str());
        if (!proxyPass.empty())
            fprintf(f, "HTTPProxyPassword %s\n", proxyPass.c_str());
    }

    fclose(f);
    return true;
}

/* ─── Load ──────────────────────────────────────────────────── */

bool CWConfig::load(const std::string& path)
{
    defaults();
    bool usingDefaultPath = path.empty();

    if (!path.empty())
        iniPath = path;

    if (usingDefaultPath)
        iniPath = resolveDefaultIniPathForLoad();

    std::string loadedProfileRoot = getParentDir(iniPath);
    if (!loadedProfileRoot.empty())
    {
        databasePath   = appendPath(loadedProfileRoot, "db");
        quarantinePath = appendPath(loadedProfileRoot, "Quarantine");
        scanLogFile    = appendPath(loadedProfileRoot, "ClamScan.log");
        updateLogFile  = appendPath(loadedProfileRoot, "FreshClam.log");
    }

    if (usingDefaultPath)
        bootstrapLegacyProfile(iniPath);

    {
        std::basic_string<TCHAR> tIniPath = CW_ToT(iniPath);
        if (GetFileAttributes(tIniPath.c_str()) == INVALID_FILE_ATTRIBUTES)
        {
            /* Keep freshclam.conf in sync with the default/profile config path
             * even when ClamWin.conf does not exist yet. */
            writeFreshclamConf();
            return false;  /* no file — defaults already applied */
        }
    }

    databasePath   = getStr(SEC_CLAMAV, TEXT("Database"),      databasePath);
    scanRecursive  = getInt(SEC_CLAMAV, TEXT("ScanRecursive"), scanRecursive) != 0;
    scanArchives   = getInt(SEC_CLAMAV, TEXT("ScanArchives"),  scanArchives)  != 0;
    scanOle2       = getInt(SEC_CLAMAV, TEXT("ScanOle2"),      scanOle2)      != 0;
    scanMail       = getInt(SEC_CLAMAV, TEXT("ScanMail"),      scanMail)      != 0;
    if (!iniHasKey(iniPath, SEC_CLAMAV, TEXT("ScanMail")))
        scanMail = getInt(SEC_CLAMAV, TEXT("EnableMbox"), scanMail ? 1 : 0) != 0;
    infectedAction = getInt(SEC_CLAMAV, TEXT("InfectedAction"), infectedAction);
    infectedOnly   = getInt(SEC_CLAMAV, TEXT("InfectedOnly"),   infectedOnly)   != 0;
    maxScanSizeMb  = getInt(SEC_CLAMAV, TEXT("MaxScanSize"),   maxScanSizeMb);
    maxFileSizeMb  = getInt(SEC_CLAMAV, TEXT("MaxFileSize"),   maxFileSizeMb);
    maxFiles       = getInt(SEC_CLAMAV, TEXT("MaxFiles"),      maxFiles);
    maxDepth       = getInt(SEC_CLAMAV, TEXT("MaxRecursion"),  maxDepth);
    quarantinePath = getStr(SEC_CLAMAV, TEXT("Quarantine"),    quarantinePath);
    if (!iniHasKey(iniPath, SEC_CLAMAV, TEXT("Quarantine")))
        quarantinePath = getStr(SEC_CLAMAV, TEXT("QuarantineDir"), quarantinePath);
    scanLogFile    = getStr(SEC_CLAMAV, TEXT("LogFile"),       scanLogFile);
    priority       = normalizePriorityValue(getStr(SEC_CLAMAV, TEXT("Priority"), priority));

    dbMirror        = getStr(SEC_UPDATES, TEXT("DBMirror"),        dbMirror);
    updateLogFile   = getStr(SEC_UPDATES, TEXT("UpdateLog"),       updateLogFile);
    if (!iniHasKey(iniPath, SEC_UPDATES, TEXT("UpdateLog")))
        updateLogFile = getStr(SEC_UPDATES, TEXT("DBUpdateLogFile"), updateLogFile);
    updateOnStartup = getInt(SEC_UPDATES, TEXT("UpdateOnStartup"), updateOnStartup) != 0;
    if (!iniHasKey(iniPath, SEC_UPDATES, TEXT("UpdateOnStartup")))
        updateOnStartup = getInt(SEC_UPDATES, TEXT("UpdateOnLogon"), updateOnStartup ? 1 : 0) != 0;
    checkVersion    = getInt(SEC_UPDATES, TEXT("CheckVersion"),    checkVersion)    != 0;

    proxyHost    = getStr(SEC_PROXY, TEXT("Host"),     proxyHost);
    proxyPort    = getInt(SEC_PROXY, TEXT("Port"),     proxyPort);
    proxyUser    = getStr(SEC_PROXY, TEXT("User"),     proxyUser);
    proxyPass    = getStr(SEC_PROXY, TEXT("Password"), proxyPass);
    if (iniHasKey(iniPath, SEC_PROXY, TEXT("Enabled")))
        proxyEnabled = getInt(SEC_PROXY, TEXT("Enabled"), proxyEnabled ? 1 : 0) != 0;
    else
        proxyEnabled = !proxyHost.empty();

    if (iniHasKey(iniPath, SEC_ALERTS, TEXT("Enabled")))
        emailEnabled = getInt(SEC_ALERTS, TEXT("Enabled"), emailEnabled ? 1 : 0) != 0;
    else
        emailEnabled = getInt(SEC_ALERTS, TEXT("Enable"), emailEnabled ? 1 : 0) != 0;
    emailFrom    = getStr(SEC_ALERTS, TEXT("From"),    emailFrom);
    emailTo      = getStr(SEC_ALERTS, TEXT("To"),      emailTo);
    emailSmtp    = getStr(SEC_ALERTS, TEXT("SMTP"),    emailSmtp);
    if (!iniHasKey(iniPath, SEC_ALERTS, TEXT("SMTP")))
        emailSmtp = getStr(SEC_ALERTS, TEXT("SMTPHost"), emailSmtp);

    scanScheduled   = getInt(SEC_SCHEDULE, TEXT("ScanEnabled"),    scanScheduled)   != 0;
    scanHour        = getInt(SEC_SCHEDULE, TEXT("ScanHour"),       scanHour);
    scanMinute      = getInt(SEC_SCHEDULE, TEXT("ScanMinute"),     scanMinute);
    scanFrequency   = getInt(SEC_SCHEDULE, TEXT("ScanFrequency"),  scanFrequency);
    scanDay         = getInt(SEC_SCHEDULE, TEXT("ScanDay"),        scanDay);
    scanPath        = getStr(SEC_SCHEDULE, TEXT("ScanPath"),        scanPath);
    scanDescription = getStr(SEC_SCHEDULE, TEXT("ScanDescription"), scanDescription);
    scanMemory      = getInt(SEC_SCHEDULE, TEXT("ScanMemory"),      scanMemory) != 0;
    scanRunMissed   = getInt(SEC_SCHEDULE, TEXT("RunMissed"),       scanRunMissed) != 0;
    scanLastRunTime = getInt64(SEC_SCHEDULE, TEXT("ScanLastRun"),   scanLastRunTime);
    updateScheduled = getInt(SEC_SCHEDULE, TEXT("UpdateEnabled"),  updateScheduled) != 0;
    updateHour      = getInt(SEC_SCHEDULE, TEXT("UpdateHour"),     updateHour);
    updateMinute    = getInt(SEC_SCHEDULE, TEXT("UpdateMinute"),   updateMinute);
    updateFrequency = getInt(SEC_SCHEDULE, TEXT("UpdateFrequency"),updateFrequency);
    updateRunMissed = getInt(SEC_SCHEDULE, TEXT("UpdateRunMissed"),updateRunMissed) != 0;
    updateLastRunTime = getInt64(SEC_SCHEDULE, TEXT("UpdateLastRun"),updateLastRunTime);
    /* Debug logging is typically under UI, but fall back to old SchedulerDebug */
    debugEnabled = getInt(SEC_UI, TEXT("Debug"), -1) != -1
                 ? (getInt(SEC_UI, TEXT("Debug"), 0) != 0)
                 : (getInt(SEC_SCHEDULE, TEXT("SchedulerDebug"), 0) != 0);

    closeOnExit     = getInt(SEC_UI, TEXT("CloseOnExit"), closeOnExit)  != 0;
    trayNotify      = getInt(SEC_UI, TEXT("TrayNotify"),  trayNotify)   != 0;

    /* Preserve backward compatibility with INI files that contain empty log path values. */
    if (scanLogFile.empty())
    {
        TCHAR exedir[MAX_PATH];
        GetModuleFileName(NULL, exedir, MAX_PATH);
        TCHAR* slash = _tcsrchr(exedir, TEXT('\\'));
        if (slash)
            *(slash + 1) = '\0';
        scanLogFile = CW_ToNarrow(exedir) + "ClamScan.log";
    }
    if (updateLogFile.empty())
    {
        TCHAR exedir[MAX_PATH];
        GetModuleFileName(NULL, exedir, MAX_PATH);
        TCHAR* slash = _tcsrchr(exedir, TEXT('\\'));
        if (slash)
            *(slash + 1) = '\0';
        updateLogFile = CW_ToNarrow(exedir) + "FreshClam.log";
    }

    /* Migrate legacy install-dir defaults to user profile paths.
     * This avoids update failures when ClamWin is installed under Program Files. */
    {
        TCHAR exedir[MAX_PATH];
        GetModuleFileName(NULL, exedir, MAX_PATH);
        TCHAR* slash = _tcsrchr(exedir, TEXT('\\'));
        if (slash)
            *(slash + 1) = '\0';

        std::string exedirStr = CW_ToNarrow(exedir);
        std::string installDb         = exedirStr + "db";
        std::string installQuarantine = exedirStr + "Quarantine";
        std::string installScanLog    = exedirStr + "ClamScan.log";
        std::string installUpdateLog  = exedirStr + "FreshClam.log";

        std::string profileRoot = !loadedProfileRoot.empty()
            ? loadedProfileRoot
            : getLegacyProfileRoot();
        if (!profileRoot.empty())
        {
            if (databasePath == installDb)
                databasePath = profileRoot + "\\db";
            if (quarantinePath == installQuarantine)
                quarantinePath = profileRoot + "\\Quarantine";
            if (scanLogFile == installScanLog)
                scanLogFile = profileRoot + "\\ClamScan.log";
            if (updateLogFile == installUpdateLog)
                updateLogFile = profileRoot + "\\FreshClam.log";
        }
    }

    includePatterns = getStr(SEC_CLAMAV, TEXT("IncludePatterns"), includePatterns);
    excludePatterns = getStr(SEC_CLAMAV, TEXT("ExcludePatterns"), excludePatterns);
    includePatterns = normalizeFilterPatterns(includePatterns);
    excludePatterns = normalizeFilterPatterns(excludePatterns);

    writeFreshclamConf();

    return true;
}

/* ─── Save ──────────────────────────────────────────────────── */

bool CWConfig::save() const
{
    /* Create directory if needed */
    std::string dir = iniPath;
    size_t slash = dir.rfind('\\');
    if (slash != std::string::npos)
    {
        dir.resize(slash);
        std::basic_string<TCHAR> tDir = CW_ToT(dir);
        CreateDirectory(tDir.c_str(), NULL);
    }

    setStr(SEC_CLAMAV, TEXT("Database"),       databasePath);
    setInt(SEC_CLAMAV, TEXT("ScanRecursive"),  scanRecursive  ? 1 : 0);
    setInt(SEC_CLAMAV, TEXT("ScanArchives"),   scanArchives   ? 1 : 0);
    setInt(SEC_CLAMAV, TEXT("ScanOle2"),       scanOle2       ? 1 : 0);
    setInt(SEC_CLAMAV, TEXT("ScanMail"),       scanMail       ? 1 : 0);
    setInt(SEC_CLAMAV, TEXT("InfectedAction"), infectedAction);
    setInt(SEC_CLAMAV, TEXT("InfectedOnly"),   infectedOnly   ? 1 : 0);
    setInt(SEC_CLAMAV, TEXT("MaxScanSize"),    maxScanSizeMb);
    setInt(SEC_CLAMAV, TEXT("MaxFileSize"),    maxFileSizeMb);
    setInt(SEC_CLAMAV, TEXT("MaxFiles"),       maxFiles);
    setInt(SEC_CLAMAV, TEXT("MaxRecursion"),   maxDepth);
    setStr(SEC_CLAMAV, TEXT("Quarantine"),     quarantinePath);
    setStr(SEC_CLAMAV, TEXT("LogFile"),        scanLogFile);
    setStr(SEC_CLAMAV, TEXT("Priority"),       priority);

    setStr(SEC_UPDATES, TEXT("DBMirror"),         dbMirror);
    setStr(SEC_UPDATES, TEXT("UpdateLog"),        updateLogFile);
    setInt(SEC_UPDATES, TEXT("UpdateOnStartup"),  updateOnStartup ? 1 : 0);
    setInt(SEC_UPDATES, TEXT("CheckVersion"),     checkVersion    ? 1 : 0);

    setInt(SEC_PROXY, TEXT("Enabled"),  proxyEnabled ? 1 : 0);
    setStr(SEC_PROXY, TEXT("Host"),     proxyHost);
    setInt(SEC_PROXY, TEXT("Port"),     proxyPort);
    setStr(SEC_PROXY, TEXT("User"),     proxyUser);
    setStr(SEC_PROXY, TEXT("Password"), proxyPass);

    setInt(SEC_ALERTS, TEXT("Enabled"), emailEnabled ? 1 : 0);
    setStr(SEC_ALERTS, TEXT("From"),    emailFrom);
    setStr(SEC_ALERTS, TEXT("To"),      emailTo);
    setStr(SEC_ALERTS, TEXT("SMTP"),    emailSmtp);

    setInt(SEC_SCHEDULE, TEXT("ScanEnabled"),    scanScheduled   ? 1 : 0);
    setInt(SEC_SCHEDULE, TEXT("ScanHour"),       scanHour);
    setInt(SEC_SCHEDULE, TEXT("ScanMinute"),     scanMinute);
    setInt(SEC_SCHEDULE, TEXT("ScanFrequency"),  scanFrequency);
    setInt(SEC_SCHEDULE, TEXT("ScanDay"),        scanDay);
    setStr(SEC_SCHEDULE, TEXT("ScanPath"),        scanPath);
    setStr(SEC_SCHEDULE, TEXT("ScanDescription"), scanDescription);
    setInt(SEC_SCHEDULE, TEXT("ScanMemory"),      scanMemory ? 1 : 0);
    setInt(SEC_SCHEDULE, TEXT("RunMissed"),       scanRunMissed ? 1 : 0);
    setInt64(SEC_SCHEDULE, TEXT("ScanLastRun"),   scanLastRunTime);
    setInt(SEC_SCHEDULE, TEXT("UpdateEnabled"),  updateScheduled ? 1 : 0);
    setInt(SEC_SCHEDULE, TEXT("UpdateHour"),     updateHour);
    setInt(SEC_SCHEDULE, TEXT("UpdateMinute"),   updateMinute);
    setInt(SEC_SCHEDULE, TEXT("UpdateFrequency"),updateFrequency);
    setInt(SEC_SCHEDULE, TEXT("UpdateRunMissed"),updateRunMissed ? 1 : 0);
    setInt64(SEC_SCHEDULE, TEXT("UpdateLastRun"),updateLastRunTime);
    setInt(SEC_UI, TEXT("Debug"), debugEnabled ? 1 : 0);

    setInt(SEC_UI, TEXT("CloseOnExit"), closeOnExit ? 1 : 0);
    setInt(SEC_UI, TEXT("TrayNotify"),  trayNotify  ? 1 : 0);
    setStr(SEC_CLAMAV, TEXT("IncludePatterns"), includePatterns);
    setStr(SEC_CLAMAV, TEXT("ExcludePatterns"), excludePatterns);

    writeFreshclamConf();

    return true;
}

/* ─── Private helpers ────────────────────────────────────────── */

std::string CWConfig::getStr(LPCTSTR sec, LPCTSTR key,
                              const std::string& def) const
{
    TCHAR buf[1024];
    std::basic_string<TCHAR> tDef = CW_ToT(def);
    std::basic_string<TCHAR> tIniPath = CW_ToT(iniPath);
    GetPrivateProfileString(sec, key, tDef.c_str(),
                              buf, _countof(buf), tIniPath.c_str());
    return CW_ToNarrow(buf);
}

int CWConfig::getInt(LPCTSTR sec, LPCTSTR key, int def) const
{
    std::basic_string<TCHAR> tIniPath = CW_ToT(iniPath);
    return GetPrivateProfileInt(sec, key, def, tIniPath.c_str());
}

void CWConfig::setStr(LPCTSTR sec, LPCTSTR key,
                       const std::string& val) const
{
    std::basic_string<TCHAR> tVal = CW_ToT(val);
    std::basic_string<TCHAR> tIniPath = CW_ToT(iniPath);
    WritePrivateProfileString(sec, key, tVal.c_str(), tIniPath.c_str());
}

void CWConfig::setInt(LPCTSTR sec, LPCTSTR key, int val) const
{
    TCHAR buf[32];
    wsprintf(buf, TEXT("%d"), val);
    std::basic_string<TCHAR> tIniPath = CW_ToT(iniPath);
    WritePrivateProfileString(sec, key, buf, tIniPath.c_str());
}

long long CWConfig::getInt64(LPCTSTR sec, LPCTSTR key, long long def) const
{
    std::string valStr = getStr(sec, key, "");
    if (valStr.empty()) return def;
    return _atoi64(valStr.c_str());
}

void CWConfig::setInt64(LPCTSTR sec, LPCTSTR key, long long val) const
{
    TCHAR buf[64];
    _sntprintf(buf, _countof(buf), TEXT("%I64d"), val);
    buf[_countof(buf) - 1] = TEXT('\0');
    std::basic_string<TCHAR> tIniPath = CW_ToT(iniPath);
    WritePrivateProfileString(sec, key, buf, tIniPath.c_str());
}
