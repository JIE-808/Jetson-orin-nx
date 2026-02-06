# ArmMotionParams.msg - 单臂运动参数

uint8 MOVEJ = 0
uint8 MOVEL = 1

uint8 ARM_LEFT = 0
uint8 ARM_RIGHT = 1

uint8 arm_id                  # 机械臂ID 0: 左臂, 1: 右臂
uint8 motion_type             # 运动模式: MOVEJ / MOVEL
geometry_msgs/Pose target_pose    # 笛卡尔目标位姿 (仅 MOVEL 使用)
float64[] target_joints           # 目标关节角(rad) (仅 MOVEJ 使用)

