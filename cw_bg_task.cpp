/*
 * ClamWin Free Antivirus — CWBgTask implementation
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

#include "cw_bg_task.h"
#include "cw_gui_shared.h"
#include "cw_text_conv.h"

#include <tchar.h>
#include <time.h>

/* ─── helpers ──────────────────────────────────────────────── */

static std::string getExeDir()
{
    TCHAR buf[CW_MAX_PATH];
    GetModuleFileName(NULL, buf, _countof(buf));
    TCHAR* slash = _tcsrchr(buf, TEXT('\\'));
    if (slash) *(slash + 1) = TEXT('\0');
    return CW_ToNarrow(buf);
}

/* Append a line to a log file (matches legacy Python Utils.AppendLogFile
 * pattern).  The Python code wrote "\nScan Started <ctime>" before spawning
 * and "\n------\nCompleted\n------" after the process finished. */
static void appendLineToLogFile(const std::string& filePath,
                                const std::string& line)
{
    if (filePath.empty() || line.empty())
        return;

    std::basic_string<TCHAR> tPath = CW_ToT(filePath);
    HANDLE hFile = CreateFile(tPath.c_str(), FILE_APPEND_DATA,
                              FILE_SHARE_READ | FILE_SHARE_WRITE,
                              NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE)
        return;

    DWORD written = 0;
    WriteFile(hFile, line.c_str(), (DWORD)line.size(), &written, NULL);
    (void)written;
    CloseHandle(hFile);
}

/* Build a "Scan Started <timestamp>" or "Update Started <timestamp>" line
 * matching the legacy Python format: time.ctime(time.time()). */
static std::string buildStartTimestamp(bool isUpdate)
{
    time_t now = time(NULL);
    char timeBuf[64];
    char* ct = ctime(&now);
    if (ct)
    {
        /* ctime() includes trailing '\n' — strip it */
        _snprintf(timeBuf, sizeof(timeBuf), "%s", ct);
        timeBuf[sizeof(timeBuf) - 1] = '\0';
        char* nl = strchr(timeBuf, '\n');
        if (nl) *nl = '\0';
    }
    else
    {
        _snprintf(timeBuf, sizeof(timeBuf), "(unknown)");
    }

    std::string line = "\r\n";
    line += isUpdate ? "Update Started " : "Scan Started ";
    line += timeBuf;
    line += "\r\n";
    return line;
}

static std::string buildCompletedFooter()
{
    return "\r\n--------------------------------------\r\nCompleted\r\n--------------------------------------\r\n";
}

/* ─── construction ─────────────────────────────────────────── */

CWBgTask::CWBgTask(HWND hwndOwner, const CWConfig& cfg,
                   bool isUpdate, const std::string& targetPath,
                   bool scanMemoryOnly)
    : m_hwndOwner(hwndOwner)
    , m_cfg(cfg)
    , m_isUpdate(isUpdate)
    , m_targetPath(targetPath)
    , m_scanMemoryOnly(scanMemoryOnly)
    , m_exitCode(-1)
{
    CWScanLogic::initScanOutputState(m_outputState, isUpdate);
}

CWBgTask::~CWBgTask()
{
    stop();
}

/* ─── public API ───────────────────────────────────────────── */

std::string CWBgTask::buildCommand(const std::string& exeDir) const
{
    if (m_isUpdate)
        return CWScanLogic::buildFreshclamCommand(m_cfg, exeDir);
    else
        return CWScanLogic::buildClamscanCommand(m_cfg, m_targetPath,
                                                 exeDir, m_scanMemoryOnly);
}

bool CWBgTask::start()
{
    std::string exeDir = getExeDir();

    if (m_isUpdate && !CWScanLogic::hasFreshclamExecutable(exeDir))
        return false;

    /* Write "Scan Started" / "Update Started" timestamp to the log file
     * before spawning — matches legacy Python ClamTray.ScanPath() which
     * wrote: file(scanlog, 'wt').write('\nScan Started %s' % time.ctime()) */
    const std::string& logPath = m_isUpdate ? m_cfg.updateLogFile
                                            : m_cfg.scanLogFile;
    appendLineToLogFile(logPath, buildStartTimestamp(m_isUpdate));

    std::string cmd = buildCommand(exeDir);
    return m_process.start(cmd, m_cfg.priority,
                           onOutput, onError, onFinished, this);
}

void CWBgTask::stop()
{
    m_process.stop();
}

bool CWBgTask::isRunning() const
{
    return m_process.isRunning();
}

CWBgResult CWBgTask::result() const
{
    CWBgResult r;
    r.exitCode        = m_exitCode;
    r.isUpdate        = m_isUpdate;
    r.threatsFound    = m_outputState.threatsFound;
    r.updateHadChanges = m_outputState.updateHadChanges;
    return r;
}

/* ─── callbacks (called from CWProcess reader thread) ────── */

void CWBgTask::onOutput(const char* line, void* ud)
{
    CWBgTask* self = static_cast<CWBgTask*>(ud);
    CWScanLogic::processOutputLine(self->m_outputState, line, false);
}

void CWBgTask::onError(const char* line, void* ud)
{
    CWBgTask* self = static_cast<CWBgTask*>(ud);
    CWScanLogic::processOutputLine(self->m_outputState, line, true);
}

void CWBgTask::onFinished(int exitCode, void* ud)
{
    CWBgTask* self = static_cast<CWBgTask*>(ud);
    self->m_exitCode = exitCode;

    /* Write completion footer to log file — matches legacy Python
     * wxDialogStatus.OnThreadFinished() separator lines. */
    const std::string& logPath = self->m_isUpdate ? self->m_cfg.updateLogFile
                                                  : self->m_cfg.scanLogFile;
    appendLineToLogFile(logPath, buildCompletedFooter());

    if (self->m_hwndOwner)
        PostMessage(self->m_hwndOwner, WM_CW_BG_FINISHED,
                    (WPARAM)exitCode, (LPARAM)self);
}
