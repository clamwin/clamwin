/*
 * ClamWin Free Antivirus — CWScheduler
 *
 * Timer-based scheduled scanning and database updates.
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

#include "cw_scheduler.h"
#include "cw_gui_shared.h"
#include "cw_log_utils.h"
#include <time.h>
#include <stdio.h>

#define SCHEDULER_TIMER_ID  42
#define SCHEDULER_INTERVAL  60000  /* 60 seconds */

/* ─── Scheduler diagnostic log ─────────────────────────────── */
/* Scheduler logging is now handled by cw_log_utils.cpp: CW_DebugLog */

/* ─── Day mapping ───────────────────────────────────────────── */

static int cfgDayToTmWday(int cfgDay)
{
    /* Config uses 0=Monday..6=Sunday, tm_wday uses 0=Sunday..6=Saturday. */
    if (cfgDay < 0 || cfgDay > 6)
        return -1;
    return (cfgDay + 1) % 7;
}

static const char* frequencyName(int f)
{
    switch (f) {
        case 0: return "Daily";
        case 1: return "Workdays";
        case 2: return "Weekly";
        case 3: return "Hourly";
        default: return "Unknown";
    }
}

/* ─── Construction ──────────────────────────────────────────── */

CWScheduler::CWScheduler()
    : m_hwnd(NULL)
    , m_config(NULL)
    , m_timerId(0)
    , m_debug(false)
{
}

CWScheduler::~CWScheduler()
{
    stop();
}

/* ─── isDue (pure logic, no logging — unit-testable) ─────────── */

int CWScheduler::isDue(time_t now, int scheduled, int hour, int minute, int frequency, int day, bool runMissed, long long& last_run_time)
{
    if (!scheduled) return 0;

    struct tm* tm_ptr = localtime(&now);
    if (!tm_ptr) return 0;
    
    struct tm tm_val = *tm_ptr;
    struct tm* tm = &tm_val;

    time_t last_rt = (time_t)last_run_time;
    struct tm ltm = {0};
    if (last_rt > 0) {
        struct tm* ltm_ptr = localtime(&last_rt);
        if (ltm_ptr) ltm = *ltm_ptr;
    }

    /* Determine current interval identifier to prevent running twice.
     * We only count a previous run as "this interval" if it occurred AT or
     * AFTER the scheduled time — a runMissed catch-up that fired before the
     * scheduled time must not block the real scheduled firing later. */
    bool ran_this_interval = false;
    if (last_rt > 0) {
        bool same_day = (ltm.tm_year == tm->tm_year && ltm.tm_yday == tm->tm_yday);
        if (frequency == 3) {
            /* Hourly: same hour AND last run was at or after the scheduled minute */
            bool same_hour = same_day && (ltm.tm_hour == tm->tm_hour);
            ran_this_interval = same_hour && (ltm.tm_min >= minute);
        } else {
            /* Daily/Workdays/Weekly: same day AND last run was at or after scheduled time */
            bool ran_at_or_after = (ltm.tm_hour > hour ||
                                    (ltm.tm_hour == hour && ltm.tm_min >= minute));
            ran_this_interval = same_day && ran_at_or_after;
        }
    }

    if (ran_this_interval) return 0;

    /* Is today an eligible day? */
    bool eligible_day = false;
    switch (frequency) {
        case 0: /* Daily */     eligible_day = true; break;
        case 1: /* Workdays */  eligible_day = (tm->tm_wday >= 1 && tm->tm_wday <= 5); break;
        case 2: /* Weekly */    eligible_day = (tm->tm_wday == cfgDayToTmWday(day)); break;
        case 3: /* Hourly */    eligible_day = true; break;
    }

    if (!eligible_day) return 0;

    bool time_to_run = false;

    if (frequency == 3) {
        if (tm->tm_min >= minute) time_to_run = true;
    } else {
        if (runMissed) {
            if (tm->tm_hour > hour || (tm->tm_hour == hour && tm->tm_min >= minute))
                time_to_run = true;
        } else {
            if (tm->tm_hour == hour && tm->tm_min >= minute)
                time_to_run = true;
        }
    }

    if (time_to_run) {
        last_run_time = now;
        return 1;
    }

    bool reached_scheduled_time = false;
    if (frequency == 3)
        reached_scheduled_time = (tm->tm_min >= minute);
    else
        reached_scheduled_time = (tm->tm_hour > hour || (tm->tm_hour == hour && tm->tm_min >= minute));

    /* Catch up on missed tasks if computer was off */
    if (runMissed && last_rt > 0)
    {
        int gap = (int)(now - last_rt);
        if (reached_scheduled_time)
        {
            if (frequency == 3 && gap > 5400) time_to_run = true;
            if (frequency == 0 && gap > 129600) time_to_run = true; /* 36h */
            if (frequency == 1 && gap > 302400) time_to_run = true; /* 84h (3.5 days) */
            if (frequency == 2 && gap > 648000) time_to_run = true; /* 7.5 days */
        }
    }

    if (time_to_run) {
        last_run_time = now;
        return 1;
    }

    return 0;
}

