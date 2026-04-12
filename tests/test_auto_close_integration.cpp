#include "doctest.h"
#include "cw_auto_close.h"
#include "cw_cli_args.h"

TEST_SUITE("auto_close_integration")
{
    TEST_CASE("scanner close switch maps to success-only autoclose policy")
    {
        CWCliArgs args;
        CW_ParseCommandLineArgs("--mode=scanner --path=C:\\scan --close", args);

        CWAutoClosePolicy policy = CW_CliAutoClosePolicy(args.mode, args.close);

        CHECK(policy.enabled);
        CHECK(policy.hasRetCodeFilter);
        CHECK(policy.retCodeFilter == 0);
    }

    TEST_CASE("update close switch maps to success-only autoclose policy")
    {
        CWCliArgs args;
        CW_ParseCommandLineArgs("--mode=update --close", args);

        CWAutoClosePolicy policy = CW_CliAutoClosePolicy(args.mode, args.close);

        CHECK(policy.enabled);
        CHECK(policy.hasRetCodeFilter);
        CHECK(policy.retCodeFilter == 0);
        CHECK(policy.hasAltRetCodeFilter);
        CHECK(policy.altRetCodeFilter == 2);
        CHECK_FALSE(policy.allowCancelled);
    }
}