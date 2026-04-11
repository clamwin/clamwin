# ClamWin GUI — Native Win32 C++ frontend
# Spawns clamscan.exe / freshclam.exe (no libclamav link dependency)

cmake_minimum_required(VERSION 3.14)
project(clamwin VERSION "1.5.2")

# ── curl + OpenSSL (from clamav-win32 prebuilts) ──────────────────────────
# The update checker uses libcurl + static OpenSSL for HTTPS so that TLS 1.2
# works on Windows XP without relying on the OS's SChannel.
get_filename_component(_CW_ROOT "${CMAKE_SOURCE_DIR}/.." ABSOLUTE)
set(_CLAMAV_WIN32_3P "${_CW_ROOT}/clamav-win32/3rdparty")

# Curl static library (built as part of the clamav-win32 build tree)
# We point at the curl source include dir; the .a is built there.
set(CW_CURL_INCLUDE "${_CLAMAV_WIN32_3P}/curl/include")

# OpenSSL prebuilt statics — arch-aware selection (x64 vs x86)
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    set(_CW_OPENSSL_LIB_DIR "${_CLAMAV_WIN32_3P}/openssl/lib/mingw/x64")
else()
    set(_CW_OPENSSL_LIB_DIR "${_CLAMAV_WIN32_3P}/openssl/lib/mingw/x86")
endif()
set(CW_OPENSSL_INCLUDE "${_CLAMAV_WIN32_3P}/openssl/include")

# These targets are created by the clamav-win32 sibling CMake project that
# must be the parent (or included) build.  When clamwin is built standalone
# (e.g. in CI without clamav-win32) fall back to find_library so the build
# still works if the .a files are present.
if(NOT TARGET libcurl_static)
    find_library(CW_LIBCURL   NAMES libcurl_static libcurl  HINTS "${_CLAMAV_WIN32_3P}/curl/lib" REQUIRED)
    find_library(CW_LIBSSL    NAMES ssl libssl                HINTS "${_CW_OPENSSL_LIB_DIR}" REQUIRED)
    find_library(CW_LIBCRYPTO NAMES crypto libcrypto          HINTS "${_CW_OPENSSL_LIB_DIR}" REQUIRED)
    set(CW_CURL_LINK_LIBS "${CW_LIBCURL}" "${CW_LIBSSL}" "${CW_LIBCRYPTO}")
else()
    set(CW_CURL_LINK_LIBS libcurl_static "${_CW_OPENSSL_LIB_DIR}/libssl.a" "${_CW_OPENSSL_LIB_DIR}/libcrypto.a")
endif()

set(clamwin
    cw_main.cpp
    cw_application.cpp
    cw_cli_args.cpp
    cw_auto_close.cpp
    cw_bg_task.cpp
    cw_log_utils.cpp
    cw_dashboard.cpp
    cw_window.cpp
    cw_dialog.cpp
    cw_config.cpp
    cw_process.cpp
    cw_scan_logic.cpp
    cw_prefs_validation.cpp
    cw_scan_dialog.cpp
    cw_about_dialog.cpp
    cw_logview_dialog.cpp
    cw_prefs_dialog.cpp
    cw_schedule_dialog.cpp
    cw_tray.cpp
    cw_scheduler.cpp
    cw_utils.cpp
    cw_theme.cpp
    cw_update_checker.cpp
)

# Legacy function-based GUI modules were removed after the cw_* class migration.
set(clamwin_legacy)

set(clamwin_resources resources/clamwin.rc)

set(CW_BUILD_COUNTER_FILE ${CMAKE_BINARY_DIR}/cw_gui_build_counter.txt)
set(CW_BUILD_VERSION_HEADER ${CMAKE_BINARY_DIR}/cw_build_version.h)
set(CW_BUILD_VERSION_RC ${CMAKE_BINARY_DIR}/cw_build_version.rc)
set(CW_BUILD_VERSION_SCRIPT ${CMAKE_SOURCE_DIR}/cmake/increment_clamwin_build_version.cmake)

