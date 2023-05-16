from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routs.drone_api_controls import router as drone_api_controls

app = FastAPI()

origins = [
    "http://localhost:5000",
    'http://127.0.0.1:5000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    drone_api_controls,
    prefix='/drone-api'
)

@app.get('/')
def hello():
    return 'hello world'

# @app.on_event('startup')
# async def startup_event():
#     redis = aioredis.from_url('redis://localhost', encoding='utf8', decode_responses=True)
#     # FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')
