from youtube_transcript_api import YouTubeTranscriptApi
import re


def get_video_id(url):
    if "watch?v=" in url:
        return url.split("watch?v=")[-1]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1]
    else:
        raise ValueError("Invalid YouTube URL")


def clean_text(text):
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_transcript(url):
    video_id = get_video_id(url)

    transcript = YouTubeTranscriptApi().fetch(video_id)

    full_text = " ".join([item.text for item in transcript])

    return clean_text(full_text)