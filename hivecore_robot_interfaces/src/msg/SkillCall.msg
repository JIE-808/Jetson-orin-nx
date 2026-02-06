# Generic skill call descriptor for ExecuteBtAction (scheme A)
string name           # Skill name, e.g., "MoveWaist" / "MoveLeg"
string interface_type # e.g., "interfaces/action/MoveWaist" or "interfaces/srv/VisionObjectRecognition"
string call_kind      # "action" | "srv"
string topic          # optional topic/service override; empty => use defaults/parameters
string payload_yaml   # YAML string of Goal/Request fields; may be empty for default goal
string instance_name  # optional instance name; empty => use default
int32 timeout_ms   # optional timeout; 0 => use default
