include(lib)

find_package(SDL3 CONFIG REQUIRED)

create_library(OS
    window.cpp
)

target_link_libraries(OS
    PRIVATE
    SDL3::SDL3
)