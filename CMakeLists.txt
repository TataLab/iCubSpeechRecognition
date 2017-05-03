# Copyright: (C) 2010 RobotCub Consortium
# Author: Paul Fitzpatrick
# CopyPolicy: Released under the terms of the LGPLv2.1 or later, see LGPL.TXT
# YARP needs CMake 2.8.9 or greater

cmake_minimum_required(VERSION 2.8.9)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/Modules/")

find_package(SphinxBase REQUIRED)
find_package(PocketSphinx REQUIRED)

FIND_PACKAGE(YARP REQUIRED)
INCLUDE_DIRECTORIES(${YARP_INCLUDE_DIRS})
LINK_LIBRARIES(${YARP_LIBRARIES})

include_directories(
  ${SPHINXBASE_INCLUDE_DIRS}
  ${POCKETSPHINX_INCLUDE_DIRS}
)

# set up our program
add_executable(continuous continuous.c)
target_link_libraries(continuous ${POCKETSPHINX_LIBRARIES} ${SPHINXBASE_LIBRARIES} ${SPHINXAD_LIBRARIES})

add_executable(recognize recognize.cpp)
target_link_libraries(recognize ${POCKETSPHINX_LIBRARIES} ${SPHINXBASE_LIBRARIES} ${SPHINXAD_LIBRARIES})

ADD_EXECUTABLE(sound_receiver sound_receiver.cpp)
TARGET_LINK_LIBRARIES(sound_receiver ${YARP_LIBRARIES})
