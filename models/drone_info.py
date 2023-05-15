from redis_om import HashModel, get_redis_connection
redis = get_redis_connection(port=6379)

class Drone_info(HashModel):
    app_mode: str           # go_to / velocity / landing
    is_connected: int
    is_active: int


class Drone_settings(HashModel):
    is_connected: int
    arm: int
    is_took_off: int
    ground_speed: float     # m/s
