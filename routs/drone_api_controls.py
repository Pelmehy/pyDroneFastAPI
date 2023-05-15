import sys
import tracemalloc
from fastapi import APIRouter
from redis_om import get_redis_connection
import subprocess
from fastapi import BackgroundTasks
import asyncio

from helpers.dronekit import DroneControls
import helpers.redis_helper as redis_helper

from models.controls import Controls
from models.drone_info import Drone_info
from models.gps import Go_to_gps, Cur_gps

tracemalloc.start()
r = get_redis_connection(port=6379)

router = APIRouter(
    prefix='/controls',
    tags=["Drone controls"]
)


@router.post('/connect')
async def connect():
    print('start')

    p = subprocess.Popen(
        [
            sys.executable,
            'tasks/drone_control_module.py'
        ],
        shell=True,
        stdin=None,
        stdout=None,
        stderr=None,
        close_fds=True
    )

    print('end')
    return {'status': 'success'}


@router.post('/disconnect')
async def disconnect():
    drone_info = redis_helper.get_drone_info(r)
    if not drone_info:
        return {'status': 'drone not connected'}

    drone_info.is_connected = 0
    drone_info.save()

    return {'status': 'success'}
    



@router.post('/x_speed/{velocity}')
async def set_x_speed(velocity: float):
    if velocity > 20:
        return 'max speed 20 m/s'

    drone_controls_pk = r.get('drone_controls')

    if not drone_controls_pk:
        return {'status': 'drone not connected'}

    drone_controls = Controls.get(drone_controls_pk)

    drone_controls.vx = velocity
    drone_controls.save()

    return drone_controls


@router.post('/y_speed/')
async def set_y_speed(velocity: float):
    if velocity > 20:
        return 'max speed 20 m/s'

    drone_controls_pk = r.get('drone_controls')

    if not drone_controls_pk:
        return {'status': 'drone not connected'}

    drone_controls = Controls.get(drone_controls_pk)

    drone_controls.vy = velocity
    drone_controls.save()

    return drone_controls


@router.post('/z_speed/{velocity}')
async def set_z_speed(velocity: float):
    if velocity > 20:
        return 'max speed 20 m/s'

    drone_controls_pk = r.get('drone_controls')

    if not drone_controls_pk:
        return {'status': 'drone not connected'}

    drone_controls = Controls.get(drone_controls_pk)

    drone_controls.vz = velocity
    drone_controls.save()

    return drone_controls


@router.post('/yaw/{degrees}')
async def set_yaw_degrees(degrees: int):
    drone_controls_pk = r.get('drone_controls')

    if not drone_controls_pk:
        return {'status': 'drone not connected'}

    drone_controls = Controls.get(drone_controls_pk)

    drone_controls.yaw = degrees
    drone_controls.save()

    return drone_controls

@router.post('/set_velocity/{vx}/{vy}/{vz}/{yaw}')
async def set_velocity(vx, vy, vz, yaw):
    drone_controls_pk = r.get('drone_controls')

    if not drone_controls_pk:
        return {'status': 'drone not connected'}

    drone_controls = Controls.get(drone_controls_pk)

    drone_controls.vx = vx
    drone_controls.vy = vy
    drone_controls.vz = vz
    drone_controls.yaw = yaw

    drone_controls.save()

    return drone_controls

@router.post('/take_off')
async def take_off():
    drone_info = redis_helper.get_drone_info(r)
    if not drone_info:
        return {'status': 'drone not connected'}

    drone_info.app_mode = 'take_off'
    drone_info.save()

    return {'status': 'success'}


@router.post('/velocity_mode')
async def velocity_mode():
    drone_info = redis_helper.get_drone_info(r)
    if not drone_info:
        return {'status': 'drone not connected'}

    drone_info.app_mode = 'velocity'
    drone_info.save()

    return {'status': 'drone not connected'}


@router.post('/go_to_mode')
async def go_to_mode():
    drone_info = redis_helper.get_drone_info(r)
    if not drone_info:
        return {'status': 'drone not connected'}

    print(drone_info)

    drone_info.app_mode = 'go_to'
    drone_info.save()

    return {'status': 'drone not connected'}


@router.post('/gps_set/{lat}/{lon}/{alt}')
async def gps_set(lat, lon, alt):
    return {
        'lat': lat,
        'lon': lon,
        'alt': alt
    }


@router.post('/landing_mode')
async def landing_mode():
    drone_info = redis_helper.get_drone_info(r)
    if not drone_info:
        return {'status': 'drone not connected'}

    drone_info.app_mode = 'landing'
    drone_info.save()

    return {'status': 'drone not connected'}
