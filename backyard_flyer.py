import argparse
import time
from enum import Enum

import numpy as np

from udacidrone import Drone
from udacidrone.connection import MavlinkConnection, WebSocketConnection  # noqa: F401
from udacidrone.messaging import MsgID


class States(Enum):
    MANUAL = 0
    ARMING = 1
    TAKEOFF = 2
    WAYPOINT = 3
    LANDING = 4
    DISARMING = 5


class BackyardFlyer(Drone):

    def __init__(self, connection, altitude, side):
        super().__init__(connection)
        self.target_position = np.array([0.0, 0.0, 0.0])
        self.altitude = altitude
        self.side = side
        self.all_waypoints = []
        self.in_mission = True
        self.check_state = {}

        # initial state
        self.flight_state = States.MANUAL

        # TODO: Register all your callbacks here
        self.register_callback(MsgID.LOCAL_POSITION, self.local_position_callback)
        self.register_callback(MsgID.LOCAL_VELOCITY, self.velocity_callback)
        self.register_callback(MsgID.STATE, self.state_callback)

    def waypoint_reached(self, index):
        return (abs(self.local_position[0]-self.all_waypoints[index][0]) < 0.05 and
                abs(self.local_position[1]-self.all_waypoints[index][1]) < 0.05 and
                abs(self.local_position[2]-self.all_waypoints[index][2]) < 0.05)
    

    def local_position_callback(self):
        """
        TODO: Implement waypoints (3m height, 10m square side)

        This triggers when `MsgID.LOCAL_POSITION` is received and self.local_position contains new data
        """
        # TODO (BackyardFlyer):
        # if state is TAKEOFF:
        #     If takeoff argument altitude reached:
        #         call waypoint_transition
        # elif state is WAYPOINT:
        #     If all_waypoints[0] waypoint reached:
        #         remove first element of all_waypoints
        #         if more waypoints:
        #             command to all_waypoints[0]
        #         else
        #             call landing_transition
        if self.flight_state == States.TAKEOFF:

            current_altitude = -1.0 * self.local_position[2]
            if abs(current_altitude - self.altitude) < 0.05:
                self.waypoint_transition()

        elif self.flight_state == States.WAYPOINT:

            if self.waypoint_reached(0):  # the next is always first since reached are deleted

                self.all_waypoints.pop(0)

                if len(self.all_waypoints) > 0:

                    self.cmd_position(self.all_waypoints[0][0],
                                      self.all_waypoints[0][1],
                                      -self.all_waypoints[0][2],
                                      0.0)  # TODO: extra w/ yaw=-pi/2

                else:
                    
                    self.landing_transition()

        # if self.flight_state == States.TAKEOFF:

        #     # convert from local NED to global
        #     # Note: NED vetical component points down
        #     altitude = -1.0 * self.local_position[2]

        #     if altitude > 0.95 * self.target_position[2]:
        #         self.landing_transition()

        #     # TODO: target is 0,0,0, so change test to wpt[0]
        #     # if altitude > 0.95 * self.target_position[2]:
        #     #     self.waypoint_transition()

        # # elif self.flight_state == States.WAYPOINT:
        # #     pass
        #     # What messages are called during flight around square?


    def velocity_callback(self):
        """
        This triggers when `MsgID.LOCAL_VELOCITY` is received and self.local_velocity contains new data
        """
        if self.flight_state == States.LANDING:
            if ((self.global_position[2] - self.global_home[2] < 0.1) and
                abs(self.local_position[2]) < 0.01):
                self.disarming_transition()


    def state_callback(self):
        """
        This triggers when `MsgID.STATE` is received and self.armed and self.guided contain new data
        """
        if not self.in_mission:
            return

        if self.flight_state == States.MANUAL:
            self.arming_transition()
        elif self.flight_state == States.ARMING:
            if self._armed:
                self.takeoff_transition()
        elif self.flight_state == States.DISARMING:
            if not self._armed:
                self.manual_transition()

    def calculate_box(self):
        """TODO: Fill out this method
        
        1. Call from waypoint_transition.
        2. Use current local position as origin.
        3. Use self.side to compute box.
        4. 4 points, last one is origin.
        5. Set self.all_waypoints.
        """
        n0 = self.local_position[0]
        e0 = self.local_position[1]
        d0 = self.local_position[2]
        self.all_waypoints = [(n0 + self.side, e0, d0),
                              (n0 + self.side, e0 + self.side, d0),
                              (n0, e0 + self.side, d0),
                              (n0, e0, d0)]

    def arming_transition(self):
        """
        1. Take control of the drone
        2. Pass an arming command
        3. Set the home location to current position
        4. Transition to the ARMING state
        """
        print("arming transition")
        self.take_control()
        self.arm()

        # set current global location to be (global) home
        self.set_home_position(self.global_position[0],
                               self.global_position[1],
                               self.global_position[2])
        self.flight_state = States.ARMING

    def takeoff_transition(self):
        """
        1. Set target_position altitude to 3.0m
        2. Command a takeoff to 3.0m
        3. Transition to the TAKEOFF state
        """
        print("takeoff transition")
        target_altitude = self.altitude
        self.target_position[2] = target_altitude
        self.takeoff(target_altitude)
        self.flight_state = States.TAKEOFF

    def waypoint_transition(self):
        """
        1. Calculate box relative to local position.
        2. Command the next waypoint position w/ cmd_position
        3. cmd_position is in NED
        4. Transition to WAYPOINT state
        """
        print("waypoint transition")
        self.calculate_box()
        self.cmd_position(self.all_waypoints[0][0],
                          self.all_waypoints[0][1],
                          -self.all_waypoints[0][2],
                          0.0)  # TODO: extra w/ yaw=-pi/2
        self.flight_state = States.WAYPOINT

    def landing_transition(self):
        """
        1. Command the drone to land
        2. Transition to the LANDING state
        """
        print("landing transition")
        self.land()
        self.flight_state = States.LANDING

    def disarming_transition(self):
        """
        1. Command the drone to disarm
        2. Transition to the DISARMING state
        """
        print("disarm transition")
        self.disarm()
        self.flight_state = States.DISARMING

    def manual_transition(self):
        """This method is provided
        
        1. Release control of the drone
        2. Stop the connection (and telemetry log)
        3. End the mission
        4. Transition to the MANUAL state
        """
        print("manual transition")

        self.release_control()
        self.stop()
        self.in_mission = False
        self.flight_state = States.MANUAL

    def start(self):
        """This method is provided
        
        1. Open a log file
        2. Start the drone connection
        3. Close the log file
        """
        print("Creating log file")
        self.start_log("Logs", "NavLog.txt")
        print("starting connection")
        self.connection.start()
        print("Closing log file")
        self.stop_log()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5760, help='Port number')
    parser.add_argument('--host', type=str, default='127.0.0.1', help="host address, i.e. '127.0.0.1'")
    parser.add_argument('--altitude', type=int, default=3, help='Altitude of trajectory')
    parser.add_argument('--side', type=int, default=10, help='Side of square trajectory')
    args = parser.parse_args()

    conn = MavlinkConnection('tcp:{0}:{1}'.format(args.host, args.port), threaded=False, PX4=False)
    #conn = WebSocketConnection('ws://{0}:{1}'.format(args.host, args.port))
    drone = BackyardFlyer(conn, args.altitude, args.side)
    time.sleep(2)
    drone.start()
