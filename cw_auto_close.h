#pragma once

#include <string>

struct CWAutoClosePolicy
{
    bool enabled;
    bool allowCancelled;
    bool hasRetCodeFilter;
    int retCodeFilter;
    bool hasAltRetCodeFilter;
    int altRetCodeFilter;

    CWAutoClosePolicy()
        : enabled(false)
        , allowCancelled(false)
        , hasRetCodeFilter(false)
        , retCodeFilter(0)
        , hasAltRetCodeFilter(false)
        , altRetCodeFilter(0)
    {
    }
};

CWAutoClosePolicy CW_AutoCloseDisabled();
CWAutoClosePolicy CW_AutoCloseOnAnyResult();
CWAutoClosePolicy CW_AutoCloseOnExitCode(int exitCode);
CWAutoClosePolicy CW_AutoCloseOnExitCodes(int exitCode, int altExitCode);
CWAutoClosePolicy CW_CliAutoClosePolicy(const std::string& mode, bool closeRequested);
bool CW_ShouldAutoClose(const CWAutoClosePolicy& policy, int exitCode, bool cancelled);