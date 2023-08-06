import logging
import re
import os
import subprocess
import threading
from threading import Lock
import io
import sys
import time
import traceback
import pycountry
from queue import Queue, Empty
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime
from collections import Counter
from youtube_transcript_api import YouTubeTranscriptApi
from pydub import AudioSegment
from pydub.utils import make_chunks
from celery import Task

# TODO: Use google.cloud.speech_v2 instead of google.cloud.speech_v1p1beta1
# TODO: Use cloud storage instead of local storage
# from google.cloud.speech_v2 import SpeechClient
# from google.cloud.speech_v2.types import cloud_speech
from google.cloud import speech_v1p1beta1 as speech

start_duration_transcript_t = List[Dict[str, Union[str, float]]]

headers = {
    "authority": "api.youtube.com",
    "accept": "application/json, text/plain, */*",
    "user-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
}

class HytGpt:
    def __init__(self):
        pass

    def fetch_subtitles(
        self, ylink: str, task_instance: Optional[Task] = None
    ) -> Dict[str, Any]:
        if not self.is_valid_youtube_url(ylink):
            return {
                "status": "failed",
                "url": ylink,
                "subtitles": [],
                "summaries": "Invalid youtube url",
            }
        HytGpt.update_task_instance(task_instance, 0, "Fetching subtitles...")
        subtitles, language = self.__youtube_subtitle(ylink)
        if not subtitles:
            try:
                HytGpt.update_task_instance(
                    task_instance,
                    0.05,
                    "No subtitles found, transcribing video to subtitles...",
                )
                subtitles, language = self.transcribe_youtube_video(
                    ylink, task_instance
                )
            except Exception as e:
                print(f"Exception occurred in transcription: {str(e)}")
                traceback.print_exc()
                return {
                    "status": "failed",
                    "url": ylink,
                    "subtitles": subtitles,
                    "language": language,
                    "summaries": "Subtitle retrieval failed",
                }
        HytGpt.update_task_instance(task_instance, 1, "subtitles fetched.")
        return {
            "status": "success",
            "url": ylink,
            "subtitles": subtitles,
            "language": language,
            "summaries": "Subtitle retrieval succeeded",
        }

    def transcribe_youtube_video(
        self, ylink: str, task_instance: Optional[Task] = None
    ) -> Tuple[start_duration_transcript_t, str]:
        video_id = HytGpt.get_youtube_id(ylink)
        output_file = f"{video_id}.mp3"

        self.__download_youtube_audio(ylink, output_file)
        HytGpt.update_task_instance(task_instance, 0.2, "Audio downloaded.")

        chunk_duration_ms = 60000  # Duration of each audio chunk in milliseconds
        audio_chunks = self.__split_audio_file(video_id, chunk_duration_ms)
        os.remove(output_file)
        HytGpt.update_task_instance(task_instance, 0.3, "Audio prepared for processing.")

        transcripts = []
        for i, chunk in enumerate(audio_chunks):
            print(f"Transcribing chunk {i + 1}/{len(audio_chunks)}...")
            transcripts += self.__transcribe_audio_file(chunk)
            HytGpt.update_task_instance(
                task_instance, 0.3 + 0.6 * (i + 1) / len(audio_chunks), f"Transcribing the {i+1}/{len(audio_chunks)} parts..."
            )
            os.remove(chunk)
        common_language_code = self.__most_common_language_code(transcripts)
        common_language_name = self.__language_code_to_name(common_language_code)
        HytGpt.update_task_instance(task_instance, 0.95, "Transcription completed.")
        parsed_transcripts = self.__parse_transcripts(transcripts)

        return parsed_transcripts, common_language_name

    @staticmethod
    def update_progress(
        task_instance, progress_queue, progress_lock, start, end, duration
    ):
        increment = (end - start) / duration
        progress = start

        for _ in range(duration):
            progress += increment
            # progress_queue.put(progress)
            with progress_lock:
                HytGpt.update_task_instance(task_instance, progress)
            time.sleep(1)

    @staticmethod
    def update_task_instance(
        task_instance: Optional[Task], progress: float, info: str = ""
    ):
        """
        Update the task instance with the progress

        :param task_instance: The task instance
        :param progress: The progress of the task (between 0 and 1)
        """
        if task_instance:
            progress = int(progress * 100)
            if info:
                task_instance.update_state(
                    state="PROGRESS", meta={"progress": progress, "info": info}
                )
            else:
                task_instance.update_state(
                    state="PROGRESS", meta={"progress": progress}
                )

    @staticmethod
    def is_valid_youtube_url(url):
        # Regular expression pattern for YouTube URLs
        youtube_url_pattern = re.compile(
            r"(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+"
        )

        # Check if the URL matches the pattern
        if youtube_url_pattern.match(url):
            return True
        else:
            return False

    @staticmethod
    def get_youtube_id(url: str) -> Optional[str]:
        youtube_id_match = re.search(r"(?<=v=)[^&#]+", url)
        youtube_id_match = youtube_id_match or re.search(r"(?<=be/)[^&#]+", url)
        return youtube_id_match.group(0) if youtube_id_match else None

    @staticmethod
    def build_youtube_url(youtube_id: str) -> str:
        return f"https://www.youtube.com/watch?v={youtube_id}"

    @staticmethod
    def get_timestamp_diff(start_time, end_time):
        start_time = datetime.strptime(start_time, "%H:%M:%S.%f")
        end_time = datetime.strptime(end_time, "%H:%M:%S.%f")
        diff = (end_time - start_time).total_seconds()
        return diff

    @classmethod
    def should_concatenate(cls, segment1, segment2, max_time_difference=1.1):  # seconds
        current_end_time = segment1["start"] + segment1["duration"]
        next_start_time = segment2["start"]
        is_close = current_end_time + max_time_difference > next_start_time
        no_punctuation = not segment1["text"].strip().endswith((".", "?", "!"))
        return is_close and no_punctuation

    @staticmethod
    def parse_text_from_start_duration(
        subtitles: start_duration_transcript_t,
    ) -> List[str]:
        combined_texts = []
        current_text = subtitles[0]["text"]
        current_segment = subtitles[0]

        for i in range(1, len(subtitles)):
            next_segment = subtitles[i]

            if HytGpt.should_concatenate(current_segment, next_segment):
                current_text += " " + next_segment["text"]  # type: ignore
            else:
                combined_texts.append(current_text)
                current_text = next_segment["text"]

            current_segment = next_segment

        combined_texts.append(current_text)
        return combined_texts

    def __most_common_language_code(self, results):
        language_codes = [result.language_code for result in results]
        most_common_code = Counter(language_codes).most_common(1)[0][0]
        return most_common_code

    def __language_code_to_name(self, language_code: str) -> str:
        # Split the language code into parts
        parts = language_code.split("-")

        # Get the language and region objects from pycountry
        language = pycountry.languages.get(alpha_3=parts[0])
        script = pycountry.scripts.get(alpha_4=parts[1]) if len(parts) > 1 else None

        # Build the language name string
        language_name = language.name
        if script:
            language_name += f" ({script.name})"

        return language_name


    def __parse_transcripts(self, results) -> start_duration_transcript_t:
        formatted_results = []

        for result in results:
            alternative = result.alternatives[0]  # Select the first alternative
            transcript = alternative.transcript
            confidence = alternative.confidence
            end_time = result.result_end_time.total_seconds()

            # Calculate the start time and duration
            if formatted_results:
                start_time = (
                    formatted_results[-1]["start"] + formatted_results[-1]["duration"]
                )
            else:
                start_time = 0

            duration = end_time - start_time

            formatted_result = {
                "text": transcript,
                "start": start_time,
                "duration": duration,
            }

            formatted_results.append(formatted_result)
        return formatted_results

    def __transcribe_audio_file(self, file_path) -> start_duration_transcript_t:
        client = speech.SpeechClient()

        with io.open(file_path, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz=44100,
            language_code="en-US",
            alternative_language_codes=["zh-CN"],
        )

        response = client.recognize(config=config, audio=audio)

        return response.results
        # return self.__parse_transcripts(response.results)

    def __download_youtube_audio(self, url, output_file):
        cmd = f"yt-dlp --extract-audio --audio-format mp3 --audio-quality 64 --postprocessor-args '-ac 1' '{url}' -o '{output_file}'"
        result = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

        if result.returncode != 0:
            print(f"Error downloading YouTube audio:\n{result.stderr.decode('utf-8')}")
            sys.exit(1)

    def __split_audio_file(self, video_id, chunk_duration_ms) -> List[str]:
        audio = AudioSegment.from_file(video_id + ".mp3")

        chunk_length_ms = chunk_duration_ms
        chunks = make_chunks(audio, chunk_length_ms)

        chunk_files = []

        for i, chunk in enumerate(chunks):
            chunk_name = f"{video_id}_chunk_{i}.mp3"
            chunk.export(chunk_name, format="mp3")
            chunk_files.append(chunk_name)

        return chunk_files

    def __youtube_subtitle(
        self, url: str
    ) -> Tuple[Optional[start_duration_transcript_t], str]:
        """Get the subtitle of the youtube video
        Args:
            url (str): The url of the youtube video
        Returns:
            Tuple[Union[List[Dict[str, str]], None], str]: The subtitle of the youtube video
        """
        video_id = self.get_youtube_id(url)
        try:
            list = YouTubeTranscriptApi.list_transcripts(video_id)
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            return None, ""
        logging.debug(list)

        for transcript in list:
            if transcript.language_code in ["en", "zh", "zh-Hans", "zh-Hant"]:
                return transcript.fetch(), transcript.language
        return None, ""


