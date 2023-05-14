from redis_om import HashModel, get_redis_connection
redis = get_redis_connection(port=6379)

class Cur_gps(HashModel):
    cur_lat: float
    cur_lon: float
    cur_alt: float

class Go_to_gps(HashModel):
    go_to_lat: float
    go_to_lon: float
    go_to_alt: float

