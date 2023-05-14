import sys

sys.path.insert(1, 'C:/forme/pyDrne/pyDroneFastApi')

from redis import Redis
from redis_om import HashModel
from pydantic import ValidationError

from models.drone_info import Drone_info
from models.controls import Controls
from models.gps import Cur_gps, Go_to_gps

from helpers.dronekit import DroneControls


def controls_loop():
    try:
        drone_info = Drone_info(
            is_connected=False,
            arm=False,
            is_took_off=False,
            mode='GUIDED',
            app_mode='landing',
            ground_speed=0
        )
        drone_info.save()  # pk available inside model

        drone_controls = Controls(
            vx=0.0,
            vy=0.0,
            vz=0.0,
            yaw=0.0
        )
        drone_controls.save()

        drone_go_to_gps = Go_to_gps(
            go_to_lat=0.0,
            go_to_lon=0.0,
            go_to_alt=0.0
        )

        drone = DroneControls()
        drone_info.is_connected = True
        drone_info.save()

        gps = drone.get_gps_position()
        cur_drone_gps = Cur_gps(
            cur_lat=gps.gps.lat,
            cur_lon=gps.gps.lon,
            cur_alt=gps.gps.alt
        )
        cur_drone_gps.save()
    except ValidationError as e:
        print(e)

    while True:
        if not drone_info.is_connected:
            drone.disconnect()
            return

        drone_info = Drone_info.get(drone_info.pk)
        drone_controls = Controls.get(drone_controls.pk)
        drone_go_to_gps = Go_to_gps.get(drone_go_to_gps.pk)

        # TODO set control and get gps pos

        # set cur gps pos
        gps = drone.get_gps_position()

        cur_drone_gps.lat = gps.gps.lat
        cur_drone_gps.lon = gps.gps.lon
        cur_drone_gps.alt = gps.gps.alt
        cur_drone_gps.save()


if __name__ == '__main__':
    controls_loop()
