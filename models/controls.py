from redis_om import HashModel, get_redis_connection
redis = get_redis_connection(port=6379)

class Controls(HashModel):
    vx: float   # m/s
    vy: float   # m/s
    vz: float   # m/s
    yaw: float  # m/s
