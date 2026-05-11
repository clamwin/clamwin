#include "doctest.h"
#include "cw_log_utils.h"
#include "test_support.h"

TEST_SUITE("log_utils")
{
    TEST_CASE("append trims log file to configured max bytes")
    {
        TestTempDir tempDir;
        std::string logPath = testJoinPath(tempDir.path, "scan.log");

        REQUIRE(testWriteFile(logPath, "1234567890"));

        CW_AppendToLogFile(logPath, "ABCDE", 8);

        std::string content;
        REQUIRE(testReadFile(logPath, content));
        CHECK(content == "890ABCDE");
    }

    TEST_CASE("append without cap preserves full log")
    {
        TestTempDir tempDir;
        std::string logPath = testJoinPath(tempDir.path, "scan.log");

        REQUIRE(testWriteFile(logPath, "1234"));

        CW_AppendToLogFile(logPath, "5678");

        std::string content;
        REQUIRE(testReadFile(logPath, content));
        CHECK(content == "12345678");
    }
}