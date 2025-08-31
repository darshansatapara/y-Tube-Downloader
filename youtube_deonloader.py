# import streamlit as st
# import yt_dlp
# import os
# import subprocess
# import sys
# import time
# import logging

# # --- Setup Logging ---
# logging.basicConfig(level=logging.INFO)

# # --- Check for FFmpeg ---
# def check_ffmpeg():
#     try:
#         result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, encoding="utf-8", check=True)
#         logging.info(f"FFmpeg found: {result.stdout.splitlines()[0]}")
#         return True
#     except (subprocess.CalledProcessError, FileNotFoundError) as e:
#         st.error(f"❌ FFmpeg is not installed or not found in PATH. Please install FFmpeg to enable audio merging. Error: {str(e)}")
#         return False

# if not check_ffmpeg():
#     st.stop()

# # --- Streamlit Page Setup ---
# st.set_page_config(page_title="🎬 YouTube Downloader", page_icon="🎧", layout="wide")
# st.title("🎬 YouTube Video & Playlist Downloader")

# # --- Download Folder ---
# download_folder = "D:/ytube-downloader"
# if not os.path.exists(download_folder):
#     os.makedirs(download_folder)

# # --- Progress Tracking ---
# if "downloads" not in st.session_state:
#     st.session_state.downloads = {}  # Track download status
# if "video_info" not in st.session_state:
#     st.session_state.video_info = None
# if "selected_videos" not in st.session_state:
#     st.session_state.selected_videos = []
# if "quality_options" not in st.session_state:
#     st.session_state.quality_options = []
# if "chosen_quality" not in st.session_state:
#     st.session_state.chosen_quality = None

# # --- Progress Bar & Status ---
# progress_bar = st.progress(0)
# status_text = st.empty()

# def progress_hook(d):
#     """Updates progress bar and status during download"""
#     video_id = st.session_state.current_video_id
#     if d['status'] == 'downloading':
#         percent = d.get('_percent_str', '0.0%')
#         try:
#             pct = float(percent.replace('%', ''))
#             progress_bar.progress(int(pct))
#         except:
#             pass
#         st.session_state.downloads[video_id] = {
#             'status': f"Downloading: {percent} | ETA: {d.get('_eta_str', 'NA')}",
#             'downloaded': d.get('downloaded_bytes', 0),
#             'total': d.get('total_bytes', 0)
#         }
#         status_text.text(st.session_state.downloads[video_id]['status'])
#     elif d['status'] == 'finished':
#         progress_bar.progress(100)
#         st.session_state.downloads[video_id]['status'] = "Completed"
#         status_text.text("✅ Download complete, finalizing file...")

# # --- Input ---
# url = st.text_input("🔗 Enter YouTube URL (Video or Playlist):")

# # --- Fetch Video/Playlist Metadata ---
# if url and url != st.session_state.get("last_url", ""):
#     try:
#         with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
#             st.session_state.video_info = ydl.extract_info(url, download=False)
#         st.session_state.last_url = url

#         # --- Playlist or Single Video ---
#         if "entries" in st.session_state.video_info:
#             playlist_videos = st.session_state.video_info["entries"]
#             video_titles = [video["title"] for video in playlist_videos]
#             st.session_state.selected_videos = video_titles  # Preselect all
#         else:
#             playlist_videos = [st.session_state.video_info]
#             st.session_state.selected_videos = [st.session_state.video_info["title"]]

#         # --- Quality Selection ---
#         formats = playlist_videos[0]["formats"]
#         quality_options = sorted(
#             set(f.get("height") for f in formats if f.get("ext") == "mp4" and f.get("height")),
#             reverse=True
#         )
#         quality_options = [str(q) for q in quality_options]  # Convert to strings
#         st.session_state.quality_options = quality_options
#         st.session_state.chosen_quality = quality_options[0] if quality_options else "720"  # Default to highest or 720p
#     except Exception as e:
#         st.error(f"❌ Error fetching metadata: {str(e)}")
#         logging.error(f"Metadata extraction error: {str(e)}")
#         st.session_state.video_info = None
#         st.session_state.quality_options = []
#         st.session_state.selected_videos = []

# # --- Static UI ---
# st.subheader("🎞️ Video/Playlist Selection")
# if st.session_state.video_info and "entries" in st.session_state.video_info:
#     st.session_state.selected_videos = st.multiselect(
#         "✅ Select videos to download:",
#         options=[video["title"] for video in st.session_state.video_info["entries"]],
#         default=st.session_state.selected_videos
#     )
# elif st.session_state.video_info:
#     st.write(f"🎥 Video: {st.session_state.video_info['title']}")
# else:
#     st.write("ℹ️ Enter a valid URL to see video/playlist details.")

