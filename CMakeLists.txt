# ClamWin GUI — Native Win32 C++ frontend
# Spawns clamscan.exe / freshclam.exe (no libclamav link dependency)

cmake_minimum_required(VERSION 3.14)
project(clamwin VERSION "1.5.2")

set(clamwin
    cw_main.cpp
    cw_application.cpp
    cw_cli_args.cpp
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
            -P ${CW_BUILD_VERSION_SCRIPT}
    BYPRODUCTS ${CW_BUILD_VERSION_HEADER} ${CW_BUILD_VERSION_RC}
    COMMENT "Incrementing ClamWin GUI build number"
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

if(MSVC)
    target_sources(clamwin PRIVATE ${CMAKE_SOURCE_DIR}/resources/compatibility.manifest)
    target_link_options(clamwin PRIVATE "/MANIFEST:NO")
endif()

target_include_directories(clamwin PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_BINARY_DIR}
)

target_include_directories(clamwin_test PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/shell-extension
    ${CMAKE_SOURCE_DIR}/3rdparty/doctest
    ${CMAKE_BINARY_DIR}
    ${clamwin_test_dir}
)

target_compile_definitions(clamwin PRIVATE
    _CRT_SECURE_NO_WARNINGS
)

target_compile_definitions(clamwin_test PRIVATE
    _CRT_SECURE_NO_WARNINGS
)

target_link_libraries(clamwin PRIVATE
    comctl32
    shlwapi
    wininet
    gdiplus
    version
)

target_link_libraries(clamwin_test PRIVATE
    shlwapi
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
