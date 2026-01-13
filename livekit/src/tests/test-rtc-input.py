"""
Stream audio files to LiveKit room using RTC SDK directly.
Much faster than WHIP - connects once and can play multiple times with minimal latency.
"""

import argparse
import asyncio
import logging
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from livekit import api, rtc

load_dotenv(".env.local")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioStreamer:
    def __init__(self, room_name: str):
        self.room_name = room_name
        self.room = rtc.Room()
        self.audio_source = rtc.AudioSource(24000, 1)  # 24kHz, mono
        self.is_connected = False
        self.is_publishing = False
        self.current_track = None

    async def connect(self):
        """Connect to the LiveKit room once"""
        if self.is_connected:
            logger.info("Already connected")
            return

        livekit_url = os.environ.get("LIVEKIT_URL")
        livekit_api_key = os.environ.get("LIVEKIT_API_KEY")
        livekit_api_secret = os.environ.get("LIVEKIT_API_SECRET")

        if not all([livekit_url, livekit_api_key, livekit_api_secret]):
            raise ValueError("Missing LiveKit credentials in environment")

        # Generate a token for this participant
        token = (
            api.AccessToken(api_key=livekit_api_key, api_secret=livekit_api_secret)
            .with_identity("external-agent-ingress" + str(uuid.uuid4()))
            .with_name("Audio Streamer")
            .with_grants(api.VideoGrants(room_join=True, room=self.room_name))
            .to_jwt()
        )

        logger.info(f"Connecting to room: {self.room_name}")
        await self.room.connect(livekit_url, token)
        self.is_connected = True
        logger.info("✓ Connected to room")

        # Publish the audio track
        track_options = rtc.TrackPublishOptions(
            source=rtc.TrackSource.SOURCE_MICROPHONE
        )
        track = rtc.LocalAudioTrack.create_audio_track(
            "streamed-audio", self.audio_source
        )
        self.current_track = track

        publication = await self.room.local_participant.publish_track(
            track, track_options
        )
        self.is_publishing = True
        logger.info(f"✓ Published audio track: {publication.sid}")

    async def play_file(self, file_path: str):
        """Play an audio file through the existing connection"""
        if not self.is_connected:
            raise RuntimeError("Not connected. Call connect() first.")

        logger.info(f"Playing: {file_path}")

        # Use ffmpeg to read and resample the audio file
        import subprocess

        import numpy as np

        # Get audio duration first
        duration_cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            file_path,
        ]
        try:
            result = subprocess.run(
                duration_cmd, capture_output=True, text=True, check=True
            )
            duration = float(result.stdout.strip())
            logger.info(f"Audio duration: {duration:.2f}s")
        except Exception as e:
            logger.warning(f"Could not get duration: {e}")
            duration = None

        # Stream audio with ffmpeg
        ffmpeg_cmd = [
            "ffmpeg",
            "-i",
            file_path,
            "-f",
            "s16le",  # 16-bit signed PCM
            "-acodec",
            "pcm_s16le",
            "-ar",
            "24000",  # 24kHz sample rate
            "-ac",
            "1",  # mono
            "-",  # output to stdout
        ]

        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

        frame_size = 480  # 20ms at 24kHz
        bytes_per_frame = frame_size * 2  # 16-bit = 2 bytes per sample

        try:
            while True:
                data = process.stdout.read(bytes_per_frame)
                if not data:
                    break

                # Convert bytes to numpy array
                audio_data = np.frombuffer(data, dtype=np.int16)

                # Pad if necessary
                if len(audio_data) < frame_size:
                    audio_data = np.pad(audio_data, (0, frame_size - len(audio_data)))

                # Create AudioFrame and capture it
                frame = rtc.AudioFrame(
                    data=audio_data.tobytes(),
                    sample_rate=24000,
                    num_channels=1,
                    samples_per_channel=frame_size,
                )

                await self.audio_source.capture_frame(frame)

        finally:
            process.terminate()
            process.wait()
            logger.info("✓ Finished playing")

    async def disconnect(self):
        """Disconnect from the room"""
        if self.is_connected:
            await self.room.disconnect()
            self.is_connected = False
            logger.info("Disconnected from room")


async def main():
    parser = argparse.ArgumentParser(
        description="Stream audio to LiveKit room using RTC SDK (fast, reusable connection)."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="test_data/hello_world.mp3",
        help="Path to the audio file to stream",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        raise ValueError(f"Input file not found: {args.input_file}")

    # Interactive room name input
    loop = asyncio.get_event_loop()
    room_name = await loop.run_in_executor(None, input, "Enter LiveKit room name: ")
    room_name = room_name.strip()

    if not room_name:
        raise ValueError("Room name cannot be empty")

    streamer = AudioStreamer(room_name)

    try:
        # Connect once
        await streamer.connect()

        # Play audio on demand
        while True:
            loop = asyncio.get_event_loop()
            input_value = await loop.run_in_executor(
                None, input, "\nPress Enter to play audio... or 'q' to quit: "
            )

            if input_value.strip().lower() == "q":
                break

            # Play the file (instant - no reconnection needed!)
            await streamer.play_file(args.input_file)

    finally:
        await streamer.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
