import os

# highlight-next-line
from avaluma_livekit_plugin import AvatarSession
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
avatar_id = os.getenv("AVATAR_ID", "260218-Avaluma_Avatar_Kadda_v1")
license_key = os.getenv("AVALUMA_LICENSE_KEY", "")
avatar_server_url = os.getenv("AVATAR_SERVER_URL", "http://avaluma-avatar-server:8888")


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

    if license_key is None:
        raise ValueError("AVALUMA_LICENSE_KEY is not set")

    # highlight-start
    avatar = AvatarSession(
        license_key=license_key,  # Your License Key
        avatar_id=avatar_id,  # Avatar identifier (Name of .hvia file)
        avaluma_server_url=avatar_server_url,
    )
    # Start the avatar and wait for it to join
    await avatar.start(agent_session=session, room=ctx.room)
    # highlight-end

    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
        # highlight-next-line
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
