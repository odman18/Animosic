from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from services.playlist_service import generate_playlist
import base64
import os
from dotenv import load_dotenv
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()
router = APIRouter()

# Define the request model
class PlaylistRequest(BaseModel):
    mood: str
    genre: Optional[str] = None
    artist: Optional[str] = None

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8000/callback"  
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPES = "playlist-modify-public playlist-modify-private user-read-private"

# Simple in-memory state storage 
state_store = {}

@router.get("/")
async def root():
    return {"message": "Welcome to Animosic Playlist Generator"}

@router.get("/login")
async def login():
    state = base64.b64encode(os.urandom(16)).decode("utf-8")
    state_store["state"] = state  # Store state
    auth_url = (
        f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope={SCOPES}&state={state}"
    )
    return RedirectResponse(auth_url)

@router.get("/callback")
async def callback(code: str, state: str):
    if state_store.get("state") != state:
        logger.error(f"State mismatch: stored {state_store.get('state')}, received {state}")
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    del state_store["state"]  # Clean up state

    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    logger.debug(f"Token data: {token_data}") 
    response = requests.post(TOKEN_URL, data=token_data)
    logger.debug(f"Token response status: {response.status_code}, body: {response.text}")
    if response.status_code != 200:
        logger.error(f"Failed to get access token: {response.text}")
        raise HTTPException(status_code=400, detail="Failed to get access token")

    tokens = response.json()
    access_token = tokens.get("access_token")
    if not access_token:
        logger.error(f"No access token in response: {tokens}")
        raise HTTPException(status_code=400, detail="No access token received")

    logger.debug(f"Access token retrieved: {access_token}") 
    return RedirectResponse(f"http://127.0.0.1:3000/callback.html?access_token={access_token}")

@router.post("/generate_playlist")
async def create_playlist(request: PlaylistRequest):
    try:
        playlist = generate_playlist(
            user_mood=request.mood,
            user_genre=request.genre,
            user_artist=request.artist
        )
        pplaylist = playlist.replace({float('nan'): None})
        return {"playlist": pplaylist.to_dict(orient='records')}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")