# Seed generated version files at configure time so includes exist immediately.
execute_process(
    COMMAND ${CMAKE_COMMAND}
            -DCOUNTER_FILE=${CW_BUILD_COUNTER_FILE}
            -DHEADER_OUT=${CW_BUILD_VERSION_HEADER}
            -DRC_OUT=${CW_BUILD_VERSION_RC}
            -DBASE_MAJOR=${PROJECT_VERSION_MAJOR}
            -DBASE_MINOR=${PROJECT_VERSION_MINOR}
            -DBASE_PATCH=${PROJECT_VERSION_PATCH}
            -DINCREMENT=OFF
            -P ${CW_BUILD_VERSION_SCRIPT}
)

add_custom_target(cw_gui_build_version
    COMMAND ${CMAKE_COMMAND}
            -DCOUNTER_FILE=${CW_BUILD_COUNTER_FILE}
            -DHEADER_OUT=${CW_BUILD_VERSION_HEADER}
            -DRC_OUT=${CW_BUILD_VERSION_RC}
            -DBASE_MAJOR=${PROJECT_VERSION_MAJOR}
            -DBASE_MINOR=${PROJECT_VERSION_MINOR}
            -DBASE_PATCH=${PROJECT_VERSION_PATCH}
            -DINCREMENT=OFF
            -P ${CW_BUILD_VERSION_SCRIPT}
    BYPRODUCTS ${CW_BUILD_VERSION_HEADER} ${CW_BUILD_VERSION_RC}
    COMMENT "Generating ClamWin GUI build version header"
    VERBATIM
)

file(GLOB clamwin_headers *.h)

source_group("Source Files"  FILES ${clamwin})
source_group("Legacy Files"  FILES ${clamwin_legacy})
source_group("Header Files"  FILES ${clamwin_headers})
source_group("Resources"     FILES ${clamwin_resources})

add_executable(clamwin WIN32
    ${clamwin}
    ${clamwin_legacy}
    ${clamwin_headers}
    ${clamwin_resources}
)

set(clamwin_test_dir tests)
set(clamwin_test_sources
    ${clamwin_test_dir}/test_main.cpp
    ${clamwin_test_dir}/test_support.cpp
    ${clamwin_test_dir}/test_cli_args.cpp
    ${clamwin_test_dir}/test_auto_close.cpp
    ${clamwin_test_dir}/test_auto_close_integration.cpp
    ${clamwin_test_dir}/test_bg_task.cpp
    ${clamwin_test_dir}/test_shell_extension_command.cpp
    ${clamwin_test_dir}/test_config.cpp
    ${clamwin_test_dir}/test_scan_commands.cpp
    ${clamwin_test_dir}/test_scan_parsers.cpp
    ${clamwin_test_dir}/test_scan_transcripts.cpp
    ${clamwin_test_dir}/test_prefs_validation.cpp
    ${clamwin_test_dir}/test_real_tools.cpp
    ${clamwin_test_dir}/test_scheduler.cpp
    ${clamwin_test_dir}/test_utils.cpp
    ${clamwin_test_dir}/test_update_checker.cpp
    cw_config.cpp
    cw_cli_args.cpp
    cw_auto_close.cpp
    cw_bg_task.cpp
    cw_log_utils.cpp
    cw_process.cpp
    cw_scan_logic.cpp
    cw_prefs_validation.cpp
    cw_scheduler.cpp
    cw_utils.cpp
    cw_update_checker.cpp
    shell-extension/cw_shell_extension_command.cpp
)

add_executable(clamwin_test
    ${clamwin_test_sources}
)

add_dependencies(clamwin cw_gui_build_version)
add_dependencies(clamwin_test cw_gui_build_version)

