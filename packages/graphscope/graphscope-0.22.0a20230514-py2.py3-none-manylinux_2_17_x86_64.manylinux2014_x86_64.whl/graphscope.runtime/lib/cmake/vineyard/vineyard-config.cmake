# - Config file for the vineyard package
#
# It defines the following variables
#
#  VINEYARD_INCLUDE_DIR         - include directory for vineyard
#  VINEYARD_INCLUDE_DIRS        - include directories for vineyard
#  VINEYARD_LIBRARIES           - libraries to link against
#  VINEYARDD_EXECUTABLE         - the vineyardd executable
#  VINEYARD_CODEGEN_EXECUTABLE  - the vineyard codegen executable

set(USE_ASAN )
set(USE_LIBUNWIND ON)

set(BUILD_VINEYARD_SERVER ON)
set(BUILD_VINEYARD_CLIENT ON)
set(BUILD_VINEYARD_PYTHON_BINDINGS ON)
set(BUILD_VINEYARD_PYPI_PACKAGES OFF)

set(BUILD_VINEYARD_BASIC ON)
set(BUILD_VINEYARD_IO ON)
set(BUILD_VINEYARD_IO_KAFKA OFF)
set(BUILD_VINEYARD_GRAPH ON)
set(BUILD_VINEYARD_GRAPH_WITH_GAR ON)
set(BUILD_VINEYARD_MALLOC ON)
set(BUILD_VINEYARD_FUSE OFF)
set(BUILD_VINEYARD_FUSE_PARQUET OFF)
set(BUILD_VINEYARD_HOSSEINMOEIN_DATAFRAME OFF)

set(BUILD_VINEYARD_TESTS OFF)
set(BUILD_VINEYARD_TESTS_ALL OFF)
set(BUILD_VINEYARD_COVERAGE OFF)
set(BUILD_VINEYARD_PROFILING OFF)

# find pthread
find_package(Threads)

# for finding dependencies
include(CMakeFindDependencyMacro)

# find apache-arrow
if(NOT Arrow_FOUND AND NOT TARGET arrow_shared AND NOT TARGET arrow_static)
    find_package(Arrow QUIET)
    if(NOT Arrow_FOUND)
        list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
        find_dependency(Arrow)
    endif()
endif()

if(BUILD_VINEYARD_GRAPH)
    if(NOT TARGET grape-lite)
        find_dependency(libgrapelite)
    endif()
endif()

if(BUILD_VINEYARD_IO AND BUILD_VINEYARD_IO_KAFKA)
    list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
    if(NOT Rdkafka_FOUND)
        find_dependency(Rdkafka)
    endif()
endif()

if(BUILD_VINEYARD_GRAPH AND BUILD_VINEYARD_GRAPH_WITH_GAR)
    if(NOT TARGET gar)
        find_dependency(gar)
    endif()
endif()

if(USE_LIBUNWIND)
    list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
    if(NOT LIBUNWIND_LIBRARIES)
        find_package(LibUnwind QUIET)
    endif()
endif()

set(VINEYARD_HOME "${CMAKE_CURRENT_LIST_DIR}/../../..")
include("${CMAKE_CURRENT_LIST_DIR}/vineyard-targets.cmake")

set(VINEYARD_LIBRARIES vineyard_client;vineyard_basic;vineyard_io;vineyard_graph;vineyard_malloc)
set(VINEYARD_INCLUDE_DIR "${VINEYARD_HOME}/include"
                         "${VINEYARD_HOME}/include/vineyard"
                         "${VINEYARD_HOME}/include/vineyard/contrib")
set(VINEYARD_INCLUDE_DIRS "${VINEYARD_INCLUDE_DIR}")

set(VINEYARDD_EXECUTABLE "${VINEYARD_HOME}/bin/vineyardd")

set(VINEYARD_CODEGEN_EXECUTABLE "${VINEYARD_HOME}/bin/vineyard-codegen")

include(FindPackageMessage)
find_package_message(vineyard
    "Found vineyard: ${CMAKE_CURRENT_LIST_FILE} (found version \"0.14.5\")"
    "Vineyard version: 0.14.5\nVineyard libraries: ${VINEYARD_LIBRARIES}, include directories: ${VINEYARD_INCLUDE_DIRS}"
)
