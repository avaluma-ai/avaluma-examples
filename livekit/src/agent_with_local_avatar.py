import os

from avaluma_livekit_plugin import LocalAvatarSession
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    RoomOutputOptions,
    WorkerOptions,
    cli,
    inference,
)
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv(".env.local")
agent_name = os.getenv("AGENT_NAME", "")
license_key = os.getenv("AVALUMA_LICENSE_KEY", "")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful virtual AI assistant. The user is interacting with you via voice, even if you perceive the conversation as text.
            You eagerly assist users with their questions by providing information from your extensive knowledge.
            Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
            You are curious, friendly, and have a sense of humor.""",
        )


async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    session = AgentSession(
        stt=inference.STT(model="assemblyai/universal-streaming", language="en"),
        llm=inference.LLM(model="openai/gpt-4.1-mini"),
        tts=inference.TTS(
            model="cartesia/sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    avatar = LocalAvatarSession(
        license_key=license_key,  # Your License Key
        avatar_id="2025-09-06-Kadda_very_long_DS_v2_release_v5_gcs",  # Avatar identifier (Name of .hvia file)
        assets_dir=os.path.join(
            os.path.dirname(__file__), "..", "assets"
        ),  # Path to the assets directory with .hvia files
    )
    # Start the avatar and wait for it to join
    await avatar.start(agent_session=session, room=ctx.room)

    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
        room_output_options=RoomOutputOptions(audio_enabled=False),
    )
    await ctx.connect()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint,
            prewarm_fnc=prewarm,
            job_memory_warn_mb=4096,
            agent_name=agent_name,
        )
    )