# st.subheader("🎚️ Quality Selection")
# if st.session_state.quality_options:
#     st.session_state.chosen_quality = st.selectbox(
#         "Select Quality (p)",
#         options=st.session_state.quality_options,
#         index=0  # Default to highest quality
#     )
# else:
#     st.session_state.chosen_quality = st.selectbox(
#         "Select Quality (p)",
#         options=["360", "720", "1080", "1440", "2160"],
#         index=1,  # Default to 720p
#         disabled=True
#     )

# # --- Download Button ---
# download_button = st.button("⬇️ Start Download", disabled=not st.session_state.video_info)

# if download_button and st.session_state.video_info:
#     playlist_videos = st.session_state.video_info["entries"] if "entries" in st.session_state.video_info else [st.session_state.video_info]
#     for video in playlist_videos:
#         if video["title"] in st.session_state.selected_videos:
#             video_id = str(len(st.session_state.downloads) + 1)
#             st.session_state.downloads[video_id] = {'status': 'Queued', 'downloaded': 0, 'total': 0}
#             st.session_state.current_video_id = video_id

#             # Create video-specific directory
#             video_dir = os.path.join(download_folder, video_id)
#             if not os.path.exists(video_dir):
#                 os.makedirs(video_dir)

#             ydl_opts = {
#                 'format': f'bestvideo[height<={st.session_state.chosen_quality}]+bestaudio/best[height<={st.session_state.chosen_quality}]',
#                 'merge_output_format': 'mp4',
#                 'outtmpl': os.path.join(video_dir, '%(title)s.%(ext)s'),
#                 'progress_hooks': [progress_hook],
#                 'postprocessors': [{
#                     'key': 'FFmpegVideoConvertor',
#                     'preferedformat': 'mp4'
#                 }],
#                 'verbose': True
#             }

#             st.info(f"▶️ Downloading: {video['title']}")
#             try:
#                 with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                     info = ydl.extract_info(video["webpage_url"], download=True)
#                     filename = ydl.prepare_filename(info)
#                     # Verify audio stream
#                     result = subprocess.run(
#                         ["ffprobe", "-show_streams", filename],
#                         capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
#                     )
#                     has_audio = "codec_type=audio" in result.stdout
#                     if not has_audio:
#                         st.warning(f"⚠️ File {os.path.basename(filename)} has no audio stream. Trying fallback...")
#                         ydl_opts['format'] = 'best[height<=720]'
#                         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                             info = ydl.extract_info(video["webpage_url"], download=True)
#                             filename = ydl.prepare_filename(info)
#                             result = subprocess.run(
#                                 ["ffprobe", "-show_streams", filename],
#                                 capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
#                             )
#                             has_audio = "codec_type=audio" in result.stdout
#                             if not has_audio:
#                                 st.error(f"❌ Fallback failed: {os.path.basename(filename)} still has no audio.")
#                     if has_audio:
#                         with open(filename, "rb") as f:
#                             time.sleep(1)  # Ensure file is fully written
#                             st.download_button(
#                                 label=f"⬇️ Saved in ytube-download folder: {os.path.basename(filename)}",
#                                 data=f,
#                                 file_name=os.path.basename(filename),
#                                 mime="video/mp4"
#                             )
#             except yt_dlp.DownloadError as de:
#                 st.error(f"❌ Download failed for {video['title']}: {str(de)}")
#                 logging.error(f"Download error: {str(de)}")
#             except subprocess.CalledProcessError as pe:
#                 st.error(f"❌ FFprobe error for {video['title']}: {str(pe)}")
#                 logging.error(f"FFprobe error: {str(pe)}")
#             except Exception as e:
#                 st.error(f"❌ General error for {video['title']}: {str(e)}")
#                 logging.error(f"General error: {str(e)}")

# # --- Display Download Status ---
# if st.session_state.downloads:
#     st.subheader("📊 Download Status")
#     for video_id, status in st.session_state.downloads.items():
#         st.write(f"Video ID {video_id}: {status['status']}")

# # --- Optional Cleanup ---
# if st.session_state.downloads and st.button("🗑️ Clear Downloaded Files"):
#     for video_id in st.session_state.downloads:
#         video_dir = os.path.join(download_folder, video_id)
#         if os.path.exists(video_dir):
#             for file in os.listdir(video_dir):
#                 os.remove(os.path.join(video_dir, file))
#             os.rmdir(video_dir)
#     st.session_state.downloads.clear()
#     st.success("✅ All downloaded files cleared.")


