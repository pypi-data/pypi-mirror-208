#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "vineyardd" for configuration "Release"
set_property(TARGET vineyardd APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(vineyardd PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/vineyardd"
  )

list(APPEND _cmake_import_check_targets vineyardd )
list(APPEND _cmake_import_check_files_for_vineyardd "${_IMPORT_PREFIX}/bin/vineyardd" )

# Import target "vineyard_internal_registry" for configuration "Release"
set_property(TARGET vineyard_internal_registry APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(vineyard_internal_registry PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libvineyard_internal_registry.so"
  IMPORTED_SONAME_RELEASE "libvineyard_internal_registry.so"
  )

list(APPEND _cmake_import_check_targets vineyard_internal_registry )
list(APPEND _cmake_import_check_files_for_vineyard_internal_registry "${_IMPORT_PREFIX}/lib/libvineyard_internal_registry.so" )

# Import target "vineyard_client" for configuration "Release"
set_property(TARGET vineyard_client APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(vineyard_client PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libvineyard_client.so"
  IMPORTED_SONAME_RELEASE "libvineyard_client.so"
  )

list(APPEND _cmake_import_check_targets vineyard_client )
list(APPEND _cmake_import_check_files_for_vineyard_client "${_IMPORT_PREFIX}/lib/libvineyard_client.so" )

# Import target "vineyard_basic" for configuration "Release"
set_property(TARGET vineyard_basic APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(vineyard_basic PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libvineyard_basic.so"
  IMPORTED_SONAME_RELEASE "libvineyard_basic.so"
  )

list(APPEND _cmake_import_check_targets vineyard_basic )
list(APPEND _cmake_import_check_files_for_vineyard_basic "${_IMPORT_PREFIX}/lib/libvineyard_basic.so" )

# Import target "vineyard_io" for configuration "Release"
set_property(TARGET vineyard_io APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(vineyard_io PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libvineyard_io.so"
  IMPORTED_SONAME_RELEASE "libvineyard_io.so"
  )

list(APPEND _cmake_import_check_targets vineyard_io )
list(APPEND _cmake_import_check_files_for_vineyard_io "${_IMPORT_PREFIX}/lib/libvineyard_io.so" )

# Import target "vineyard_graph" for configuration "Release"
set_property(TARGET vineyard_graph APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(vineyard_graph PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "gar"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libvineyard_graph.so"
  IMPORTED_SONAME_RELEASE "libvineyard_graph.so"
  )

list(APPEND _cmake_import_check_targets vineyard_graph )
list(APPEND _cmake_import_check_files_for_vineyard_graph "${_IMPORT_PREFIX}/lib/libvineyard_graph.so" )

# Import target "vineyard-graph-loader" for configuration "Release"
set_property(TARGET vineyard-graph-loader APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(vineyard-graph-loader PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/vineyard-graph-loader"
  )

list(APPEND _cmake_import_check_targets vineyard-graph-loader )
list(APPEND _cmake_import_check_files_for_vineyard-graph-loader "${_IMPORT_PREFIX}/bin/vineyard-graph-loader" )

# Import target "vineyard_malloc" for configuration "Release"
set_property(TARGET vineyard_malloc APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(vineyard_malloc PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libvineyard_malloc.so"
  IMPORTED_SONAME_RELEASE "libvineyard_malloc.so"
  )

list(APPEND _cmake_import_check_targets vineyard_malloc )
list(APPEND _cmake_import_check_files_for_vineyard_malloc "${_IMPORT_PREFIX}/lib/libvineyard_malloc.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
