include(lib)

find_package(SDL3 CONFIG REQUIRED)

add_library(OS SHARED
    window.cpp
)

target_link_libraries(OS
    PRIVATE
    SDL3::SDL3
)

install_library(OS os)