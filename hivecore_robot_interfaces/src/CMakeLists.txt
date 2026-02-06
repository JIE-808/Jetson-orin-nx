cmake_minimum_required(VERSION 3.8)
project(interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)

set(msg_files
  msg/PoseArrayClassAndID.msg
  msg/PoseClassAndID.msg
  msg/RobotWorkInfo.msg
  msg/DistMsg.msg
  msg/InputMsg.msg
  msg/ImuMsg.msg
  msg/ImgMsg.msg
  msg/MotorPos.msg
  msg/MotorCmd.msg
  msg/SkillCall.msg
  msg/MetaKey.msg
  msg/ArmMotionParams.msg
)
set(action_files
  action/MoveToPosition.action
  action/ArmSpaceControl.action
  action/HandControl.action
  action/LegControl.action
  action/VisionGraspObject.action
  action/SlamMode.action
  action/Arm.action
  action/DualArm.action
  action/CameraTakePhoto.action
  action/MoveHome.action
  action/MoveLeg.action
  action/MoveWaist.action
  action/MoveWheel.action
  action/ExecuteBtAction.action
  action/GripperCmd.action
)
set(srv_files
  srv/VisionObjectRecognition.srv
  srv/MapLoad.srv
  srv/MapSave.srv
  srv/BtRebuild.srv
  srv/MotorParam.srv
  srv/GripperCmd.srv
  srv/MotorInfo.srv
)

include_directories(include)
ament_export_include_directories(include)
install(DIRECTORY include/
  DESTINATION include/interfaces
)

# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
  ${action_files}
  ${srv_files}
  
  DEPENDENCIES
    std_msgs
    geometry_msgs
    sensor_msgs
    builtin_interfaces
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_export_dependencies(rosidl_default_runtime)
ament_package()