"""
5/5/23: Older version

    def __youtube_player_list(self, yvid):
        url = f"https://www.youtube.com/watch?v={yvid}"
        response = requests.request("GET", url, headers=headers)
        return response.text


    def __get_text_from_url(self, url: str) -> str:
        response = requests.request("GET", url, headers=headers)
        return response.text


    def __parse_subtitles(self, subtitles) -> List[Dict[str, str]]:
        result = []
        subtitle_lines = subtitles.strip().split('\n')[3:]
        for i in range(0, len(subtitle_lines), 2):
            if ' --> ' not in subtitle_lines[i]:
                continue
            start, end = subtitle_lines[i].split(' --> ')
            text = subtitle_lines[i+1]

            result.append({
                'start': start,
                'end': end,
                'text': text
            })
        return result

    def __parse_requested_subtitles(self, requested_subtitles) -> List[Dict[str, str]]:
        result = []
        subtitle_lines = requested_subtitles.strip().split('\n')[3:]
        for i in range(0, len(subtitle_lines), 1):
            match_timestamp = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})', subtitle_lines[i])
            if not match_timestamp:
                continue
            start = match_timestamp.group(1)
            end = match_timestamp.group(2)
            if self.get_timestamp_diff(start, end) <= 1:
                continue
            text = subtitle_lines[i+1]
            if not re.compile(r'[a-zA-Z]+').search(text):
                continue
            result.append({
                'start': start,
                'end': end,
                'text': text
            })
        return result        


    def __youtube_subtitle(self, url: str) -> List[Dict[str, str]]:
        # options for subtitle extraction
        options = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en', 'zh-Hans'],  # You can add more languages here
            'skip_download': True,  # We don't need to download the video
            'quiet': False  # Suppress console output
        }        
        with yt_dlp.YoutubeDL(options) as ydl:
            result = ydl.extract_info(url, download=False)

        # Extract the subtitles
        subtitles = []
        if 'subtitles' in result:
            print('Found subtitles.')
            for subtitle_list in result['subtitles'].values():
                for subtitle in subtitle_list:
                    if subtitle.get('ext') == 'vtt':
                        text = self.__get_text_from_url(subtitle.get('url'))
                        subtitles.extend(self.__parse_subtitles(text))
        
        if 'requested_subtitles' in result:
            print('Found requested subtitles.')
            requested_subtitles = result.get('requested_subtitles')
            if isinstance(requested_subtitles, dict) and 'en' in requested_subtitles:
                subtitle = requested_subtitles['en']
                if subtitle.get('ext') == 'vtt':
                    print('No subtitles found, fetching requested subtitles.')
                    text = self.__get_text_from_url(subtitle.get('url'))
                    subtitles.extend(self.__parse_requested_subtitles(text))
        print(f'Fetched {len(subtitles)} subtitles.')
        return subtitles


    def __to_subtitle_list(self, subtitles):
        results = []
        for subtitle in subtitles:
            if 'text' in subtitle:
                results.append(subtitle.get('text'))
        return results
"""

