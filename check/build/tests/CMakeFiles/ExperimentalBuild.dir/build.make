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

# Utility rule file for ExperimentalBuild.

# Include the progress variables for this target.
include tests/CMakeFiles/ExperimentalBuild.dir/progress.make

tests/CMakeFiles/ExperimentalBuild:
	cd /home/neil/Documents/cs4098/check/build/tests && /usr/bin/ctest -D ExperimentalBuild

ExperimentalBuild: tests/CMakeFiles/ExperimentalBuild
ExperimentalBuild: tests/CMakeFiles/ExperimentalBuild.dir/build.make
.PHONY : ExperimentalBuild

# Rule to build all files generated by this target.
tests/CMakeFiles/ExperimentalBuild.dir/build: ExperimentalBuild
.PHONY : tests/CMakeFiles/ExperimentalBuild.dir/build

tests/CMakeFiles/ExperimentalBuild.dir/clean:
	cd /home/neil/Documents/cs4098/check/build/tests && $(CMAKE_COMMAND) -P CMakeFiles/ExperimentalBuild.dir/cmake_clean.cmake
.PHONY : tests/CMakeFiles/ExperimentalBuild.dir/clean

tests/CMakeFiles/ExperimentalBuild.dir/depend:
	cd /home/neil/Documents/cs4098/check/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/neil/Documents/cs4098/check /home/neil/Documents/cs4098/check/tests /home/neil/Documents/cs4098/check/build /home/neil/Documents/cs4098/check/build/tests /home/neil/Documents/cs4098/check/build/tests/CMakeFiles/ExperimentalBuild.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : tests/CMakeFiles/ExperimentalBuild.dir/depend

