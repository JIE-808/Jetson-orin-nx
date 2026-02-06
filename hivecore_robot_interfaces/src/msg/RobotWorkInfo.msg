int64     msg_id
string    working_state        #[Standby, Working, Fault]
int8      battery_capacity     #[0-100]
float32   working_time         #1.5 (h)
string    nav_state            #[Normal, Fault]
string    comm_quality         #[Excellent, Good, Fair, Poor, NoSignal]
string[]  task                 #[last_task, next_task, current_task], [StockIn, StockOut, None]
string    expt_completion_time ##2025-11-11 12:34:56
string    work_log             #
string    skill                #MoveWaist
string    action_name          #s1_waist_bend_down
string    instance_params      #
string    bt_node_status       #[IDLE, RUNNING, SUCCESS, FAILURE, SKIPPED]
string    smacc_state          #[StIdle, StExecuting, StCompleted, StFailed, StEmergency]