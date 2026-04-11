/*
 * cw_xpcompat.c — XP-compatible shims for Vista+ kernel32 APIs
 *
 * libcurl (compiled with _WIN32_WINNT >= 0x0600) references SRW lock and
 * condition variable functions that exist in kernel32.dll only on Vista+.
 * Windows XP's kernel32.dll has the DLL but not these exports, producing
 * "Entry Point Not Found" at process startup before main() runs.
 *
 * This file provides our own definitions for each affected symbol.  At the
 * first call we probe kernel32.dll via GetProcAddress:
 *   - Vista+: the real function is available, call it directly.
 *   - XP:     fall back to a CRITICAL_SECTION / semaphore implementation.
 *
 * SRW lock fallback: SRWLOCK is { PVOID Ptr }.  On XP we allocate a
 * CRITICAL_SECTION on the heap and store the pointer in Ptr.  Locks are
 * long-lived in curl (connection cache, share handle), so not explicitly
 * deleting them on shutdown is acceptable.
 *
 * Condition variable fallback: a semaphore + waiter counter stored behind
 * the CONDITION_VARIABLE Ptr field.  Provides correct signal / broadcast
 * semantics for the Mesa-style usage curl makes of condition variables.
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

#include <windows.h>

/* ── Probe helper ──────────────────────────────────────────────── */

static FARPROC cw_k32proc(const char* name)
{
    /* kernel32.dll is always mapped into every process; no LoadLibrary needed */
    HMODULE k32 = GetModuleHandleA("kernel32.dll");
    return k32 ? GetProcAddress(k32, name) : NULL;
}

/* ══════════════════════════════════════════════════════════════════
 *  SRW Locks
 * ══════════════════════════════════════════════════════════════════
 * SRWLOCK  =  { PVOID Ptr }  (single pointer, opaque on Vista+)
 * XP fallback stores a heap-allocated CRITICAL_SECTION in Ptr.
 */

typedef void  (WINAPI *fn_InitSRW)(PVOID);
typedef void  (WINAPI *fn_AcqSRWEx)(PVOID);
typedef void  (WINAPI *fn_RelSRWEx)(PVOID);
typedef void  (WINAPI *fn_AcqSRWSh)(PVOID);
typedef void  (WINAPI *fn_RelSRWSh)(PVOID);
typedef BOOL  (WINAPI *fn_TryAcqSRWEx)(PVOID);
typedef BOOL  (WINAPI *fn_TryAcqSRWSh)(PVOID);

/* Lazy-initialised, written once under the assumption of benign data races
 * (worst case: two threads both probe and get the same answer). */
static fn_InitSRW      pfn_InitializeSRWLock           = (fn_InitSRW)(LONG_PTR)-1;
static fn_AcqSRWEx     pfn_AcquireSRWLockExclusive     = (fn_AcqSRWEx)(LONG_PTR)-1;
static fn_RelSRWEx     pfn_ReleaseSRWLockExclusive     = (fn_RelSRWEx)(LONG_PTR)-1;
static fn_AcqSRWSh     pfn_AcquireSRWLockShared        = (fn_AcqSRWSh)(LONG_PTR)-1;
static fn_RelSRWSh     pfn_ReleaseSRWLockShared        = (fn_RelSRWSh)(LONG_PTR)-1;
static fn_TryAcqSRWEx  pfn_TryAcquireSRWLockExclusive  = (fn_TryAcqSRWEx)(LONG_PTR)-1;
static fn_TryAcqSRWSh  pfn_TryAcquireSRWLockShared     = (fn_TryAcqSRWSh)(LONG_PTR)-1;

#define PROBE(var, name, type) \
    if ((LONG_PTR)(var) == (LONG_PTR)-1) \
        (var) = (type)cw_k32proc(name)

/* XP helpers */
static CRITICAL_SECTION* cw_srw_cs(PVOID* ptr)
{
    return (CRITICAL_SECTION*)(*ptr);
}

static void cw_srw_init_xp(PVOID* ptr)
{
    CRITICAL_SECTION* cs = HeapAlloc(GetProcessHeap(), 0, sizeof(CRITICAL_SECTION));
    if (cs) InitializeCriticalSection(cs);
    *ptr = cs;
}

