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

# Include any dependencies generated for this target.
include tests/CMakeFiles/check_nofork_teardown.dir/depend.make

# Include the progress variables for this target.
include tests/CMakeFiles/check_nofork_teardown.dir/progress.make

# Include the compile flags for this target's objects.
include tests/CMakeFiles/check_nofork_teardown.dir/flags.make

tests/CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.o: tests/CMakeFiles/check_nofork_teardown.dir/flags.make
tests/CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.o: ../tests/check_nofork_teardown.c
	$(CMAKE_COMMAND) -E cmake_progress_report /home/neil/Documents/cs4098/check/build/CMakeFiles $(CMAKE_PROGRESS_1)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building C object tests/CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.o"
	cd /home/neil/Documents/cs4098/check/build/tests && /usr/bin/cc  $(C_DEFINES) $(C_FLAGS) -o CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.o   -c /home/neil/Documents/cs4098/check/tests/check_nofork_teardown.c

tests/CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing C source to CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.i"
	cd /home/neil/Documents/cs4098/check/build/tests && /usr/bin/cc  $(C_DEFINES) $(C_FLAGS) -E /home/neil/Documents/cs4098/check/tests/check_nofork_teardown.c > CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.i

tests/CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling C source to assembly CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.s"
	cd /home/neil/Documents/cs4098/check/build/tests && /usr/bin/cc  $(C_DEFINES) $(C_FLAGS) -S /home/neil/Documents/cs4098/check/tests/check_nofork_teardown.c -o CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.s

tests/CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.o.requires:
.PHONY : tests/CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.o.requires

tests/CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.o.provides: tests/CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.o.requires
	$(MAKE) -f tests/CMakeFiles/check_nofork_teardown.dir/build.make tests/CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.o.provides.build
.PHONY : tests/CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.o.provides

tests/CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.o.provides.build: tests/CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.o

# Object files for target check_nofork_teardown
check_nofork_teardown_OBJECTS = \
"CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.o"

# External object files for target check_nofork_teardown
check_nofork_teardown_EXTERNAL_OBJECTS =

tests/check_nofork_teardown: tests/CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.o
tests/check_nofork_teardown: tests/CMakeFiles/check_nofork_teardown.dir/build.make
tests/check_nofork_teardown: src/libcheck.a
tests/check_nofork_teardown: lib/libcompat.a
tests/check_nofork_teardown: tests/CMakeFiles/check_nofork_teardown.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --red --bold "Linking C executable check_nofork_teardown"
	cd /home/neil/Documents/cs4098/check/build/tests && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/check_nofork_teardown.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
tests/CMakeFiles/check_nofork_teardown.dir/build: tests/check_nofork_teardown
.PHONY : tests/CMakeFiles/check_nofork_teardown.dir/build

tests/CMakeFiles/check_nofork_teardown.dir/requires: tests/CMakeFiles/check_nofork_teardown.dir/check_nofork_teardown.c.o.requires
.PHONY : tests/CMakeFiles/check_nofork_teardown.dir/requires

tests/CMakeFiles/check_nofork_teardown.dir/clean:
	cd /home/neil/Documents/cs4098/check/build/tests && $(CMAKE_COMMAND) -P CMakeFiles/check_nofork_teardown.dir/cmake_clean.cmake
.PHONY : tests/CMakeFiles/check_nofork_teardown.dir/clean

tests/CMakeFiles/check_nofork_teardown.dir/depend:
	cd /home/neil/Documents/cs4098/check/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/neil/Documents/cs4098/check /home/neil/Documents/cs4098/check/tests /home/neil/Documents/cs4098/check/build /home/neil/Documents/cs4098/check/build/tests /home/neil/Documents/cs4098/check/build/tests/CMakeFiles/check_nofork_teardown.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : tests/CMakeFiles/check_nofork_teardown.dir/depend

