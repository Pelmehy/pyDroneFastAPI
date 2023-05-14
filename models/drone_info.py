from redis_om import JsonModel, get_redis_connection
redis = get_redis_connection(port=6379)

class Drone_info(JsonModel):
    app_mode: str           # go_to / velocity / landing
    is_connected: bool


class Drone_settings(JsonModel):
    is_connected: bool
    arm: bool
    is_took_off: bool
    ground_speed: float     # m/s