/* ─── isDueVerbose (logging wrapper around isDue) ────────────── */

static int isDueVerbose(const std::string& logPath, const char* label,
                        time_t now, int scheduled, int hour, int minute,
                        int frequency, int day, bool runMissed,
                        long long& last_run_time)
{
    CW_DebugLog(logPath, "--- Checking %s schedule ---", label);
    CW_DebugLog(logPath, "  scheduled=%d  frequency=%s(%d)  at=%02d:%02d  day=%d  runMissed=%d",
             scheduled, frequencyName(frequency), frequency, hour, minute, day, (int)runMissed);

    char lastBuf[32] = "never";
    if (last_run_time > 0) {
        time_t lrt = (time_t)last_run_time;
        struct tm ltmBuf = {0};
        struct tm* tmPtr = localtime(&lrt);
        if (tmPtr) {
            ltmBuf = *tmPtr;
            strftime(lastBuf, sizeof(lastBuf), "%Y-%m-%d %H:%M:%S", &ltmBuf);
        }
    }
    CW_DebugLog(logPath, "  lastRunTime=%lld (%s)", last_run_time, lastBuf);

    if (!scheduled) {
        CW_DebugLog(logPath, "  SKIP: not scheduled");
        return 0;
    }

    /* Replicate isDue decision trace */
    struct tm tmNow = {0};
    struct tm* tmPtr = localtime(&now);
    if (tmPtr) tmNow = *tmPtr;
    CW_DebugLog(logPath, "  now: wday=%d  yday=%d  hour=%d  min=%d",
             tmNow.tm_wday, tmNow.tm_yday, tmNow.tm_hour, tmNow.tm_min);

    time_t last_rt = (time_t)last_run_time;
    struct tm ltm = {0};
    if (last_rt > 0) {
        struct tm* lp = localtime(&last_rt);
        if (lp) ltm = *lp;
    }

    bool ran_this_interval = false;
    if (last_rt > 0) {
        bool same_day = (ltm.tm_year == tmNow.tm_year && ltm.tm_yday == tmNow.tm_yday);
        if (frequency == 3) {
            bool same_hour = same_day && (ltm.tm_hour == tmNow.tm_hour);
            ran_this_interval = same_hour && (ltm.tm_min >= minute);
        } else {
            bool ran_at_or_after = (ltm.tm_hour > hour ||
                                    (ltm.tm_hour == hour && ltm.tm_min >= minute));
            ran_this_interval = same_day && ran_at_or_after;
        }
    }

    bool eligible_day = false;
    switch (frequency) {
        case 0: eligible_day = true; break;
        case 1: eligible_day = (tmNow.tm_wday >= 1 && tmNow.tm_wday <= 5); break;
        case 2: eligible_day = (tmNow.tm_wday == cfgDayToTmWday(day)); break;
        case 3: eligible_day = true; break;
    }

    bool time_reached = false;
    if (frequency == 3)
        time_reached = (tmNow.tm_min >= minute);
    else
        time_reached = (tmNow.tm_hour > hour || (tmNow.tm_hour == hour && tmNow.tm_min >= minute));

    int gap = (last_rt > 0) ? (int)(now - last_rt) : -1;

    CW_DebugLog(logPath, "  ran_this_interval=%d  eligible_day=%d  time_reached=%d  gap=%ds",
             (int)ran_this_interval, (int)eligible_day, (int)time_reached, gap);

    int result = CWScheduler::isDue(now, scheduled, hour, minute, frequency, day, runMissed, last_run_time);

    CW_DebugLog(logPath, "  RESULT: %s", result ? "TRIGGER" : "not due");
    return result;
}

/* ─── check ─────────────────────────────────────────────────── */

