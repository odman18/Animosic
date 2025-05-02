from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.playlist_service import generate_playlist

router = APIRouter()

# Define the request model
class PlaylistRequest(BaseModel):
    mood: str
    genre: Optional[str] = None
    artist: Optional[str] = None

@router.get("/")
async def root():
    return {"message": "Welcome to Animosic Playlist Generator"}
@router.post("/generate_playlist")
async def create_playlist(request: PlaylistRequest):
    try:
        playlist = generate_playlist(
            user_mood=request.mood,
            user_genre=request.genre,
            user_artist=request.artist
        )
        pplaylist = playlist.replace({float('nan'): None})
        return {"playlist": playlist.to_dict(orient='records')}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")