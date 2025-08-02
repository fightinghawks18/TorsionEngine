include(lib)

find_package(SDL3 CONFIG REQUIRED)

add_library(OS SHARED
    window.cpp
    ${SWIG_GEN}/os_wrap.cpp
)

target_link_libraries(OS
    PRIVATE
    SDL3::SDL3
)

target_include_directories(OS PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/..
    ${SWIG_GEN}
)

install_library(OS os)