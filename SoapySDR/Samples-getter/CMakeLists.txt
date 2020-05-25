cmake_minimum_required(VERSION 3.6)
project(SoapySDR-Test)

find_package(SoapySDR REQUIRED)
if(NOT SoapySDR_FOUND)
    message(SEND_ERROR "Failed to find SoapySDR library!")
endif()

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17 -Wall")

add_executable(${PROJECT_NAME} main.cpp)

target_link_libraries(${PROJECT_NAME} SoapySDR)