import streamlit as st
import yt_dlp
import os
import subprocess
import sys
import time
import logging

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)

# --- Check for FFmpeg ---
def check_ffmpeg():
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, encoding="utf-8", check=True)
        logging.info(f"FFmpeg found: {result.stdout.splitlines()[0]}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        st.error(
            f"❌ FFmpeg is not installed or not found in PATH. Please install FFmpeg to enable audio merging. "
            f"Error: {str(e)}\n\n"
            f"For Streamlit Cloud, ensure a `packages.txt` file exists in your repository with 'ffmpeg' listed."
        )
        return False

if not check_ffmpeg():
    st.stop()

# --- Streamlit Page Setup ---
st.set_page_config(page_title="🎬 YouTube Downloader", page_icon="🎧", layout="wide")
st.title("🎬 YouTube Video & Playlist Downloader")

# --- Download Folder ---
download_folder = "D:/ytube-downloader"
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

# --- Progress Tracking ---
if "downloads" not in st.session_state:
    st.session_state.downloads = {}  # Track download status
if "video_info" not in st.session_state:
    st.session_state.video_info = None
if "selected_videos" not in st.session_state:
    st.session_state.selected_videos = []
if "quality_options" not in st.session_state:
    st.session_state.quality_options = []
if "chosen_quality" not in st.session_state:
    st.session_state.chosen_quality = None

# --- Progress Bar & Status ---
progress_bar = st.progress(0)
status_text = st.empty()

def progress_hook(d):
    """Updates progress bar and status during download"""
    video_id = st.session_state.current_video_id
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0.0%')
        try:
            pct = float(percent.replace('%', ''))
            progress_bar.progress(int(pct))
        except:
            pass
        st.session_state.downloads[video_id] = {
            'status': f"Downloading: {percent} | ETA: {d.get('_eta_str', 'NA')}",
            'downloaded': d.get('downloaded_bytes', 0),
            'total': d.get('total_bytes', 0)
        }
        status_text.text(st.session_state.downloads[video_id]['status'])
    elif d['status'] == 'finished':
        progress_bar.progress(100)
        st.session_state.downloads[video_id]['status'] = "Completed"
        status_text.text("✅ Download complete, finalizing file...")

# --- Input ---
url = st.text_input("🔗 Enter YouTube URL (Video or Playlist):")

