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

/* ─── helpers ──────────────────────────────────────────────── */

static std::string getExeDir()
{
    TCHAR buf[CW_MAX_PATH];
    GetModuleFileName(NULL, buf, _countof(buf));
    TCHAR* slash = _tcsrchr(buf, TEXT('\\'));
    if (slash) *(slash + 1) = TEXT('\0');
    return CW_ToNarrow(buf);
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

    if (self->m_hwndOwner)
        PostMessage(self->m_hwndOwner, WM_CW_BG_FINISHED,
                    (WPARAM)exitCode, (LPARAM)self);
}
