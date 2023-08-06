# ============================================================================
# To use the Akida model API with generated fixtures you have to include the
# CMake folder and link the library akida to your CMake target as following:
#
# set(CMAKE_INCLUDE_CURRENT_DIR ON)
# set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR}/cmake)
# include(akida-model)
# target_link_libraries(my_program PRIVATE akida)
# ============================================================================

cmake_minimum_required(VERSION 3.20)
set(Python_FIND_VIRTUALENV ONLY)
set(Python_FIND_REGISTRY LAST)
find_package(Python 3.7...<3.11 REQUIRED COMPONENTS Interpreter)
cmake_path(CONVERT "${Python_SITELIB}/akida" TO_CMAKE_PATH_LIST AKIDA_PATH)

if (WIN32)
    install(FILES ${AKIDA_PATH}/akida.dll DESTINATION ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
endif()

SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

find_library(AKIDA_LIB NAMES akida libakida.so.2 PATHS ${AKIDA_PATH} NO_DEFAULT_PATH REQUIRED)

add_library(akida INTERFACE)
target_link_libraries(akida INTERFACE ${AKIDA_LIB})
target_include_directories(akida INTERFACE
    ${AKIDA_PATH}/api
    ${AKIDA_PATH}/engine/api/
    ${AKIDA_PATH})
