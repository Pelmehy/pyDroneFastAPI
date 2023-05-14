import time

import dronekit
import socket

import threading

from models.drone_info import Drone_info
from models.controls import Controls
from models.gps import Cur_gps, Go_to_gps


class DroneControls:
    # CONNECTION_STRING = 'COM3'
    CONNECTION_STRING = 'udp:127.0.0.1:14550'
    # BAUD_RATE = 57600
    BAUD_RATE = 115200

    vehicle = None
    drone_error = None

    mode_list = {
        'NA': None,
        'guided': 'GUIDED',
        'guided_nogps': 'GUIDED_NOGPS',
        'rtl': 'RTL'
    }

    app_mode_list = {
        'NA': None,
        'take_off': 'GUIDED',
        'go_to': 'GUIDED',
        'velocity': 'GUIDED',
        'velocity_nogps': 'GUIDED_NOGPS',
        'landing': 'RTL',
        'disconnect': 'RTL'
    }
    # mode = None
    mode = mode_list['guided']
    app_mode = app_mode_list['NA']
    # mode = "GUIDED_NOGPS"

    controls = {
        'vx': 0.0,
        'vy': 0.0,
        'vz': 0.0,
        'yaw': 0.0,
    }

    go_to_gps = {
        'lat': 0.0,
        'lon': 0.0,
        'alt': 0.0,
    }

    cur_gps_pos = {
        'lat': 0.0,
        'lon': 0.0,
        'alt': 0.0,
    }

    ground_speed = 0.0
    duration = 5

    arm = False
    is_connected = True
    is_took_off = False


    is_active = False
    is_changed = False

    app_error = {
        'is_error': False,
        'msg': None
    }

    def __init__(
            self,
            connection_string=None,
            baud_rate=None
    ):
        threading.Thread.__init__(self)

        if connection_string:
            self.CONNECTION_STRING = connection_string

        if baud_rate:
            self.BAUD_RATE = baud_rate

        print(self.CONNECTION_STRING)
        print(self.BAUD_RATE)

        self.connect()

    def __del__(self):
        self.disconnect()
        print('disconnected')

    def success(self):
        self.app_error['is_error'] = False
        return self.app_error

    def error(self, msg):
        self.app_error['is_error'] = True
        self.app_error['msg'] = msg

    def is_error(self):
        return self.app_error['is_error']

    def send_controls(self):
        if not self.controls['is_took_off'] and not self.controls['simple_takeoff']:
            return
        elif not self.controls['is_took_off'] and self.controls['simple_takeoff']:
            self.arm_and_takeoff(5)
            self.set_controls('is_took_off', True)
            self.set_controls('simple_takeoff', False)
        elif self.is_armed and not self.arm:
            self.vehicle.mode = self.mode_list['rtl']
            self.set_controls('is_took_off', False)

            return

        if self.controls['is_velocity_mode']:
            self.send_velocity(self.controls['vx'], self.controls['vy'], self.controls['vz'], self.duration)

            if self.controls['yaw'] != 0:
                self.condition_yaw(self.controls['yaw'])
                self.set_controls('yaw')
        elif self.go_to_gps['is_go_to_mode']:
            # TODO add goto function
            print('in dev')
        return

    def temp_terminal(self):
        command = 0

        while True:
            print(
                '1:\tget position',
                '2:\tget ground speed',
                '3:\tarm',
                '4:\tdisarm',
                '5:\tchange controls',
                '6\tsimple takeoff',
                '0:\tdisconnect',
                sep='\n'
            )
            print('enter command: ')
            command = int(input())

            if command == 0:
                self.is_active = False
                return
            elif command == 1:
                position = self.get_gps_position()
                print('position:', position)
            elif command == 2:
                motor_sped = self.get_ground_speed()
                print('ground speed:', motor_sped)
            elif command == 3:
                self.set_arm(True)
                print('armed')
            elif command == 4:
                self.set_arm(False)
                print('disarmed')
            elif command == 5:
                self.is_active = True
                self.control_thread()
            elif command == 6:
                self.arm_and_takeoff(20)

            self.is_changed = True

    def controls_facade_terminal(self):
        print('vx: ', self.controls['vx'])
        print('vy: ', self.controls['vy'])
        print('vz: ', self.controls['vz'])
        print('yaw: ', self.controls['yaw'], end='\n\n')

        while True:
            if 'stop' in self.controls:
                return

            print('sending command...')

            self.send_velocity(self.controls['vx'], self.controls['vy'], self.controls['vz'], self.duration)

            if self.controls['yaw'] != 0:
                self.condition_yaw(self.controls['yaw'])
                self.set_controls('yaw')

            print('command sent')
            self.is_changed = False

            time.sleep(1)

    def controls_facade(self):
        if self.app_mode == 'NA':
            return self.error(
                'invalid app mode\n please use one of supported:\n take_off\ngo_to\nvelocity\nlanding\ndisconnect'
            )
        elif self.app_mode == 'go_to':
            # add goto function
            print('in dev')
        elif self.app_mode == 'velocity':
            self.send_velocity(self.controls['vx'], self.controls['vy'], self.controls['vz'], self.duration)
            if self.controls['yaw'] != 0:
                self.condition_yaw(self.controls['yaw'])
                self.set_controls('yaw')
        elif self.app_mode == 'landing':
            self.return_to_landing_pad()
            self.is_took_off = False
            self.is_took_off = False
        elif self.app_mode == 'take_off' and not self.is_took_off:
            self.arm_and_takeoff(5)
            self.is_took_off = True
        elif self.app_mode == 'disconnect':
            self.return_to_landing_pad()
            self.is_connected = False

        return True

    def update_settings(self):
        self.set_cur_gps(self.get_gps_position())
        self.ground_speed = self.get_ground_speed()

    def get_info(self):
        return {
            'is_connected': self.is_connected,
            'arm': self.arm,
            'is_took_off': self.is_took_off,
            'ground_speed': self.ground_speed
        }

    def get_cur_gps(self):
        return self.cur_gps_pos

    def api_facade(
            self,
            info: Drone_info,
            controls: Controls,
            go_to_gps: Go_to_gps
    ):
        self.set_api(controls, go_to_gps, info)
        if self.is_error():
            return self.app_error

        self.controls_facade()
        if self.is_error():
            return self.app_error

        self.update_settings()



    def control_thread(self):
        thread_terminal = threading.Thread(target=self.terminal_input_facade)
        thread_controls = threading.Thread(target=self.controls_facade_terminal)

        thread_controls.setDaemon(True)

        thread_terminal.start()
        thread_controls.start()

        thread_terminal.join()

    def terminal_input_facade(self):
        while True:
            print('vx: ', self.controls['vx'])
            print('vy: ', self.controls['vy'])
            print('vz: ', self.controls['vz'])
            print('yaw: ', self.controls['yaw'], end='\n\n')

            print(
                'enter command:',
                '1:\tset x speed',
                '2:\tset y speed',
                '3:\tset z speed',
                '4:\tset yaw',
                '0:\texit',
                sep='\n'
            )
            print('enter command: ')
            command = int(input())

            if command == 0:
                return
            elif command == 1:
                print('enter x velocity: ')
                velocity = int(input())

                self.set_controls('vx', velocity)

                print('x velocity = ', velocity)
            elif command == 2:
                print('enter y velocity: ')
                velocity = int(input())

                self.set_controls('vy', velocity)

                print('y velocity = ', velocity)
            elif command == 3:
                print('enter z velocity: ')
                velocity = int(input())

                self.set_controls('vz', velocity)

                print('z velocity = ', velocity)
            elif command == 4:
                print('enter yaw: ')
                yaw = int(input())

                self.set_controls('yaw', yaw)

                print('yaw = ', yaw)

    def connect(self):
        try:
            self.vehicle = dronekit.connect(self.CONNECTION_STRING, wait_ready=False, baud=self.BAUD_RATE)
            self.vehicle.wait_ready(True, raise_exception=False)

            if self.mode:
                self.vehicle.mode = dronekit.VehicleMode(self.mode)

        # Bad TCP connection
        except socket.error:
            self.drone_error = 'No server exists!'

        # API Error
        except dronekit.APIException:
            self.drone_error = 'Timeout!'

        # Other error
        except:
            self.drone_error = 'Some other error!'

    def disconnect(self):
        self.vehicle.close()

    def check_connection(self):
        if not bool(self.vehicle):
            raise ValueError(self.drone_error)

    def get_gps_position(self):
        self.check_connection()

        return self.vehicle.location.global_relative_frame

    def get_ground_speed(self):
        return self.vehicle.groundspeed

    def set_arm(self, is_arm: bool):
        self.arm = is_arm

    # **************************
    # speed and height control
    # **************************
    def condition_yaw(self, heading, relative=True):
        if relative:
            is_relative = 1  # yaw relative to direction of travel
        else:
            is_relative = 0  # yaw is an absolute angle
        # create the CONDITION_YAW command using command_long_encode()
        msg = self.vehicle.message_factory.command_long_encode(
            0, 0,  # target system, target component
            dronekit.mavutil.mavlink.MAV_CMD_CONDITION_YAW,  # command
            0,  # confirmation
            heading,  # param 1, yaw in degrees
            0,  # param 2, yaw speed deg/s
            1,  # param 3, direction -1 ccw, 1 cw
            is_relative,  # param 4, relative offset 1, absolute angle 0
            0, 0, 0  # param 5 ~ 7 not used
        )
        # send command to vehicle
        self.vehicle.send_mavlink(msg)

    def send_velocity(self, velocity_x, velocity_y, velocity_z, duration):
        """
        Move vehicle in direction based on specified velocity vectors.
        """
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,  # time_boot_ms (not used)
            0, 0,  # target system, target component
            dronekit.mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # frame
            0b0000111111000111,  # type_mask (only speeds enabled)
            0, 0, 0,  # x, y, z positions (not used)
            velocity_x, velocity_y, velocity_z,  # x, y, z velocity in m/s
            0, 0, 0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
        )

        # send command to vehicle on 1 Hz cycle
        for x in range(0, duration):
            self.vehicle.send_mavlink(msg)
            time.sleep(1)

    def set_controls(self, control_name, value=0.0):
        self.controls[control_name] = value

    def set_velocity(self, controls: Controls):
        self.controls['vx'] = controls.vx
        self.controls['vy'] = controls.vy
        self.controls['vz'] = controls.vz
        self.controls['yaw'] = controls.yaw

    def set_go_to(self, gps: Go_to_gps):
        self.go_to_gps['lat'] = gps.go_to_lat
        self.go_to_gps['lot'] = gps.go_to_lon
        self.go_to_gps['alt'] = gps.go_to_alt

    def set_cur_gps(self, gps):
        self.cur_gps_pos['lat'] = gps.lat
        self.cur_gps_pos['lon'] = gps.lon
        self.cur_gps_pos['alt'] = gps.alt

    def set_info(self, info: Drone_info):
        print(info.app_mode)
        if info.app_mode in self.app_mode_list:
            self.mode = self.app_mode_list[info.app_mode]

    def set_api(
            self,
            controls: Controls,
            gps: Go_to_gps,
            info: Drone_info
    ):
        self.set_velocity(controls)
        self.set_go_to(gps)
        self.set_info(info)

    def arm_and_takeoff(self, aTargetAltitude):
        """
        Arms vehicle and fly to aTargetAltitude.
        """

        print("Arming motors")
        # Copter should arm in GUIDED mode
        self.vehicle.mode = dronekit.VehicleMode("GUIDED")
        self.vehicle.armed = True

        # Confirm vehicle armed before attempting to take off
        while not self.vehicle.armed:
            print(" Waiting for arming...")
            time.sleep(1)

        print("Taking off!")
        self.vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
        #  after self.vehicle.simple_takeoff will execute immediately).
        while True:
            print(" Altitude: ", self.vehicle.location.global_relative_frame.alt)
            # Break and return from function just below target altitude.
            if self.vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
                print("Reached target altitude")
                break
            time.sleep(1)

        self.is_took_off = True

    def return_to_landing_pad(self):
        self.vehicle.mode = dronekit.VehicleMode(self.app_mode_list[self.app_mode])
