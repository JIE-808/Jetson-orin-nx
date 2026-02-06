#ifndef ERR_CODE_H
#define ERR_CODE_H

typedef enum {
    OK = 0,
    UNKNOWN_ERR = -1,
    ARM_NOW_FORCE_MOVING = -2,
    ARM_COLLISION = -3,
    ARM_AIM_CANNOT_REACH = -4,
    ARM_NOW_NO_GOAL = -5,
    ARM_GOAL_CANCELLED = -6,
} ErrCodeE;

#endif // ERR_CODE_H