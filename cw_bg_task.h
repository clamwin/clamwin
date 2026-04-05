/*
 * ClamWin Free Antivirus — CWBgTask
 *
 * Runs clamscan / freshclam in the background with no UI dialog.
 * Used for timer-fired scheduled scans and updates.
 * On completion, posts WM_CW_BG_FINISHED to the owner window.
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

#pragma once
#include "cwdefs.h"
#include <windows.h>
#include <string>
#include "cw_config.h"
#include "cw_process.h"
#include "cw_scan_logic.h"

struct CWBgResult
{
    int  exitCode;
    bool isUpdate;
    int  threatsFound;
    bool updateHadChanges;
};

class CWBgTask
{
public:
    CWBgTask(HWND hwndOwner, const CWConfig& cfg,
             bool isUpdate, const std::string& targetPath,
             bool scanMemoryOnly = false);
    ~CWBgTask();

    bool start();
    void stop();
    bool isRunning() const;

    CWBgResult result() const;

    /* Exposed for unit tests: build the command without starting */
    std::string buildCommand(const std::string& exeDir) const;

private:
    CWBgTask(const CWBgTask&);
    CWBgTask& operator=(const CWBgTask&);

    static void onOutput(const char* line, void* ud);
    static void onError(const char* line, void* ud);
    static void onFinished(int exitCode, void* ud);

    HWND        m_hwndOwner;
    CWConfig    m_cfg;
    bool        m_isUpdate;
    std::string m_targetPath;
    bool        m_scanMemoryOnly;
    CWProcess   m_process;

    CWScanLogic::ScanOutputState m_outputState;
    int         m_exitCode;
};
