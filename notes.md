# Backyard Flyer

Udacity FCND Project 1

## TODO

1. ~Peruse~ [udacidrone](https://udacity.github.io/udacidrone/docs/getting-started.html) ~documentation.~ Includes:  
   1. [Drone](https://udacity.github.io/udacidrone/docs/drone-api.html). In particular, [drone attributes](https://udacity.github.io/udacidrone/docs/drone-attributes.html).  
      1. _Question: If the `Drone` class does not contain an autopilot, is the "autopilot" in the simulator?_  
         1. The first clue is that the last project, Estimation, in which a EKF/UKF is written, does not have a simulator project. The drone has medium-level commands like `cmd_velocity`, `cmd_attitude`, `cmd_attitude_rate`, and `cmd_moment`, which may or may not be used in the implementation of an autopilot. _Question: If the filter is going to be written in C++, how is the Python `Drone` class going to be used?_    
         2. The second clue is that the `Drone` class is said to be a _pass-through_ (to the "drone", which can be either a real physical drone with its own autopilot, e.g. PX4, or the simulated drone).  
   2. [Connection](https://udacity.github.io/udacidrone/docs/connection-api.html).  
   3. Plotting data with [visdom](https://github.com/fossasia/visdom) (for later).  
2. ~Peruse the [project](https://github.com/ivogeorg/FCND-Backyard-Flyer/blob/main/README.md) and [official solution](https://github.com/udacity/FCND-Backyard-Flyer/blob/solution/README.md) READMEs.~  
3. Drone messages:  
   1. [`MsgID`](https://github.com/udacity/udacidrone/blob/master/udacidrone/messaging/message_ids.py) is an `enum` type in `udacidrone`. 
   2. The [`Drone`](https://github.com/udacity/udacidrone/blob/master/udacidrone/drone.py) class listens to all the messages on its `connection`.  
   3. Some of the messages are drone state and some are commands. Here is an exerpt from the log:
      ```
      MsgID.GLOBAL_POSITION,0.0000000,-122.3957515,37.7932820,-0.0810000
      MsgID.LOCAL_VELOCITY,0.0000000,0.0000000,0.0000000,0.0000000
      MsgID.LOCAL_POSITION,14.7560000,0.0222482,0.0019454,0.0817012
      MsgID.LOCAL_VELOCITY,14.7560000,0.0000000,0.0000000,-0.0000000
      MsgID.STATE,0.0000000,False,False,1
      MsgID.GLOBAL_HOME,0.0000000,-122.3957515,37.7932818,0.0000000
      MsgID.GLOBAL_POSITION,0.0000000,-122.3957515,37.7932822,-0.0960000
      MsgID.LOCAL_VELOCITY,0.0000000,0.0000000,0.0000000,0.0000000
      MsgID.LOCAL_POSITION,15.0060000,0.0458288,0.0014901,0.0963706
      MsgID.LOCAL_VELOCITY,15.0060000,0.0000000,0.0000000,-0.0000000
      MsgID.GLOBAL_POSITION,0.0000000,-122.3957515,37.7932823,-0.0980000
      MsgID.LOCAL_VELOCITY,0.0000000,0.0000000,0.0000000,0.0000000
      MsgID.LOCAL_POSITION,15.2560000,0.0598115,0.0017799,0.0981233
      MsgID.LOCAL_VELOCITY,15.2560000,0.0000000,0.0000000,-0.0000000
      MsgID.GLOBAL_POSITION,0.0000000,-122.3957515,37.7932818,-0.0860000
      MsgID.LOCAL_VELOCITY,0.0000000,0.0000000,0.0000000,0.0000000
      MsgID.LOCAL_POSITION,15.5060000,-0.0018820,0.0009520,0.0867058
      MsgID.LOCAL_VELOCITY,15.5060000,0.0000000,0.0000000,-0.0000000
      MsgID.GLOBAL_POSITION,0.0000000,-122.3957527,37.7932826,-0.0630000
      MsgID.LOCAL_VELOCITY,0.0000000,0.0000000,0.0000000,0.0000000
      MsgID.LOCAL_POSITION,15.7560000,0.0945615,-0.1092026,0.0639517
      MsgID.LOCAL_VELOCITY,15.7560000,0.0000000,0.0000000,-0.0000000
      MsgID.STATE,0.0000000,False,False,1   
      ```
   4. See [message_types](https://github.com/udacity/udacidrone/blob/master/udacidrone/connection/message_types.py) (used by `MavlinkConnection`).
   5. The 4 messages that seem to be used most often are:
      1. `MsgID.GLOBAL_POSITION`.  
      2. `MsgID.LOCAL_POSITION`.  
      2. `MsgID.LOCAL_VELOCITY`.  
      2. `MsgID.LOCAL_STATE`.  
   6. Of these, all but `MsgID.GLOBAL_POSITION` has a handler callback in `BackyardFlyer`.    
   7. To understand what messages are sent when, look at the logs for: 
      1. `UpAndDownFlyer` in _guided_ mode. The telemetry log (`Logs/TLog.txt`) contains:
         | Msg | Count | Zero time |
         | --- | --- | --- |
         | LOCAL_VELOCITY | 66 | 33 |
         | GLOBAL_POSITION | 33 | 33 |
         | LOCAL_POSITION | 33 | 0 |
         | STATE | 8 | 8 |
         | GLOBAL_HOME | 8 | 8 |

      2. Manual drone flying of the `BackyardFlyer` trajectory! **Not logged :(**      
4. Load up on [MAVLink](https://mavlink.io/en/), including the [pymavlink](https://mavlink.io/en/mavgen_python/) ([library](https://pypi.org/project/pymavlink/)).  
   1. The abstract class [`Connection`](https://github.com/udacity/udacidrone/blob/master/udacidrone/connection/connection.py) has protocol-specific subclasses. The class is declared _abstract_ as follows:
      ```python
      from abc import ABCMeta, abstractmethod

      class Connection(object):
          __metaclass__ = ABCMeta
      ```
   2. The [`MavlinkConnection`](https://github.com/udacity/udacidrone/blob/master/udacidrone/connection/mavlink_connection.py) is the MAVLink-specific subclass.  
   3. The [mavlink_utils](https://github.com/udacity/udacidrone/blob/master/udacidrone/connection/mavlink_utils.py) are interesting.  
      1. In `dispatch_message` the used MAVLink [common](https://mavlink.io/en/messages/common.html) messages are translated and passed to the `Drone` listeners.  
      2. The commands from `Drone` are translated to MAVLink messages in the `MavlinkConnection`.  
   4. _Question: If I cannot find a low-level method, e.g. `set_position_target_local_ned_encode`, which is used by many methods in `MavlinkConnection` to set up the message for `send_message`, does it mean it is autogenerated? If yes, what is the workflow?_~  
      1. Read the `mavgen` [documentation](https://mavlink.io/en/mavgen_python/).  
      2. Understand the place of `mavlink_connecion.py` in the workflow.  
         1. `self._master` is a connection returned by `mavutil`: `self._master = mavutil.mavlink_connection(device)`. It has `port`, `mav`, and `recv_match`.  
         2. The function under discussion is called as follows, usu. in a `cmd_*` function:
            ```python
            msg = self._master.mav.set_attitude_target_encode(...)
            self.send_message(msg)   
            ```  
         3. The questions is where does it come from! :D  
      3. Understand the structure of the `pymavlink` [library](https://github.com/ArduPilot/pymavlink), which is used _as a submodule_ by [MAVLink/mavlink](https://github.com/mavlink/mavlink). _(PyPi takes the ArduPilot fork.)_      
      4. There is a [SET_POSITION_TARGET_LOCAL_NED](https://mavlink.io/en/messages/common.html#MAV_PROTOCOL_CAPABILITY_SET_POSITION_TARGET_LOCAL_NED) message in the common set of MAVLink.  
      5. Using MAVLink 2.0. In `mavlink_connection.py`:
         ```python
         # force use of mavlink v2.0
         os.environ['MAVLINK20'] = '1'
         ```
   5. Link from mentor on [Communicating with Raspberry Pi via MAVLink](https://ardupilot.org/dev/docs/raspberry-pi-via-mavlink.html).
5. Coordinate systems:
   1. Figuring out _global_ vs _local_ coordinates.  
      1. Check out [frame_utils](https://github.com/udacity/udacidrone/blob/master/udacidrone/frame_utils.py).  
      2. From the documentation:
         > Two different reference frames are defined and used within the `Drone` API. Global positions are defined as [longitude, latitude, altitude (positive **up**)]. Local reference frames are defined [North, East, Down (positive **down**)] and is relative to a nearby global home provided. Both reference frames are defined in a proper **right-handed** reference frame. The global reference frame is what is provided by the Drone's GPS. Two convenience functions, `global_to_local()` and `local_to_global()` are provided within the `frame_utils.py` script to convert between the two frames. These functions are wrappers on [`utm`](https://github.com/Turbo87/utm) library functions.
   2. Figuring out coordinate systems, especially vertical coordinate `z`, and two-way transformations.  
6. State diagram, including:  
   1. Automatic state changes (sequential).  
   2. Callback state changes due to received messages.    
7. ~Extras:~  
   1. Two modes of flying in a square:  
      1. F-L-B-R.  
      2. F-LT-F-LT-F-LT-F-LT. Note that `Drone.cmd_position()` includes _heading_ as the last parameter. Heading is in _radians_.      
   2. Randomize square side.  
   3. Randomize CW-CCW.  
   4. Randomize elevation (more difficult).  
   5. Visit the square waypoints at maximum speed, effectively in a circle with virage (very difficult w/o a controller).