# CMake generated Testfile for 
# Source directory: /home/neil/Documents/cs4098/check
# Build directory: /home/neil/Documents/cs4098/check/build
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
ADD_TEST(check_check "/home/neil/Documents/cs4098/check/build/tests/check_check")
ADD_TEST(check_check_export "/home/neil/Documents/cs4098/check/build/tests/check_check_export")
ADD_TEST(test_output.sh "sh" "/home/neil/Documents/cs4098/check/tests/test_output.sh")
SET_TESTS_PROPERTIES(test_output.sh PROPERTIES  WORKING_DIRECTORY "/home/neil/Documents/cs4098/check/build/tests")
ADD_TEST(test_log_output.sh "sh" "/home/neil/Documents/cs4098/check/tests/test_log_output.sh")
SET_TESTS_PROPERTIES(test_log_output.sh PROPERTIES  WORKING_DIRECTORY "/home/neil/Documents/cs4098/check/build/tests")
ADD_TEST(test_xml_output.sh "sh" "/home/neil/Documents/cs4098/check/tests/test_xml_output.sh")
SET_TESTS_PROPERTIES(test_xml_output.sh PROPERTIES  WORKING_DIRECTORY "/home/neil/Documents/cs4098/check/build/tests")
ADD_TEST(test_tap_output.sh "sh" "/home/neil/Documents/cs4098/check/tests/test_tap_output.sh")
SET_TESTS_PROPERTIES(test_tap_output.sh PROPERTIES  WORKING_DIRECTORY "/home/neil/Documents/cs4098/check/build/tests")
ADD_TEST(test_check_nofork.sh "sh" "/home/neil/Documents/cs4098/check/tests/test_check_nofork.sh")
SET_TESTS_PROPERTIES(test_check_nofork.sh PROPERTIES  WORKING_DIRECTORY "/home/neil/Documents/cs4098/check/build/tests")
ADD_TEST(test_check_nofork_teardown.sh "sh" "/home/neil/Documents/cs4098/check/tests/test_check_nofork_teardown.sh")
SET_TESTS_PROPERTIES(test_check_nofork_teardown.sh PROPERTIES  WORKING_DIRECTORY "/home/neil/Documents/cs4098/check/build/tests")
SUBDIRS(lib)
SUBDIRS(src)
SUBDIRS(tests)
