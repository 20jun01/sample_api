import random
from typing import Union, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID, uuid4
from pydantic import BaseModel
from enum import Enum
import requests
import os

search_place_details_url = "https://maps.googleapis.com/maps/api/place/details/json?"

search_place_random_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key='


class MapRequest(BaseModel):
    location: str
    keywords: list[str]
    radius: int


class MapResponse(BaseModel):
    url: str
    name: str


app = FastAPI()

origins = [
    "https://sample-front-weld.vercel.app",
    "https://sample-front-nmyv57y1w-20jun01.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get("/health")
async def root():
    return {"status": "Server is working!"}


@app.post("/map", response_model=MapResponse)
async def read_item(request: MapRequest):
    random.seed()
    keyword = ""
    location = ""
    radius = str(request.radius)
    api_key = os.environ.get('GOOGLE_MAP_API_KEY')
    if not (request.keywords == [""]):
        keyword = "OR".join(request.keywords)
    else:
        keyword = "カフェ"
    if type(request.location) == str:
        location += str(request.location)
    else:
        location += str(request.location[0]) + "," + str(request.location[1])
    request_url = search_place_random_url + \
        api_key + '&location=' + location + '&radius=' + \
        radius + '&language=ja&keyword=' + keyword
    resp = requests.get(request_url)
    resp_json1 = resp.json()
    if len(resp_json1['results']) == 0:
        raise HTTPException(status_code=404, detail="No results found")
    results = resp_json1['results']
    random_index = random.randint(0, len(results) - 1)
    shop = results[random_index]
    place_id = shop['place_id']
    resp = requests.get(search_place_details_url +
                        'place_id=' + place_id + '&key=' + api_key)
    resp_json = resp.json()
    if resp_json['status'] == 'INVALID_REQUEST':
        raise HTTPException(status_code=500, detail="Invalid request")
    return MapResponse(url=resp_json['result']['url'], name=shop['name'])
