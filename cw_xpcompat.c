/*
 * cw_xpcompat.c — XP-compatible shims for Vista+ kernel32 APIs
 *
 * libcurl (compiled with _WIN32_WINNT >= 0x0600) references SRW lock and
 * condition variable functions that exist in kernel32.dll only on Vista+.
 * Windows XP's kernel32.dll has the DLL but not these exports, producing
 * "Entry Point Not Found" at process startup before main() runs.
 *
 * This file is compiled with _WIN32_WINNT=0x0501 so that synchapi.h does
 * NOT declare these functions (they're guarded by _WIN32_WINNT >= 0x0600).
 * We then define the Vista+ types manually and provide our own
 * implementations that dynamically probe kernel32.dll at first use:
 *   - Vista+: the real kernel32 export is available, call it.
 *   - XP:     fall back to CRITICAL_SECTION (SRW) / semaphore (condvar).
 *
 * Copyright (c) 2004-2026 ClamWin Pty Ltd
 * License: GPLv2
 */

/* Must be set before any Windows headers so synchapi.h skips Vista+ decls */
#undef  _WIN32_WINNT
#define _WIN32_WINNT 0x0501

#include <windows.h>

/* ── Vista+ types not declared when _WIN32_WINNT=0x0501 ────────── */

typedef struct _CW_SRWLOCK          { PVOID Ptr; } CW_SRWLOCK, *PCW_SRWLOCK;
typedef struct _CW_CONDITION_VARIABLE { PVOID Ptr; } CW_CONDITION_VARIABLE, *PCW_CONDITION_VARIABLE;
typedef unsigned char CW_BOOLEAN;

/* ── Probe helper ──────────────────────────────────────────────── */

static FARPROC cw_k32proc(const char* name)
{
    HMODULE k32 = GetModuleHandleA("kernel32.dll");
    return k32 ? GetProcAddress(k32, name) : NULL;
}

/* ══════════════════════════════════════════════════════════════════
 *  SRW Locks
 * ══════════════════════════════════════════════════════════════════
 * XP fallback stores a heap-allocated CRITICAL_SECTION in Ptr.
 */

typedef void        (WINAPI *fn_InitSRW)      (PCW_SRWLOCK);
typedef void        (WINAPI *fn_AcqSRWEx)     (PCW_SRWLOCK);
typedef void        (WINAPI *fn_RelSRWEx)     (PCW_SRWLOCK);
typedef void        (WINAPI *fn_AcqSRWSh)     (PCW_SRWLOCK);
typedef void        (WINAPI *fn_RelSRWSh)     (PCW_SRWLOCK);
typedef CW_BOOLEAN  (WINAPI *fn_TryAcqSRWEx)  (PCW_SRWLOCK);
typedef CW_BOOLEAN  (WINAPI *fn_TryAcqSRWSh)  (PCW_SRWLOCK);

#define SENTINEL ((FARPROC)(LONG_PTR)-1)
#define PROBE(var, name, type) \
    if ((FARPROC)(var) == SENTINEL) (var) = (type)cw_k32proc(name)

static fn_InitSRW     pfn_InitializeSRWLock          = (fn_InitSRW)SENTINEL;
static fn_AcqSRWEx    pfn_AcquireSRWLockExclusive    = (fn_AcqSRWEx)SENTINEL;
static fn_RelSRWEx    pfn_ReleaseSRWLockExclusive    = (fn_RelSRWEx)SENTINEL;
static fn_AcqSRWSh    pfn_AcquireSRWLockShared       = (fn_AcqSRWSh)SENTINEL;
static fn_RelSRWSh    pfn_ReleaseSRWLockShared       = (fn_RelSRWSh)SENTINEL;
static fn_TryAcqSRWEx pfn_TryAcquireSRWLockExclusive = (fn_TryAcqSRWEx)SENTINEL;
static fn_TryAcqSRWSh pfn_TryAcquireSRWLockShared    = (fn_TryAcqSRWSh)SENTINEL;

static CRITICAL_SECTION* cw_srw_cs(PCW_SRWLOCK lock) { return (CRITICAL_SECTION*)(lock->Ptr); }

