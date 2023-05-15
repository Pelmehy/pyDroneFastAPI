from models.controls import Controls
from models.drone_info import Drone_info
from models.gps import Go_to_gps, Cur_gps


def get_drone_info(redis):
    drone_info_pk = redis.get('drone_info')
    if not drone_info_pk:
        return False

    return Drone_info.get(drone_info_pk)

def get_drone_cur_gps(redis):
    cur_drone_gps_pk = redis.get('cur_drone_gps')
    if not cur_drone_gps_pk:
        return False

    return Cur_gps.get(cur_drone_gps_pk)

def get_drone_go_to_gps(redis):
    drone_go_to_gps_pk = redis.get('drone_go_to_gps')
    if not drone_go_to_gps_pk:
        return False

    return Go_to_gps.get(drone_go_to_gps_pk)

def get_drone_controls(redis):
    drone_controls_pk = redis.get('drone_controls')
    if not drone_controls_pk:
        return False

    return Controls.get(drone_controls_pk)
