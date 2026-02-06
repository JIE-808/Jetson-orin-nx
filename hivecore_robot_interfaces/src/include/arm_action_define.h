#ifndef ARM_ACTION_DEFINE_H
#define ARM_ACTION_DEFINE_H

#include "err_code.h"

#define USED_ARM_DOF                (6)
#define GOAL_DATA_LENGTH            (7)
#define USED_OTHER_DOF              (17)

typedef enum {
    ARM_COMMAND_TYPE_ANGLE_STEP_ON = 0,
    ARM_COMMAND_TYPE_POSE_STEP_ON,
    ARM_COMMAND_TYPE_ANGLE_DIRECT_MOVE,
    ARM_COMMAND_TYPE_POSE_DIRECT_MOVE,
    ARM_COMMAND_TYPE_ERR
} ArmCommandTypeE;

typedef enum {
    POSE_POSITION_X = 0,
    POSE_POSITION_Y,
    POSE_POSITION_Z,
    POSE_QUATERNION_X,
    POSE_QUATERNION_Y,
    POSE_QUATERNION_Z,
    POSE_QUATERNION_W,
    POSE_DIMENSION, // should be 7
} PoseDimensionE;

typedef enum {
    LEFT_ARM = 0,
    RIGHT_ARM,
    ARM_ID_ERR
} ArmIdE;

#endif // ARM_ACTION_DEFINE_H