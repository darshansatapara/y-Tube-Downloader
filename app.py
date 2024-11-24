from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import threading
import platform
from flask_cors import CORS  # Import CORS to handle cross-origin requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

downloads = {}  # To track download progress and statuses.

# Base folder setup for both desktop and mobile
desktop_folder = 'D:/ytube-downloader'
mobile_folder = 'ytube-downloader'

# Check if the desktop folder exists
if platform.system() == 'Windows':
    if not os.path.exists(desktop_folder):
        os.makedirs(desktop_folder)
    download_folder = desktop_folder
else:
    # For mobile or other platforms (could be a server), we use the general folder
    if not os.path.exists(mobile_folder):
        os.makedirs(mobile_folder)
    download_folder = mobile_folder

@app.route('/')
def serve_html():
    file_path = os.path.join('templates', 'Youtube.html')
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "File not found", 404


# Function to download video
def download_video(url, quality, video_id):
    def progress_hook(d):
        if d['status'] == 'downloading':
            downloads[video_id]['status'] = f"Downloading: {d['_percent_str']} | {d['_eta_str']}"
            downloads[video_id]['downloaded'] = d['downloaded_bytes']
            downloads[video_id]['total'] = d['total_bytes']

    # Ensure the directory for the video ID exists
    video_dir = os.path.join(download_folder, video_id)
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)

    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
        'progress_hooks': [progress_hook],
        'outtmpl': os.path.join(video_dir, '%(title)s.%(ext)s'),  # Save video inside the video ID folder
    }

    # Fallback to 720p if quality isn't available
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloads[video_id]['status'] = "Completed"
    except Exception:
        ydl_opts['format'] = 'best[height<=720]'
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            downloads[video_id]['status'] = "Completed"

@app.route('/download', methods=['POST'])
def start_download():
    data = request.json
    url = data['url']
    
    # Allow '2k' as a quality option, with a fallback to 720p if unavailable
    quality = data.get('quality', 720)
    video_id = str(len(downloads) + 1)
    downloads[video_id] = {'status': 'Queued', 'downloaded': 0, 'total': 0}

    # Start a new thread to handle the download
    thread = threading.Thread(target=download_video, args=(url, quality, video_id))
    thread.start()

    return jsonify({'video_id': video_id, 'message': 'Download started.'})

@app.route('/status/<video_id>', methods=['GET'])
def download_status(video_id):
    return jsonify(downloads.get(video_id, {'status': 'Not Found'}))

@app.route('/terminate', methods=['POST'])
def terminate_download():
    # Clear all download tasks (in this case, clear the downloads dictionary)
    downloads.clear()
    # Return a success response to the frontend
    return jsonify({"message": "All downloads terminated."}), 200

if __name__ == "__main__":
    app.run(debug=True)
