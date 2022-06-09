# CMakeList.txt : CMake project for numbers_transform, include source and define
# project specific logic here.
#
cmake_minimum_required (VERSION 3.8)

project(numbers_transform)

set(CMAKE_CXX_STANDARD 20)

file(GLOB SRC "*.cpp")
if (NOT "${PARENT_SRC}" STREQUAL "")
	set(SRC ${SRC} ${PARENT_SRC})
endif()
file(GLOB HEADERS "*.h")

add_executable (numbers_transform ${SRC} ${HEADERS})


