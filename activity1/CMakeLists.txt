project(minimal_set_cover_greedy)

cmake_minimum_required(VERSION 3.12)

add_executable(minimal_set_cover_greedy main.cpp)

target_include_directories(minimal_set_cover_greedy PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

set_target_properties(minimal_set_cover_greedy PROPERTIES 
    CXX_STANDARD 20 
    DEBUG_POSTFIX "d"
    RELEASE_POSTFIX ""
)

install(TARGETS minimal_set_cover_greedy DESTINATION ${CMAKE_INSTALL_PREFIX})