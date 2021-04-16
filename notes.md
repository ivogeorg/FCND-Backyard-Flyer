# Backyard Flyer

Udacity FCND Project 1

## TODO

1. Peruse [udacidrone](https://udacity.github.io/udacidrone/docs/getting-started.html) documentation. Includes:  
   1. [Drone](https://udacity.github.io/udacidrone/docs/drone-api.html). In particular, [drone attributes](https://udacity.github.io/udacidrone/docs/drone-attributes.html).  
   2. [Connection](https://udacity.github.io/udacidrone/docs/connection-api.html).  
   3. Plotting data with [visdom](https://github.com/fossasia/visdom).  
2. Peruse the [project](https://github.com/ivogeorg/FCND-Backyard-Flyer/blob/main/README.md) and [official solution](https://github.com/udacity/FCND-Backyard-Flyer/blob/solution/README.md) READMEs.  
3. Drone messages:  
   1. [`MsgID`](https://github.com/udacity/udacidrone/blob/master/udacidrone/messaging/message_ids.py) is an `enum` type in `udacidrone`. 
   2. The [`Drone`](https://github.com/udacity/udacidrone/blob/master/udacidrone/drone.py) class listens to all the messages on its `connection`.  
   3. Some of the messages are drone state and some are commands.   
   4. See [message_types](https://github.com/udacity/udacidrone/blob/master/udacidrone/connection/message_types.py) (used by `MavlinkConnection`).  
4. Load up on [MAVLink](https://mavlink.io/en/), including the [pymavlink](https://mavlink.io/en/mavgen_python/) ([library](https://pypi.org/project/pymavlink/)).  
   1. The abstract class [`Connection`](https://github.com/udacity/udacidrone/blob/master/udacidrone/connection/connection.py) has a protocol-specific subclasses.  
   2. The [`MavlinkConnection`](https://github.com/udacity/udacidrone/blob/master/udacidrone/connection/mavlink_connection.py) is the MAVLink-specific subclass.  
   3. The [mavlink_utils](https://github.com/udacity/udacidrone/blob/master/udacidrone/connection/mavlink_utils.py) are interesting.  
5. State diagram, including:  
   1. Automatic state changes (sequential).  
   2. Callback state changes due to received messages.    