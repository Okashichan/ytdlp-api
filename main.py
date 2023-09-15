import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import yt_dlp
import os
import threading
import time
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

VIDEO_DIR = "downloaded_videos"
HOST = "0.0.0.0"
PORT = 1337
PUBLIC_URL = os.getenv("PUBLIC_URL")

ydl_opts = {
    'format': 'best',
    'quiet': True,
    'outtmpl': f'{VIDEO_DIR}/%(id)s.%(ext)s',
}


def cleanup_videos():
    while True:
        for filename in os.listdir(VIDEO_DIR):
            filepath = os.path.join(VIDEO_DIR, filename)
            if os.path.isfile(filepath) and time.time() - os.path.getmtime(filepath) >= 3600:
                os.remove(filepath)
        time.sleep(3600)  # Run the cleanup every hour


# Start the cleanup thread
cleanup_thread = threading.Thread(target=cleanup_videos)
cleanup_thread.daemon = True
cleanup_thread.start()


@app.post("/get_video_url/")
async def get_video_url(youtube_url: str):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            video_ext = info['ext']
            video_id = info['id']
            video_filename = f"{video_id}.{video_ext}"
            video_path = os.path.join(VIDEO_DIR, video_filename)
            if os.path.exists(video_path):
                return {"url": f"{PUBLIC_URL}/get_video/{video_filename}"}
            else:
                raise HTTPException(status_code=404, detail="Video not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_video/{video_name}")
async def get_video(video_name: str):
    video_path = os.path.join(VIDEO_DIR, video_name)
    if os.path.exists(video_path):
        return FileResponse(video_path)
    else:
        raise HTTPException(status_code=404, detail="Video not found")

if __name__ == "__main__":
    if not PUBLIC_URL:
        sys.exit("Error: PUBLIC_URL environment variable not set")
    if not os.path.exists(VIDEO_DIR):
        os.makedirs(VIDEO_DIR)

    uvicorn.run(app, host=HOST, port=PORT)
