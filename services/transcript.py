"""
services/transcript.py

Production-grade transcript extraction pipeline.

Features:
1. YouTube Transcript API captions
2. Whisper fallback for videos without captions
3. Structured transcript output
4. Timestamp preservation
5. Clean text normalization
6. Better RAG grounding support
7. Hallucination-safe metadata preparation
"""

import re
import os
import tempfile
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


# ============================================================
# VIDEO ID EXTRACTION
# ============================================================

def _extract_video_id(url: str) -> str:
    """
    Extract YouTube video ID from URL.
    Supports:
    - youtube.com/watch?v=
    - youtu.be/
    - shorts/
    - embed/
    """

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

    raise ValueError(f"Could not extract video ID from URL: {url}")


# ============================================================
# TEXT CLEANING
# ============================================================

def _clean(text: str) -> str:
    """
    Normalize transcript text.
    """

    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&#39;", "'", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# ENTRY PARSER
# ============================================================

def _parse_entry(entry) -> Dict:
    """
    Normalize transcript entry into standard structure.
    Works for dict objects and transcript objects.
    """

    if isinstance(entry, dict):

        return {
            "text": _clean(entry.get("text", "")),
            "start": float(entry.get("start", 0)),
            "duration": float(entry.get("duration", 0)),
        }

    return {
        "text": _clean(getattr(entry, "text", "")),
        "start": float(getattr(entry, "start", 0)),
        "duration": float(getattr(entry, "duration", 0)),
    }


# ============================================================
# CAPTION API METHOD
# ============================================================

def _fetch_via_caption_api(video_id: str) -> List[Dict]:
    """
    Fetch transcript using youtube-transcript-api.
    """

    from youtube_transcript_api import YouTubeTranscriptApi

    api = YouTubeTranscriptApi()

    # --------------------------------------------------------
    # Try direct fetch first
    # --------------------------------------------------------

    try:

        fetched = api.fetch(
            video_id,
            languages=["en", "en-US", "en-GB"]
        )

        structured = [
            _parse_entry(entry)
            for entry in fetched
            if _parse_entry(entry)["text"]
        ]

        logger.info(
            f"[transcript] Direct fetch succeeded for {video_id}"
        )

        return structured

    except Exception as direct_err:

        logger.warning(
            f"[transcript] Direct fetch failed: {direct_err}"
        )

    # --------------------------------------------------------
    # Fallback to transcript listing
    # --------------------------------------------------------

    transcript_list = api.list(video_id)

    transcript = None

    for lang in ["en", "en-US", "en-GB"]:

        try:
            transcript = transcript_list.find_transcript([lang])
            break

        except Exception:
            continue

    if transcript is None:

        transcript = next(iter(transcript_list))

    fetched = transcript.fetch()

    structured = [
        _parse_entry(entry)
        for entry in fetched
        if _parse_entry(entry)["text"]
    ]

    logger.info(
        f"[transcript] list()+fetch() succeeded for {video_id}"
    )

    return structured


# ============================================================
# WHISPER FALLBACK
# ============================================================

def _fetch_via_whisper(url: str) -> List[Dict]:
    """
    Fallback transcript generation using:
    yt-dlp + OpenAI Whisper

    Requires:
    - yt-dlp
    - openai-whisper
    - ffmpeg
    """

    try:
        import yt_dlp
    except ImportError:
        raise ImportError(
            "yt-dlp not installed. Run: pip install yt-dlp"
        )

    try:
        import whisper
    except ImportError:
        raise ImportError(
            "openai-whisper not installed. "
            "Run: pip install openai-whisper"
        )

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

        logger.info(
            "[transcript] Downloading audio via yt-dlp..."
        )

        try:

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        except Exception as dl_err:

            if "ffmpeg" in str(dl_err).lower():

                raise RuntimeError(
                    "ffmpeg is not installed.\n"
                    "macOS: brew install ffmpeg\n"
                    "Ubuntu: sudo apt install ffmpeg\n"
                    "Windows: https://ffmpeg.org/download.html"
                ) from dl_err

            raise

        # ----------------------------------------------------
        # Locate audio file
        # ----------------------------------------------------

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

        logger.info(
            "[transcript] Transcribing with Whisper..."
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

            text = _clean(segment.get("text", ""))

            if not text:
                continue

            structured.append({
                "text": text,
                "start": float(segment.get("start", 0)),
                "duration": float(
                    segment.get("end", 0)
                    - segment.get("start", 0)
                ),
            })

        return structured


# ============================================================
# TRANSCRIPT VALIDATION
# ============================================================

def _validate_transcript(
    transcript: List[Dict]
) -> List[Dict]:
    """
    Additional cleaning + hallucination prevention prep.
    """

    validated = []

    for item in transcript:

        text = item["text"].strip()

        # Remove tiny/noisy chunks
        if len(text) < 3:
            continue

        # Remove repeated spam captions
        if text.lower() in ["[music]", "[applause]"]:
            continue

        validated.append(item)

    return validated


# ============================================================
# MAIN PUBLIC FUNCTION
# ============================================================

def fetch_transcript(url: str) -> List[Dict]:
    """
    Main transcript extraction entry point.

    Returns:
    [
        {
            "text": "...",
            "start": 12.3,
            "duration": 4.1
        }
    ]
    """

    video_id = _extract_video_id(url)

    caption_error = ""

    # --------------------------------------------------------
    # Try Caption API
    # --------------------------------------------------------

    try:

        transcript = _fetch_via_caption_api(video_id)

        transcript = _validate_transcript(transcript)

        logger.info(
            f"[transcript] "
            f"{len(transcript)} entries fetched via captions."
        )

        return transcript

    except Exception as e:

        caption_error = str(e)

        logger.warning(
            f"[transcript] Caption API failed: {e}"
        )

    # --------------------------------------------------------
    # Whisper Fallback
    # --------------------------------------------------------

    try:

        transcript = _fetch_via_whisper(url)

        transcript = _validate_transcript(transcript)

        logger.info(
            f"[transcript] "
            f"{len(transcript)} entries fetched via Whisper."
        )

        return transcript

    except Exception as whisper_error:

        raise RuntimeError(
            f"\nBoth transcript methods failed.\n\n"
            f"Caption API Error:\n{caption_error}\n\n"
            f"Whisper Error:\n{whisper_error}"
        ) from whisper_error


# ============================================================
# HELPER FUNCTION
# ============================================================

def transcript_to_text(
    transcript: List[Dict]
) -> str:
    """
    Convert structured transcript to plain text.
    Useful for summarization.
    """

    return " ".join(
        item["text"]
        for item in transcript
    )