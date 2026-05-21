"""
services/transcript.py

AI Lecture Assistant
Transcript extraction pipeline

Features:
1. YouTube captions
2. Whisper fallback
3. Transcript source tracking
4. Structured timestamps
"""

import re
import os
import tempfile
import logging

logger = logging.getLogger(__name__)


# ============================================================
# EXTRACT VIDEO ID
# ============================================================

def _extract_video_id(url: str) -> str:

    patterns = [
        r"(?:v=)([A-Za-z0-9_-]{11})",
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"embed/([A-Za-z0-9_-]{11})",
        r"shorts/([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:

        match = re.search(pattern, url)

        if match:
            return match.group(1)

    raise ValueError(
        f"Could not extract video ID from URL: {url}"
    )


# ============================================================
# CLEAN TEXT
# ============================================================

def _clean(text: str):

    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&#39;", "'", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# PARSE ENTRY
# ============================================================

def _parse_entry(entry):

    if isinstance(entry, dict):

        return {
            "text": _clean(
                entry.get("text", "")
            ),
            "start": float(
                entry.get("start", 0)
            ),
            "duration": float(
                entry.get("duration", 0)
            ),
        }

    return {
        "text": _clean(
            getattr(entry, "text", "")
        ),
        "start": float(
            getattr(entry, "start", 0)
        ),
        "duration": float(
            getattr(entry, "duration", 0)
        ),
    }


# ============================================================
# FETCH VIA YOUTUBE CAPTIONS
# ============================================================

def _fetch_via_caption_api(video_id: str):

    from youtube_transcript_api import (
        YouTubeTranscriptApi
    )

    api = YouTubeTranscriptApi()

    fetched = api.fetch(
        video_id,
        languages=["en", "en-US", "en-GB"]
    )

    structured = [
        _parse_entry(entry)
        for entry in fetched
        if _parse_entry(entry)["text"]
    ]

    return structured


# ============================================================
# FETCH VIA WHISPER
# ============================================================

def _fetch_via_whisper(url: str):

    import yt_dlp
    import whisper

    with tempfile.TemporaryDirectory() as tmp_dir:

        audio_template = os.path.join(
            tmp_dir,
            "audio.%(ext)s"
        )

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": audio_template,
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            ydl.download([url])

        audio_file = None

        for fname in os.listdir(tmp_dir):

            if fname.startswith("audio"):

                audio_file = os.path.join(
                    tmp_dir,
                    fname
                )

                break

        if not audio_file:

            raise RuntimeError(
                "Audio download failed."
            )

        model = whisper.load_model("base")

        result = model.transcribe(
            audio_file,
            language="en",
            verbose=False
        )

        segments = result.get("segments", [])

        structured = []

        for segment in segments:

            text = _clean(
                segment.get("text", "")
            )

            if not text:
                continue

            structured.append({
                "text": text,
                "start": float(
                    segment.get("start", 0)
                ),
                "duration": float(
                    segment.get("end", 0)
                    - segment.get("start", 0)
                ),
            })

        return structured


# ============================================================
# FETCH TRANSCRIPT
# ============================================================

def fetch_transcript(url: str):
    """
    Returns:
    {
        "transcript": [...],
        "source": "YouTube Captions" OR "Whisper AI"
    }
    """

    video_id = _extract_video_id(url)

    caption_error = ""

    # --------------------------------------------------------
    # TRY YOUTUBE CAPTIONS
    # --------------------------------------------------------

    try:

        transcript = _fetch_via_caption_api(
            video_id
        )

        logger.info(
            "[transcript] Using YouTube captions."
        )

        return {
            "transcript": transcript,
            "source": "YouTube Captions"
        }

    except Exception as e:

        caption_error = str(e)

        logger.warning(
            f"[transcript] Caption API failed: {e}"
        )

    # --------------------------------------------------------
    # FALLBACK TO WHISPER
    # --------------------------------------------------------

    try:

        transcript = _fetch_via_whisper(url)

        logger.info(
            "[transcript] Using Whisper fallback."
        )

        return {
            "transcript": transcript,
            "source": "Whisper AI"
        }

    except Exception as whisper_error:

        raise RuntimeError(
            f"Both transcript methods failed.\n\n"
            f"Caption Error:\n{caption_error}\n\n"
            f"Whisper Error:\n{whisper_error}"
        )


# ============================================================
# TRANSCRIPT TO TEXT
# ============================================================

def transcript_to_text(transcript):

    return " ".join([
        item["text"]
        for item in transcript
    ])