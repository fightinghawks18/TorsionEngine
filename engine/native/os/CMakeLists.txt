include(lib)

find_package(SDL3 CONFIG REQUIRED)

create_library(os window.cpp)
target_link_libraries(os
    PRIVATE
    SDL3::SDL3
)