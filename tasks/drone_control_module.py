import sys
sys.path.insert(1, 'C:/forme/pyDrne/pyDroneFastApi')

from redis_om import get_redis_connection
from pydantic import ValidationError

from models.drone_info import Drone_info
from models.controls import Controls
from models.gps import Cur_gps, Go_to_gps

from helpers.dronekit import DroneControls

r = get_redis_connection(port=6379)

def controls_loop():
    drone_info = Drone_info(
        is_connected=0,
        arm=0,
        is_took_off=0,
        mode='GUIDED',
        app_mode='landing',
        ground_speed=0
    )
    drone_info.save()  # pk available inside model
    r.set('drone_info', drone_info.pk)

    drone_controls = Controls(
        vx=0.0,
        vy=0.0,
        vz=0.0,
        yaw=0.0
    )
    drone_controls.save()
    r.set('drone_controls', drone_controls.pk)

    drone_go_to_gps = Go_to_gps(
        go_to_lat=0.0,
        go_to_lon=0.0,
        go_to_alt=0.0
    )
    drone_go_to_gps.save()
    r.set('drone_go_to_gps', drone_go_to_gps.pk)

    drone = DroneControls()
    drone_info.is_connected = 1
    drone_info.save()

    gps = drone.get_gps_position()
    cur_drone_gps = Cur_gps(
        cur_lat=gps.lat,
        cur_lon=gps.lon,
        cur_alt=gps.alt
    )
    cur_drone_gps.save()
    r.set('cur_drone_gps', cur_drone_gps.pk)

    print('connected')

    while True:
        print('it works!')
        if not drone_info.is_connected:
            drone.disconnect()
            return
        drone_info = Drone_info.get(drone_info.pk)
        drone_controls = Controls.get(drone_controls.pk)
        drone_go_to_gps = Go_to_gps.get(drone_go_to_gps.pk)

        # drone control function
        drone.api_facade(drone_info, drone_controls, drone_go_to_gps)

        # set cur gps pos
        gps = drone.get_gps_position()

        cur_drone_gps.lat = gps.lat
        cur_drone_gps.lon = gps.lon
        cur_drone_gps.alt = gps.alt
        cur_drone_gps.save()

    r.execute_command('FLUSHALL')


if __name__ == '__main__':
    controls_loop()
