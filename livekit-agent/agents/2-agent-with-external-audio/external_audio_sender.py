"""
Simulates an external audio service that sends audio directly to the avatar
via LiveKit DataStream — without any access to AgentSession or the agent pipeline.

In production this would be a completely separate process or microservice that
independently connects to the LiveKit room and streams audio to the avatar.
"""

import asyncio
import os
import uuid
import wave

from livekit import api, rtc

# Same topic as DataStreamAudioOutput uses internally
AUDIO_STREAM_TOPIC = "lk.audio_stream"
WAV_PATH = os.path.join(os.path.dirname(__file__), "assets/hello_world_16kHz.wav")


def _load_wav_data(path: str) -> tuple[bytes, int, int]:
    with wave.open(path, "rb") as wf:
        sample_rate = wf.getframerate()
        num_channels = wf.getnchannels()
        raw_data = wf.readframes(wf.getnframes())
    return raw_data, sample_rate, num_channels


async def _wait_for_avatar(room: rtc.Room) -> rtc.RemoteParticipant:
    """Return the avatar participant as soon as it appears in the room."""
    for p in room.remote_participants.values():
        if p.identity.startswith("avatar-"):
            return p

    loop = asyncio.get_running_loop()
    fut: asyncio.Future[rtc.RemoteParticipant] = loop.create_future()

    def _on_participant_connected(participant: rtc.RemoteParticipant) -> None:
        if participant.identity.startswith("avatar-") and not fut.done():
            fut.set_result(participant)

    room.on("participant_connected", _on_participant_connected)
    try:
        return await fut
    finally:
        room.off("participant_connected", _on_participant_connected)


async def run(room_name: str, interval: float = 5.0) -> None:
    """
    Create a token, connect to the LiveKit room as an independent participant,
    and send WAV audio directly to the avatar via DataStream every `interval` seconds.

    This bypasses AgentSession entirely — the token is the only thing needed.
    """
    livekit_url = os.getenv("LIVEKIT_URL", "")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY", "")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET", "")

    # Independent token for this sender — no AgentSession involved
    token = (
        api.AccessToken(api_key=livekit_api_key, api_secret=livekit_api_secret)
        .with_identity("external-audio-sender")
        .with_name("External Audio Sender")
        .with_grants(api.VideoGrants(room_join=True, room=room_name))
        .with_kind("agent")  # AGENT kind so DataStreamAudioReceiver on the avatar recognizes this participant
        .to_jwt()
    )

    room = rtc.Room()
    await room.connect(livekit_url, token)

    # Suppress "no callback attached" log: agent-kind participants receive lk.agent.session
    # streams from the framework which we don't need to handle here.
    room.register_byte_stream_handler("lk.agent.session", lambda _reader, _identity: None)

    raw_data, sample_rate, num_channels = _load_wav_data(WAV_PATH)
    avatar = await _wait_for_avatar(room)

    while True:
        await asyncio.sleep(interval)

        # Mirrors exactly what DataStreamAudioOutput.capture_frame() + flush() does internally
        writer = await room.local_participant.stream_bytes(
            name=f"AUDIO_{uuid.uuid4().hex[:8]}",
            topic=AUDIO_STREAM_TOPIC,
            destination_identities=[avatar.identity],
            attributes={
                "sample_rate": str(sample_rate),
                "num_channels": str(num_channels),
            },
        )
        await writer.write(raw_data)
        await writer.aclose()  # closing the stream = flush / end of segment
