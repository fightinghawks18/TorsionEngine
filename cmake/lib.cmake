function(create_library lib_name sources)
    add_library(${lib_name} SHARED
        ${sources}
        "${SWIG_GEN}/${lib_name}_wrap.cpp"
    )

    target_include_directories(${lib_name} PRIVATE 
        "${CMAKE_CURRENT_SOURCE_DIR}/.."
        "${SWIG_GEN}"
    )

    set_target_properties(${lib_name}
        PROPERTIES
        PREFIX ""
        OUTPUT_NAME ${lib_name}
    )
endfunction()