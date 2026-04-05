#include "doctest.h"
#include "cw_auto_close.h"

TEST_SUITE("auto_close")
{
    TEST_CASE("disabled policy never closes")
    {
        CWAutoClosePolicy policy = CW_AutoCloseDisabled();

        CHECK_FALSE(CW_ShouldAutoClose(policy, 0, false));
        CHECK_FALSE(CW_ShouldAutoClose(policy, 1, false));
        CHECK_FALSE(CW_ShouldAutoClose(policy, 0, true));
    }

    TEST_CASE("scan success-only policy matches legacy behavior")
    {
        CWAutoClosePolicy policy = CW_AutoCloseOnExitCode(0);

        CHECK(CW_ShouldAutoClose(policy, 0, false));
        CHECK_FALSE(CW_ShouldAutoClose(policy, 1, false));
        CHECK_FALSE(CW_ShouldAutoClose(policy, -1, false));
    }

    TEST_CASE("cancelled run maps to exit code zero for auto-close")
    {
        CWAutoClosePolicy policy = CW_AutoCloseOnExitCode(0);

        CHECK(CW_ShouldAutoClose(policy, -1, true));
    }

    TEST_CASE("update any-result policy closes regardless of return code")
    {
        CWAutoClosePolicy policy = CW_AutoCloseOnAnyResult();

        CHECK(CW_ShouldAutoClose(policy, 0, false));
        CHECK(CW_ShouldAutoClose(policy, 1, false));
        CHECK(CW_ShouldAutoClose(policy, -1, false));
    }
}