set(clamwin_shell_extension_sources
    ${CMAKE_CURRENT_SOURCE_DIR}/cw_shell_extension.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/cw_shell_extension_impl.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/cw_shell_extension.rc
    ${CMAKE_CURRENT_SOURCE_DIR}/cw_shell_extension.def
    ${CMAKE_CURRENT_SOURCE_DIR}/cw_shell_extension_command.cpp
)

set(clamwin_shell_extension_headers
    ${CMAKE_CURRENT_SOURCE_DIR}/cw_shell_extension.h
    ${CMAKE_CURRENT_SOURCE_DIR}/cw_shell_extension_resource.h
    ${CMAKE_CURRENT_SOURCE_DIR}/cw_shell_extension_command.h
)

set(CLAMWIN_SHELLEXT_UNICODE "" CACHE STRING
    "Shell extension TCHAR mode. Must be explicitly set to ON (Unicode) or OFF (ANSI)."
)
set_property(CACHE CLAMWIN_SHELLEXT_UNICODE PROPERTY STRINGS ON OFF)

if(NOT CLAMWIN_SHELLEXT_UNICODE MATCHES "^(ON|OFF)$")
    get_filename_component(_cw_shell_build_dir_name "${CMAKE_BINARY_DIR}" NAME)

    if(_cw_shell_build_dir_name MATCHES "(ansi|win98)$")
        set(CLAMWIN_SHELLEXT_UNICODE OFF CACHE STRING
            "Shell extension TCHAR mode. Must be explicitly set to ON (Unicode) or OFF (ANSI)."
            FORCE
        )
    elseif(_cw_shell_build_dir_name MATCHES "^(build|build-gui|build-x86-mingw-winxp|build-x64.*)$")
        set(CLAMWIN_SHELLEXT_UNICODE ON CACHE STRING
            "Shell extension TCHAR mode. Must be explicitly set to ON (Unicode) or OFF (ANSI)."
            FORCE
        )
    endif()
endif()

if(NOT CLAMWIN_SHELLEXT_UNICODE MATCHES "^(ON|OFF)$")
    message(FATAL_ERROR
        "Unable to determine CLAMWIN_SHELLEXT_UNICODE for build directory '${CMAKE_BINARY_DIR}'. "
        "Use -DCLAMWIN_SHELLEXT_UNICODE=ON for Unicode builds (x64/winxp) "
        "or -DCLAMWIN_SHELLEXT_UNICODE=OFF for ANSI builds (win98)."
    )
endif()

add_library(clamwin_shell_extension SHARED
    ${clamwin_shell_extension_sources}
    ${clamwin_shell_extension_headers}
)

set_target_properties(clamwin_shell_extension PROPERTIES
    OUTPUT_NAME ExpShell
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
    ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

foreach(_cfg Debug Release RelWithDebInfo MinSizeRel)
    string(TOUPPER ${_cfg} _cfg_upper)
    set_target_properties(clamwin_shell_extension PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY_${_cfg_upper} ${CMAKE_BINARY_DIR}
        LIBRARY_OUTPUT_DIRECTORY_${_cfg_upper} ${CMAKE_BINARY_DIR}
        ARCHIVE_OUTPUT_DIRECTORY_${_cfg_upper} ${CMAKE_BINARY_DIR}
    )
endforeach()

target_include_directories(clamwin_shell_extension PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CLAMWIN_DIR}/src/clamwin-gui-cpp
)

target_compile_definitions(clamwin_shell_extension PRIVATE
    ${CLAMWIN_DEFINES}
    _CRT_SECURE_NO_WARNINGS
)

if(CLAMWIN_SHELLEXT_UNICODE STREQUAL "ON")
    target_compile_definitions(clamwin_shell_extension PRIVATE UNICODE _UNICODE)
endif()

if(MINGW)
    if(TARGET cw_winpthread_stripped)
        add_dependencies(clamwin_shell_extension cw_winpthread_stripped)
    endif()

    target_link_options(clamwin_shell_extension PRIVATE
        -static-libstdc++ -static-libgcc
        -Wl,--whole-archive,-Bstatic ${_cw_winpthread_stripped} -Wl,-Bdynamic,--no-whole-archive
        -Wl,--enable-stdcall-fixup
    )
endif()

target_link_libraries(clamwin_shell_extension PRIVATE
    shell32
    ole32
    advapi32
    user32
)

list(APPEND CLAMAV_INSTALL_TARGETS clamwin_shell_extension)