if(MINGW)
    # libwinpthread.a ships a version.o member that contains a VERSIONINFO (.rsrc)
    # resource (type 10 / name 1 / lang 0x409).  When --whole-archive pulls the whole
    # archive into the link it clashes with our own VS_VERSION_INFO block in clamwin.rc,
    # producing "duplicate leaf: type: 10 (VERSION) name: 1 lang: 409".
    # Fix: make a stripped copy of libwinpthread.a with version.o deleted, and link
    # against that copy instead.  The version.o member contains only resource data and
    # no code symbols, so removing it is safe.
    execute_process(
        COMMAND ${CMAKE_CXX_COMPILER} -print-file-name=libwinpthread.a
        OUTPUT_VARIABLE _cw_winpthread_src
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    set(_cw_winpthread_stripped ${CMAKE_BINARY_DIR}/libwinpthread_norsrc.a)

    add_custom_command(
        OUTPUT  ${_cw_winpthread_stripped}
        COMMAND ${CMAKE_COMMAND} -E copy ${_cw_winpthread_src} ${_cw_winpthread_stripped}
        COMMAND ${CMAKE_AR} d ${_cw_winpthread_stripped} version.o
        DEPENDS ${_cw_winpthread_src}
        COMMENT "Stripping version resource from libwinpthread.a"
        VERBATIM
    )
    add_custom_target(cw_winpthread_stripped DEPENDS ${_cw_winpthread_stripped})
    add_dependencies(clamwin      cw_winpthread_stripped)
    add_dependencies(clamwin_test cw_winpthread_stripped)

    # -static-libstdc++ / -static-libgcc link the C++ and GCC runtime statically.
    # libstdc++ (posix thread model) references pthread_create; we must ensure
    # libwinpthread.a (static) is used instead of the DLL import library.
    # --whole-archive pre-loads all libwinpthread.a symbols so they are already
    # defined when libstdc++'s implicit trailing pass resolves pthread_create.
    target_link_options(clamwin PRIVATE
        -static-libstdc++ -static-libgcc
        -Wl,--whole-archive,-Bstatic ${_cw_winpthread_stripped} -Wl,-Bdynamic,--no-whole-archive)
    target_link_options(clamwin_test PRIVATE
        -static-libstdc++ -static-libgcc
        -Wl,--whole-archive,-Bstatic ${_cw_winpthread_stripped} -Wl,-Bdynamic,--no-whole-archive)
endif()

if(MSVC)
    target_sources(clamwin PRIVATE ${CMAKE_SOURCE_DIR}/resources/compatibility.manifest)
    target_link_options(clamwin PRIVATE "/MANIFEST:NO")
endif()

target_include_directories(clamwin PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_BINARY_DIR}
    ${CW_CURL_INCLUDE}
    ${CW_OPENSSL_INCLUDE}
)

target_include_directories(clamwin_test PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/shell-extension
    ${CMAKE_SOURCE_DIR}/3rdparty/doctest
    ${CMAKE_BINARY_DIR}
    ${clamwin_test_dir}
    ${CW_CURL_INCLUDE}
    ${CW_OPENSSL_INCLUDE}
)

target_compile_definitions(clamwin PRIVATE
    _CRT_SECURE_NO_WARNINGS
    CURL_STATICLIB
)

target_compile_definitions(clamwin_test PRIVATE
    _CRT_SECURE_NO_WARNINGS
    CURL_STATICLIB
)

target_link_libraries(clamwin PRIVATE
    comctl32
    shlwapi
    version
    ${CW_CURL_LINK_LIBS}
    crypt32
    ws2_32
)

target_link_libraries(clamwin_test PRIVATE
    shlwapi
    ${CW_CURL_LINK_LIBS}
    crypt32
    ws2_32
)

add_custom_target(clamwin_check
    COMMAND $<TARGET_FILE:clamwin_test>
    DEPENDS clamwin_test
    WORKING_DIRECTORY $<TARGET_FILE_DIR:clamwin_test>
    USES_TERMINAL
)

add_custom_target(clamwin_check_real_tools
    COMMAND ${CMAKE_COMMAND} -E env CLAMWIN_REAL_TOOLS=1 $<TARGET_FILE:clamwin_test>
    DEPENDS clamwin_test
    WORKING_DIRECTORY $<TARGET_FILE_DIR:clamwin_test>
    USES_TERMINAL
)

add_subdirectory(shell-extension)

list(APPEND CLAMAV_INSTALL_TARGETS clamwin)