# --- Fetch Video/Playlist Metadata ---
if url and url != st.session_state.get("last_url", ""):
    try:
        ydl_opts = {
            "quiet": True,
            "cookiefile": "cookies.txt"  # Path to cookies file (optional, place in project root)
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            st.session_state.video_info = ydl.extract_info(url, download=False)
        st.session_state.last_url = url

        # --- Playlist or Single Video ---
        if "entries" in st.session_state.video_info:
            playlist_videos = st.session_state.video_info["entries"]
            video_titles = [video["title"] for video in playlist_videos]
            st.session_state.selected_videos = video_titles  # Preselect all
        else:
            playlist_videos = [st.session_state.video_info]
            st.session_state.selected_videos = [st.session_state.video_info["title"]]

        # --- Quality Selection ---
        formats = playlist_videos[0]["formats"]
        quality_options = sorted(
            set(f.get("height") for f in formats if f.get("ext") == "mp4" and f.get("height")),
            reverse=True
        )
        quality_options = [str(q) for q in quality_options]  # Convert to strings
        st.session_state.quality_options = quality_options
        st.session_state.chosen_quality = quality_options[0] if quality_options else "720"  # Default to highest or 720p
    except Exception as e:
        st.error(f"❌ Error fetching metadata: {str(e)}")
        logging.error(f"Metadata extraction error: {str(e)}")
        st.session_state.video_info = None
        st.session_state.quality_options = []
        st.session_state.selected_videos = []

# --- Static UI ---
st.subheader("🎞️ Video/Playlist Selection")
if st.session_state.video_info and "entries" in st.session_state.video_info:
    st.session_state.selected_videos = st.multiselect(
        "✅ Select videos to download:",
        options=[video["title"] for video in st.session_state.video_info["entries"]],
        default=st.session_state.selected_videos
    )
elif st.session_state.video_info:
    st.write(f"🎥 Video: {st.session_state.video_info['title']}")
else:
    st.write("ℹ️ Enter a valid URL to see video/playlist details.")

st.subheader("🎚️ Quality Selection")
if st.session_state.quality_options:
    st.session_state.chosen_quality = st.selectbox(
        "Select Quality (p)",
        options=st.session_state.quality_options,
        index=0  # Default to highest quality
    )
else:
    st.session_state.chosen_quality = st.selectbox(
        "Select Quality (p)",
        options=["360", "720", "1080", "1440", "2160"],
        index=1,  # Default to 720p
        disabled=True
    )

# --- Download Button ---
download_button = st.button("⬇️ Start Download", disabled=not st.session_state.video_info)

if download_button and st.session_state.video_info:
    playlist_videos = st.session_state.video_info["entries"] if "entries" in st.session_state.video_info else [st.session_state.video_info]
    for video in playlist_videos:
        if video["title"] in st.session_state.selected_videos:
            video_id = str(len(st.session_state.downloads) + 1)
            st.session_state.downloads[video_id] = {'status': 'Queued', 'downloaded': 0, 'total': 0}
            st.session_state.current_video_id = video_id

            # Create video-specific directory
            video_dir = os.path.join(download_folder, video_id)
            if not os.path.exists(video_dir):
                os.makedirs(video_dir)

            ydl_opts = {
                'format': f'bestvideo[height<={st.session_state.chosen_quality}]+bestaudio/best[height<={st.session_state.chosen_quality}]',
                'merge_output_format': 'mp4',
                'outtmpl': os.path.join(video_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }],
                'cookiefile': 'cookies.txt',  # Path to cookies file (optional)
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'verbose': True
            }

            st.info(f"▶️ Downloading: {video['title']}")
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video["webpage_url"], download=True)
                    filename = ydl.prepare_filename(info)
                    # Verify audio stream
                    result = subprocess.run(
                        ["ffprobe", "-show_streams", filename],
                        capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
                    )
                    has_audio = "codec_type=audio" in result.stdout
                    if not has_audio:
                        st.warning(f"⚠️ File {os.path.basename(filename)} has no audio stream. Trying fallback...")
                        ydl_opts['format'] = 'best[height<=720]'
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(video["webpage_url"], download=True)
                            filename = ydl.prepare_filename(info)
                            result = subprocess.run(
                                ["ffprobe", "-show_streams", filename],
                                capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
                            )
                            has_audio = "codec_type=audio" in result.stdout
                            if not has_audio:
                                st.error(f"❌ Fallback failed: {os.path.basename(filename)} still has no audio.")
                    if has_audio:
                        with open(filename, "rb") as f:
                            time.sleep(1)  # Ensure file is fully written
                            st.download_button(
                                label=f"⬇️ Download {os.path.basename(filename)}",
                                data=f,
                                file_name=os.path.basename(filename),
                                mime="video/mp4"
                            )
            except yt_dlp.DownloadError as de:
                if "HTTP Error 403: Forbidden" in str(de):
                    st.error(
                        f"❌ Download failed for {video['title']}: HTTP Error 403: Forbidden. "
                        f"This video may be restricted (e.g., age-restricted, geo-blocked, or private). "
                        f"Try providing a cookies file (`cookies.txt`) in the project root or testing with a public video."
                    )
                    logging.error(f"403 Forbidden error for {video['title']}: {str(de)}")
                else:
                    st.error(f"❌ Download failed for {video['title']}: {str(de)}")
                    logging.error(f"Download error: {str(de)}")
            except subprocess.CalledProcessError as pe:
                st.error(f"❌ FFprobe error for {video['title']}: {str(pe)}")
                logging.error(f"FFprobe error: {str(pe)}")
            except Exception as e:
                st.error(f"❌ General error for {video['title']}: {str(e)}")
                logging.error(f"General error: {str(e)}")

# --- Display Download Status ---
if st.session_state.downloads:
    st.subheader("📊 Download Status")
    for video_id, status in st.session_state.downloads.items():
        st.write(f"Video ID {video_id}: {status['status']}")

# --- Optional Cleanup ---
if st.session_state.downloads and st.button("🗑️ Clear Downloaded Files"):
    for video_id in st.session_state.downloads:
        video_dir = os.path.join(download_folder, video_id)
        if os.path.exists(video_dir):
            for file in os.listdir(video_dir):
                os.remove(os.path.join(video_dir, file))
            os.rmdir(video_dir)
    st.session_state.downloads.clear()
    st.success("✅ All downloaded files cleared.")