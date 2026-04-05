#include "cw_auto_close.h"

#include <string.h>

CWAutoClosePolicy CW_AutoCloseDisabled()
{
    return CWAutoClosePolicy();
}

CWAutoClosePolicy CW_AutoCloseOnAnyResult()
{
    CWAutoClosePolicy policy;
    policy.enabled = true;
    return policy;
}

CWAutoClosePolicy CW_AutoCloseOnExitCode(int exitCode)
{
    CWAutoClosePolicy policy;
    policy.enabled = true;
    policy.hasRetCodeFilter = true;
    policy.retCodeFilter = exitCode;
    return policy;
}

CWAutoClosePolicy CW_CliAutoClosePolicy(const std::string& mode, bool closeRequested)
{
    if (!closeRequested)
        return CW_AutoCloseDisabled();

    if (_stricmp(mode.c_str(), "scanner") == 0)
        return CW_AutoCloseOnExitCode(0);

    if (_stricmp(mode.c_str(), "update") == 0 ||
        _stricmp(mode.c_str(), "updater") == 0)
    {
        return CW_AutoCloseOnAnyResult();
    }

    return CW_AutoCloseDisabled();
}

bool CW_ShouldAutoClose(const CWAutoClosePolicy& policy, int exitCode, bool cancelled)
{
    if (!policy.enabled)
        return false;

    const int effectiveExitCode = cancelled ? 0 : exitCode;
    return !policy.hasRetCodeFilter || effectiveExitCode == policy.retCodeFilter;
}