static void cw_srw_init_xp(PCW_SRWLOCK lock)
{
    CRITICAL_SECTION* cs = HeapAlloc(GetProcessHeap(), 0, sizeof(CRITICAL_SECTION));
    if (cs) InitializeCriticalSection(cs);
    lock->Ptr = cs;
}

void WINAPI InitializeSRWLock(PCW_SRWLOCK lock)
{
    PROBE(pfn_InitializeSRWLock, "InitializeSRWLock", fn_InitSRW);
    if (pfn_InitializeSRWLock) { pfn_InitializeSRWLock(lock); return; }
    cw_srw_init_xp(lock);
}

void WINAPI AcquireSRWLockExclusive(PCW_SRWLOCK lock)
{
    PROBE(pfn_AcquireSRWLockExclusive, "AcquireSRWLockExclusive", fn_AcqSRWEx);
    if (pfn_AcquireSRWLockExclusive) { pfn_AcquireSRWLockExclusive(lock); return; }
    EnterCriticalSection(cw_srw_cs(lock));
}

void WINAPI ReleaseSRWLockExclusive(PCW_SRWLOCK lock)
{
    PROBE(pfn_ReleaseSRWLockExclusive, "ReleaseSRWLockExclusive", fn_RelSRWEx);
    if (pfn_ReleaseSRWLockExclusive) { pfn_ReleaseSRWLockExclusive(lock); return; }
    LeaveCriticalSection(cw_srw_cs(lock));
}

void WINAPI AcquireSRWLockShared(PCW_SRWLOCK lock)
{
    PROBE(pfn_AcquireSRWLockShared, "AcquireSRWLockShared", fn_AcqSRWSh);
    if (pfn_AcquireSRWLockShared) { pfn_AcquireSRWLockShared(lock); return; }
    EnterCriticalSection(cw_srw_cs(lock));  /* degrade to exclusive on XP */
}

void WINAPI ReleaseSRWLockShared(PCW_SRWLOCK lock)
{
    PROBE(pfn_ReleaseSRWLockShared, "ReleaseSRWLockShared", fn_RelSRWSh);
    if (pfn_ReleaseSRWLockShared) { pfn_ReleaseSRWLockShared(lock); return; }
    LeaveCriticalSection(cw_srw_cs(lock));
}

CW_BOOLEAN WINAPI TryAcquireSRWLockExclusive(PCW_SRWLOCK lock)
{
    PROBE(pfn_TryAcquireSRWLockExclusive, "TryAcquireSRWLockExclusive", fn_TryAcqSRWEx);
    if (pfn_TryAcquireSRWLockExclusive) return pfn_TryAcquireSRWLockExclusive(lock);
    return (CW_BOOLEAN)TryEnterCriticalSection(cw_srw_cs(lock));
}

CW_BOOLEAN WINAPI TryAcquireSRWLockShared(PCW_SRWLOCK lock)
{
    PROBE(pfn_TryAcquireSRWLockShared, "TryAcquireSRWLockShared", fn_TryAcqSRWSh);
    if (pfn_TryAcquireSRWLockShared) return pfn_TryAcquireSRWLockShared(lock);
    return (CW_BOOLEAN)TryEnterCriticalSection(cw_srw_cs(lock));
}

/* ══════════════════════════════════════════════════════════════════
 *  Condition Variables  (Vista+)
 * ══════════════════════════════════════════════════════════════════
 * XP fallback: heap-allocated {semaphore, waiter count} behind Ptr.
 */

typedef struct
{
    HANDLE        sem;
    volatile LONG waiters;
} CW_CondVarXP;

typedef void   (WINAPI *fn_InitCV)    (PCW_CONDITION_VARIABLE);
typedef BOOL   (WINAPI *fn_SleepCVSRW)(PCW_CONDITION_VARIABLE, PCW_SRWLOCK, DWORD, ULONG);
typedef BOOL   (WINAPI *fn_SleepCVCS) (PCW_CONDITION_VARIABLE, PCRITICAL_SECTION, DWORD);
typedef void   (WINAPI *fn_WakeCV)    (PCW_CONDITION_VARIABLE);
typedef void   (WINAPI *fn_WakeAllCV) (PCW_CONDITION_VARIABLE);

