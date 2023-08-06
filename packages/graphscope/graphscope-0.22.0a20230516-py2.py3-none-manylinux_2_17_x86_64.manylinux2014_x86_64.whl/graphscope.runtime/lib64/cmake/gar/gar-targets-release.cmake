#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "gar" for configuration "Release"
set_property(TARGET gar APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(gar PROPERTIES
  IMPORTED_LINK_INTERFACE_LIBRARIES_RELEASE ""
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libgar.so"
  IMPORTED_SONAME_RELEASE "libgar.so"
  )

list(APPEND _cmake_import_check_targets gar )
list(APPEND _cmake_import_check_files_for_gar "${_IMPORT_PREFIX}/lib/libgar.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
