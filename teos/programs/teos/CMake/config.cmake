message(STATUS "includes teosontract.cmake")
set(CMAKE_INSTALL_PREFIX "${PROJECT_SOURCE_DIR}/../target")
set(EOSIO_INSTALL_DIR "/mnt/hgfs/Workspaces/EOS/eos")
message(STATUS "EOSIO_INSTALL_DIR: ${EOSIO_INSTALL_DIR}")
message(STATUS "CMAKE_INSTALL_PREFIX: ${CMAKE_INSTALL_PREFIX}")

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_BUILD_TYPE Debug) 

include_directories("${CMAKE_INSTALL_PREFIX}/include")