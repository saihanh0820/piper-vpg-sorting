cmake_minimum_required(VERSION 3.0.2)
project(piper_vpg_ros)
find_package(catkin REQUIRED COMPONENTS rospy sensor_msgs std_msgs geometry_msgs)
catkin_package()
install(DIRECTORY ${PROJECT_SOURCE_DIR}/../config/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/config)
catkin_install_python(PROGRAMS
  scripts/sorting_manager_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})
