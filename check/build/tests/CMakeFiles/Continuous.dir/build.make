# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 2.8

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list

# Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/neil/Documents/cs4098/check

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/neil/Documents/cs4098/check/build

# Utility rule file for Continuous.

# Include the progress variables for this target.
include tests/CMakeFiles/Continuous.dir/progress.make

tests/CMakeFiles/Continuous:
	cd /home/neil/Documents/cs4098/check/build/tests && /usr/bin/ctest -D Continuous

Continuous: tests/CMakeFiles/Continuous
Continuous: tests/CMakeFiles/Continuous.dir/build.make
.PHONY : Continuous

# Rule to build all files generated by this target.
tests/CMakeFiles/Continuous.dir/build: Continuous
.PHONY : tests/CMakeFiles/Continuous.dir/build

tests/CMakeFiles/Continuous.dir/clean:
	cd /home/neil/Documents/cs4098/check/build/tests && $(CMAKE_COMMAND) -P CMakeFiles/Continuous.dir/cmake_clean.cmake
.PHONY : tests/CMakeFiles/Continuous.dir/clean

tests/CMakeFiles/Continuous.dir/depend:
	cd /home/neil/Documents/cs4098/check/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/neil/Documents/cs4098/check /home/neil/Documents/cs4098/check/tests /home/neil/Documents/cs4098/check/build /home/neil/Documents/cs4098/check/build/tests /home/neil/Documents/cs4098/check/build/tests/CMakeFiles/Continuous.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : tests/CMakeFiles/Continuous.dir/depend