/* ── Public symbols ──────────────────────────────────────────── */

void WINAPI InitializeSRWLock(PVOID lock)
{
    PROBE(pfn_InitializeSRWLock, "InitializeSRWLock", fn_InitSRW);
    if (pfn_InitializeSRWLock) { pfn_InitializeSRWLock(lock); return; }
    cw_srw_init_xp((PVOID*)lock);
}

void WINAPI AcquireSRWLockExclusive(PVOID lock)
{
    PROBE(pfn_AcquireSRWLockExclusive, "AcquireSRWLockExclusive", fn_AcqSRWEx);
    if (pfn_AcquireSRWLockExclusive) { pfn_AcquireSRWLockExclusive(lock); return; }
    EnterCriticalSection(cw_srw_cs((PVOID*)lock));
}

void WINAPI ReleaseSRWLockExclusive(PVOID lock)
{
    PROBE(pfn_ReleaseSRWLockExclusive, "ReleaseSRWLockExclusive", fn_RelSRWEx);
    if (pfn_ReleaseSRWLockExclusive) { pfn_ReleaseSRWLockExclusive(lock); return; }
    LeaveCriticalSection(cw_srw_cs((PVOID*)lock));
}

void WINAPI AcquireSRWLockShared(PVOID lock)
{
    PROBE(pfn_AcquireSRWLockShared, "AcquireSRWLockShared", fn_AcqSRWSh);
    if (pfn_AcquireSRWLockShared) { pfn_AcquireSRWLockShared(lock); return; }
    /* Degrade to exclusive on XP — correct, just lower concurrency */
    EnterCriticalSection(cw_srw_cs((PVOID*)lock));
}

void WINAPI ReleaseSRWLockShared(PVOID lock)
{
    PROBE(pfn_ReleaseSRWLockShared, "ReleaseSRWLockShared", fn_RelSRWSh);
    if (pfn_ReleaseSRWLockShared) { pfn_ReleaseSRWLockShared(lock); return; }
    LeaveCriticalSection(cw_srw_cs((PVOID*)lock));
}

BOOL WINAPI TryAcquireSRWLockExclusive(PVOID lock)
{
    PROBE(pfn_TryAcquireSRWLockExclusive, "TryAcquireSRWLockExclusive", fn_TryAcqSRWEx);
    if (pfn_TryAcquireSRWLockExclusive) return pfn_TryAcquireSRWLockExclusive(lock);
    return TryEnterCriticalSection(cw_srw_cs((PVOID*)lock));
}

BOOL WINAPI TryAcquireSRWLockShared(PVOID lock)
{
    PROBE(pfn_TryAcquireSRWLockShared, "TryAcquireSRWLockShared", fn_TryAcqSRWSh);
    if (pfn_TryAcquireSRWLockShared) return pfn_TryAcquireSRWLockShared(lock);
    return TryEnterCriticalSection(cw_srw_cs((PVOID*)lock));
}

/* ══════════════════════════════════════════════════════════════════
 *  Condition Variables  (Vista+)
 * ══════════════════════════════════════════════════════════════════
 * CONDITION_VARIABLE = { PVOID Ptr } — same layout as SRWLOCK.
 * XP fallback: heap-allocated struct with a semaphore + waiter count.
 */

typedef struct
{
    HANDLE          sem;        /* counting semaphore                    */
    volatile LONG   waiters;    /* number of threads waiting             */
} CW_CondVarXP;

typedef void  (WINAPI *fn_InitCV)(PVOID);
typedef BOOL  (WINAPI *fn_SleepCVSRW)(PVOID cv, PVOID lock, DWORD ms, ULONG flags);
typedef BOOL  (WINAPI *fn_SleepCVCS)(PVOID cv, PVOID cs, DWORD ms);
typedef void  (WINAPI *fn_WakeCV)(PVOID);
typedef void  (WINAPI *fn_WakeAllCV)(PVOID);

