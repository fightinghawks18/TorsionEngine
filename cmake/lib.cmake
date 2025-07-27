# Serves the same purpose as add_library, but provides some automation
# May be more limited than add_library but it fits the needs of the engine
function(new_library name lib_name)
    set(sources ${ARGN})

    add_library(${name} ${sources})

    set_target_properties(${name}
        PROPERTIES
        PREFIX ""
        OUTPUT_NAME ${lib_name}
        SUFFIX ""
    )

    install(TARGETS ${name}
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
    )

    if(WIN32 AND CMAKE_BUILD_TYPE STREQUAL "Debug")
        install(FILES $<TARGET_PDB_FILE:${name}> 
            DESTINATION bin 
            OPTIONAL
        )
    endif()
endfunction()
