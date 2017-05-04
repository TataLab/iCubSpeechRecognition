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

add_executable(speech_recognizer src/speech_recognizer.cpp)
target_link_libraries(speech_recognizer ${POCKETSPHINX_LIBRARIES} ${SPHINXBASE_LIBRARIES} ${SPHINXAD_LIBRARIES} ${YARP_LIBRARIES})
