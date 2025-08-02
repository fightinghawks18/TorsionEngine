# Serves the same purpose as add_library, but provides some automation
# May be more limited than add_library but it fits the needs of the engine
function(install_library lib lib_name)

    set_target_properties(${lib}
        PROPERTIES
        PREFIX ""
        OUTPUT_NAME ${lib_name}
    )
endfunction()