static fn_InitCV      pfn_InitializeConditionVariable   = (fn_InitCV)(LONG_PTR)-1;
static fn_SleepCVSRW  pfn_SleepConditionVariableSRW     = (fn_SleepCVSRW)(LONG_PTR)-1;
static fn_SleepCVCS   pfn_SleepConditionVariableCS      = (fn_SleepCVCS)(LONG_PTR)-1;
static fn_WakeCV      pfn_WakeConditionVariable         = (fn_WakeCV)(LONG_PTR)-1;
static fn_WakeAllCV   pfn_WakeAllConditionVariable      = (fn_WakeAllCV)(LONG_PTR)-1;

static CW_CondVarXP* cw_cv_xp(PVOID* ptr)
{
    return (CW_CondVarXP*)(*ptr);
}

static void cw_cv_init_xp(PVOID* ptr)
{
    CW_CondVarXP* cv = HeapAlloc(GetProcessHeap(), 0, sizeof(CW_CondVarXP));
    if (!cv) return;
    cv->waiters = 0;
    cv->sem = CreateSemaphore(NULL, 0, 0x7FFFFFFF, NULL);
    if (!cv->sem) { HeapFree(GetProcessHeap(), 0, cv); return; }
    *ptr = cv;
}

void WINAPI InitializeConditionVariable(PVOID cv)
{
    PROBE(pfn_InitializeConditionVariable, "InitializeConditionVariable", fn_InitCV);
    if (pfn_InitializeConditionVariable) { pfn_InitializeConditionVariable(cv); return; }
    cw_cv_init_xp((PVOID*)cv);
}

void WINAPI WakeConditionVariable(PVOID cv)
{
    PROBE(pfn_WakeConditionVariable, "WakeConditionVariable", fn_WakeCV);
    if (pfn_WakeConditionVariable) { pfn_WakeConditionVariable(cv); return; }
    {
        CW_CondVarXP* xp = cw_cv_xp((PVOID*)cv);
        if (xp && xp->sem && xp->waiters > 0)
            ReleaseSemaphore(xp->sem, 1, NULL);
    }
}

void WINAPI WakeAllConditionVariable(PVOID cv)
{
    PROBE(pfn_WakeAllConditionVariable, "WakeAllConditionVariable", fn_WakeAllCV);
    if (pfn_WakeAllConditionVariable) { pfn_WakeAllConditionVariable(cv); return; }
    {
        CW_CondVarXP* xp = cw_cv_xp((PVOID*)cv);
        if (xp && xp->sem && xp->waiters > 0)
            ReleaseSemaphore(xp->sem, xp->waiters, NULL);
    }
}

BOOL WINAPI SleepConditionVariableSRW(PVOID cv, PVOID lock, DWORD ms, ULONG flags)
{
    PROBE(pfn_SleepConditionVariableSRW, "SleepConditionVariableSRW", fn_SleepCVSRW);
    if (pfn_SleepConditionVariableSRW) return pfn_SleepConditionVariableSRW(cv, lock, ms, flags);
    {
        CW_CondVarXP* xp = cw_cv_xp((PVOID*)cv);
        DWORD rc;
        if (!xp) return FALSE;
        InterlockedIncrement(&xp->waiters);
        /* Release the SRW lock (treated as exclusive on XP) */
        LeaveCriticalSection(cw_srw_cs((PVOID*)lock));
        rc = WaitForSingleObject(xp->sem, ms);
        InterlockedDecrement(&xp->waiters);
        EnterCriticalSection(cw_srw_cs((PVOID*)lock));
        return (rc == WAIT_OBJECT_0);
    }
}

BOOL WINAPI SleepConditionVariableCS(PVOID cv, PVOID cs, DWORD ms)
{
    PROBE(pfn_SleepConditionVariableCS, "SleepConditionVariableCS", fn_SleepCVCS);
    if (pfn_SleepConditionVariableCS) return pfn_SleepConditionVariableCS(cv, cs, ms);
    {
        CW_CondVarXP* xp = cw_cv_xp((PVOID*)cv);
        DWORD rc;
        if (!xp) return FALSE;
        InterlockedIncrement(&xp->waiters);
        LeaveCriticalSection((CRITICAL_SECTION*)cs);
        rc = WaitForSingleObject(xp->sem, ms);
        InterlockedDecrement(&xp->waiters);
        EnterCriticalSection((CRITICAL_SECTION*)cs);
        return (rc == WAIT_OBJECT_0);
    }
}
