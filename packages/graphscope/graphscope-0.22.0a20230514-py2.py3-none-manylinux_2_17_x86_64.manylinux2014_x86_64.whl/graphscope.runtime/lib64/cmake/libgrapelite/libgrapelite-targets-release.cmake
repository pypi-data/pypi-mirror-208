#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "grape-lite" for configuration "Release"
set_property(TARGET grape-lite APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(grape-lite PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LINK_INTERFACE_LIBRARIES_RELEASE "/opt/graphscope/lib/libmpi_cxx.so;/opt/graphscope/lib/libmpi.so;-pthread;/opt/graphscope/lib64/libglog.so"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libgrape-lite.a"
  )

list(APPEND _cmake_import_check_targets grape-lite )
list(APPEND _cmake_import_check_files_for_grape-lite "${_IMPORT_PREFIX}/lib/libgrape-lite.a" )

# Import target "analytical_apps" for configuration "Release"
set_property(TARGET analytical_apps APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(analytical_apps PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/run_app"
  )

list(APPEND _cmake_import_check_targets analytical_apps )
list(APPEND _cmake_import_check_files_for_analytical_apps "${_IMPORT_PREFIX}/bin/run_app" )

# Import target "gnn_sampler" for configuration "Release"
set_property(TARGET gnn_sampler APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(gnn_sampler PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/run_sampler"
  )

list(APPEND _cmake_import_check_targets gnn_sampler )
list(APPEND _cmake_import_check_files_for_gnn_sampler "${_IMPORT_PREFIX}/bin/run_sampler" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