static fn_InitCV     pfn_InitializeConditionVariable  = (fn_InitCV)SENTINEL;
static fn_SleepCVSRW pfn_SleepConditionVariableSRW    = (fn_SleepCVSRW)SENTINEL;
static fn_SleepCVCS  pfn_SleepConditionVariableCS     = (fn_SleepCVCS)SENTINEL;
static fn_WakeCV     pfn_WakeConditionVariable        = (fn_WakeCV)SENTINEL;
static fn_WakeAllCV  pfn_WakeAllConditionVariable     = (fn_WakeAllCV)SENTINEL;

static CW_CondVarXP* cw_cv_xp(PCW_CONDITION_VARIABLE cv) { return (CW_CondVarXP*)(cv->Ptr); }

static void cw_cv_init_xp(PCW_CONDITION_VARIABLE cv)
{
    CW_CondVarXP* x = HeapAlloc(GetProcessHeap(), 0, sizeof(CW_CondVarXP));
    if (!x) return;
    x->waiters = 0;
    x->sem = CreateSemaphoreA(NULL, 0, 0x7FFFFFFF, NULL);
    if (!x->sem) { HeapFree(GetProcessHeap(), 0, x); return; }
    cv->Ptr = x;
}

void WINAPI InitializeConditionVariable(PCW_CONDITION_VARIABLE cv)
{
    PROBE(pfn_InitializeConditionVariable, "InitializeConditionVariable", fn_InitCV);
    if (pfn_InitializeConditionVariable) { pfn_InitializeConditionVariable(cv); return; }
    cw_cv_init_xp(cv);
}

void WINAPI WakeConditionVariable(PCW_CONDITION_VARIABLE cv)
{
    PROBE(pfn_WakeConditionVariable, "WakeConditionVariable", fn_WakeCV);
    if (pfn_WakeConditionVariable) { pfn_WakeConditionVariable(cv); return; }
    { CW_CondVarXP* x = cw_cv_xp(cv); if (x && x->waiters > 0) ReleaseSemaphore(x->sem, 1, NULL); }
}

void WINAPI WakeAllConditionVariable(PCW_CONDITION_VARIABLE cv)
{
    PROBE(pfn_WakeAllConditionVariable, "WakeAllConditionVariable", fn_WakeAllCV);
    if (pfn_WakeAllConditionVariable) { pfn_WakeAllConditionVariable(cv); return; }
    { CW_CondVarXP* x = cw_cv_xp(cv); if (x && x->waiters > 0) ReleaseSemaphore(x->sem, x->waiters, NULL); }
}

BOOL WINAPI SleepConditionVariableSRW(PCW_CONDITION_VARIABLE cv, PCW_SRWLOCK lock,
                                       DWORD ms, ULONG flags)
{
    PROBE(pfn_SleepConditionVariableSRW, "SleepConditionVariableSRW", fn_SleepCVSRW);
    if (pfn_SleepConditionVariableSRW) return pfn_SleepConditionVariableSRW(cv, lock, ms, flags);
    {
        CW_CondVarXP* x = cw_cv_xp(cv);
        DWORD rc;
        if (!x) return FALSE;
        InterlockedIncrement(&x->waiters);
        LeaveCriticalSection(cw_srw_cs(lock));
        rc = WaitForSingleObject(x->sem, ms);
        InterlockedDecrement(&x->waiters);
        EnterCriticalSection(cw_srw_cs(lock));
        return rc == WAIT_OBJECT_0;
    }
}

BOOL WINAPI SleepConditionVariableCS(PCW_CONDITION_VARIABLE cv, PCRITICAL_SECTION cs,
                                      DWORD ms)
{
    PROBE(pfn_SleepConditionVariableCS, "SleepConditionVariableCS", fn_SleepCVCS);
    if (pfn_SleepConditionVariableCS) return pfn_SleepConditionVariableCS(cv, cs, ms);
    {
        CW_CondVarXP* x = cw_cv_xp(cv);
        DWORD rc;
        if (!x) return FALSE;
        InterlockedIncrement(&x->waiters);
        LeaveCriticalSection(cs);
        rc = WaitForSingleObject(x->sem, ms);
        InterlockedDecrement(&x->waiters);
        EnterCriticalSection(cs);
        return rc == WAIT_OBJECT_0;
    }
}
