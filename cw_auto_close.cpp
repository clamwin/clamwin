#include "cw_auto_close.h"

#include "cw_gui_shared.h"

#include <string.h>

CWAutoClosePolicy CW_AutoCloseDisabled()
{
    return CWAutoClosePolicy();
}

CWAutoClosePolicy CW_AutoCloseOnAnyResult()
{
    CWAutoClosePolicy policy;
    policy.enabled = true;
    policy.allowCancelled = true;
    return policy;
}

CWAutoClosePolicy CW_AutoCloseOnExitCode(int exitCode)
{
    CWAutoClosePolicy policy;
    policy.enabled = true;
    policy.allowCancelled = true;
    policy.hasRetCodeFilter = true;
    policy.retCodeFilter = exitCode;
    return policy;
}

CWAutoClosePolicy CW_AutoCloseOnExitCodes(int exitCode, int altExitCode)
{
    CWAutoClosePolicy policy;
    policy.enabled = true;
    policy.hasRetCodeFilter = true;
    policy.retCodeFilter = exitCode;
    policy.hasAltRetCodeFilter = true;
    policy.altRetCodeFilter = altExitCode;
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
        return CW_AutoCloseOnExitCodes(0, CW_UPDATE_RC_NO_CHANGES);
    }

    return CW_AutoCloseDisabled();
}

bool CW_ShouldAutoClose(const CWAutoClosePolicy& policy, int exitCode, bool cancelled)
{
    if (!policy.enabled)
        return false;

    if (cancelled)
        return policy.allowCancelled;

    if (!policy.hasRetCodeFilter)
        return true;

    if (exitCode == policy.retCodeFilter)
        return true;

    return policy.hasAltRetCodeFilter && exitCode == policy.altRetCodeFilter;
}