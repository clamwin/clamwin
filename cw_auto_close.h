#pragma once

#include <string>

struct CWAutoClosePolicy
{
    bool enabled;
    bool hasRetCodeFilter;
    int retCodeFilter;

    CWAutoClosePolicy()
        : enabled(false)
        , hasRetCodeFilter(false)
        , retCodeFilter(0)
    {
    }
};

CWAutoClosePolicy CW_AutoCloseDisabled();
CWAutoClosePolicy CW_AutoCloseOnAnyResult();
CWAutoClosePolicy CW_AutoCloseOnExitCode(int exitCode);
CWAutoClosePolicy CW_CliAutoClosePolicy(const std::string& mode, bool closeRequested);
bool CW_ShouldAutoClose(const CWAutoClosePolicy& policy, int exitCode, bool cancelled);