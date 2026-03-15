#if defined(__MINGW32__) && !defined(_GLIBCXX_HAS_GTHREADS)
#define DOCTEST_CONFIG_NO_MULTITHREADING
#endif
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"