void CWScheduler::check()
{
    if (!m_config || !m_hwnd) return;

    time_t now = time(NULL);
    bool conf_changed = false;

    std::string logPath = m_debug ? CW_GetDebugLogPath(m_config->scanLogFile) : "";

    if (m_debug)
        CW_DebugLog(logPath, "=== Scheduler check ===");

    int scanDue, updateDue;
    if (m_debug) {
        scanDue   = isDueVerbose(logPath, "Scan",
                         now, m_config->scanScheduled,
                         m_config->scanHour, m_config->scanMinute,
                         m_config->scanFrequency, m_config->scanDay,
                         m_config->scanRunMissed, m_config->scanLastRunTime);
        updateDue = isDueVerbose(logPath, "Update",
                         now, m_config->updateScheduled,
                         m_config->updateHour, m_config->updateMinute,
                         m_config->updateFrequency, 0,
                         m_config->updateRunMissed, m_config->updateLastRunTime);
    } else {
        scanDue   = isDue(now, m_config->scanScheduled,
                         m_config->scanHour, m_config->scanMinute,
                         m_config->scanFrequency, m_config->scanDay,
                         m_config->scanRunMissed, m_config->scanLastRunTime);
        updateDue = isDue(now, m_config->updateScheduled,
                         m_config->updateHour, m_config->updateMinute,
                         m_config->updateFrequency, 0,
                         m_config->updateRunMissed, m_config->updateLastRunTime);
    }

    if (scanDue)
    {
        if (m_debug) CW_DebugLog(logPath, "  => Posting IDM_TRAY_SCHEDULED_SCAN");
        conf_changed = true;
        PostMessage(m_hwnd, WM_COMMAND, IDM_TRAY_SCHEDULED_SCAN, 0);
    }

    if (updateDue)
    {
        if (m_debug) CW_DebugLog(logPath, "  => Posting IDM_TRAY_SCHEDULED_UPDATE");
        conf_changed = true;
        PostMessage(m_hwnd, WM_COMMAND, IDM_TRAY_SCHEDULED_UPDATE, 0);
    }

    if (conf_changed) {
        if (m_debug) CW_DebugLog(logPath, "  => Saving config (lastRunTime updated)");
        m_config->save();
    }
}

/* ─── start / stop ──────────────────────────────────────────── */

void CWScheduler::start(HWND hwnd, CWConfig *cfg)
{
    m_hwnd   = hwnd;
    m_config = cfg;
    m_debug  = cfg->debugEnabled;

    if (m_debug) {
        std::string logPath = CW_GetDebugLogPath(cfg->scanLogFile);
        CW_DebugLog(logPath, "=== Scheduler started (interval=%ds) ===", SCHEDULER_INTERVAL / 1000);
        CW_DebugLog(logPath, "  Scan:   scheduled=%d  freq=%s  at=%02d:%02d  runMissed=%d  lastRun=%lld",
                 cfg->scanScheduled, frequencyName(cfg->scanFrequency),
                 cfg->scanHour, cfg->scanMinute, (int)cfg->scanRunMissed, cfg->scanLastRunTime);
        CW_DebugLog(logPath, "  Update: scheduled=%d  freq=%s  at=%02d:%02d  runMissed=%d  lastRun=%lld",
                 cfg->updateScheduled, frequencyName(cfg->updateFrequency),
                 cfg->updateHour, cfg->updateMinute, (int)cfg->updateRunMissed, cfg->updateLastRunTime);
        CW_DebugLog(logPath, "  ScanPath: [%s]  LogFile: [%s]",
                 cfg->scanPath.c_str(), cfg->scanLogFile.c_str());
        CW_DebugLog(logPath, "  SchedulerLog: [%s]", logPath.c_str());
    }

    m_timerId = SetTimer(hwnd, SCHEDULER_TIMER_ID, SCHEDULER_INTERVAL, NULL);

    /* Do an initial check immediately */
    check();
}

void CWScheduler::stop()
{
    if (m_timerId && m_hwnd)
    {
        if (m_debug && m_config) {
            std::string logPath = CW_GetDebugLogPath(m_config->scanLogFile);
            CW_DebugLog(logPath, "=== Scheduler stopped ===");
        }
        KillTimer(m_hwnd, SCHEDULER_TIMER_ID);
        m_timerId = 0;
    }
    m_hwnd   = NULL;
    m_config = NULL;
    m_debug  = false;
}

/* ─── Global C wrappers for compatibility ───────────────────────── */
static CWScheduler s_globalScheduler;

void CW_SchedulerStart(HWND hwnd, CWConfig *cfg)
{
    s_globalScheduler.start(hwnd, cfg);
}

void CW_SchedulerStop(void)
{
    s_globalScheduler.stop();
}

void CW_SchedulerCheck(void)
{
    s_globalScheduler.check();
}
