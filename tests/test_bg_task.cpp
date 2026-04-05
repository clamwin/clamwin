#include "doctest.h"
#include "cw_bg_task.h"

namespace
{
CWConfig makeBaseConfig()
{
    CWConfig cfg;
    cfg.databasePath = "C:\\db";
    cfg.quarantinePath = "C:\\Quarantine";
    cfg.scanLogFile = "C:\\logs\\scan.log";
    cfg.updateLogFile = "C:\\logs\\update.log";
    cfg.priority = "l";
    return cfg;
}
}

TEST_SUITE("bg_task")
{
    TEST_CASE("scan task builds clamscan command")
    {
        CWConfig cfg = makeBaseConfig();
        CWBgTask task(NULL, cfg, false, "C:\\scan\\target", false);

        std::string cmd = task.buildCommand("C:\\Program Files\\ClamWin\\");

        CHECK(cmd.find("clamscan.exe") != std::string::npos);
        CHECK(cmd.find("C:\\scan\\target") != std::string::npos);
        CHECK(cmd.find("--database=") != std::string::npos);
    }

    TEST_CASE("memory scan task builds clamscan command with --memory flag")
    {
        CWConfig cfg = makeBaseConfig();
        CWBgTask task(NULL, cfg, false, "", true);

        std::string cmd = task.buildCommand("C:\\ClamWin\\");

        CHECK(cmd.find("clamscan.exe") != std::string::npos);
        CHECK(cmd.find("--memory") != std::string::npos);
    }

    TEST_CASE("update task builds freshclam command")
    {
        CWConfig cfg = makeBaseConfig();
        CWBgTask task(NULL, cfg, true, "", false);

        std::string cmd = task.buildCommand("C:\\ClamWin\\");

        CHECK(cmd.find("freshclam.exe") != std::string::npos);
        CHECK(cmd.find("--datadir=") != std::string::npos);
    }

    TEST_CASE("result reflects initial state before start")
    {
        CWConfig cfg = makeBaseConfig();
        CWBgTask task(NULL, cfg, false, "C:\\target", false);

        CWBgResult res = task.result();

        CHECK(res.exitCode == -1);
        CHECK(res.isUpdate == false);
        CHECK(res.threatsFound == 0);
        CHECK(res.updateHadChanges == false);
    }

    TEST_CASE("update result isUpdate flag is set")
    {
        CWConfig cfg = makeBaseConfig();
        CWBgTask task(NULL, cfg, true, "", false);

        CWBgResult res = task.result();

        CHECK(res.isUpdate == true);
    }
}
