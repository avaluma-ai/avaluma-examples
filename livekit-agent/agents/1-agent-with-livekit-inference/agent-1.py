import os

# highlight-next-line
from livekit.plugins.avaluma import AvatarSession
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    TurnHandlingOptions,
    cli,
    inference,
    room_io,
)
from livekit.plugins import noise_cancellation

load_dotenv(".env.local")
agent_name = "agent-1"
avatar_id = "260218-Avaluma_Avatar_Kadda_v5"
license_key = os.getenv("AVALUMA_LICENSE_KEY", "")
avatar_server_url = os.getenv("AVATAR_SERVER_URL", "https://api.avaluma.ai")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful virtual AI assistant. The user is interacting with you via voice, even if you perceive the conversation as text.
            You eagerly assist users with their questions by providing information from your extensive knowledge.
            Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
            You are curious, friendly, and have a sense of humor.""",
        )


server = AgentServer()


@server.rtc_session(agent_name=agent_name)
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
        # VAD: AgentSession uses the bundled Silero VAD by default
        turn_handling=TurnHandlingOptions(
            turn_detection=inference.TurnDetector(),
            preemptive_generation={"enabled": True},
        ),
    )

    if not license_key:
        raise ValueError("AVALUMA_LICENSE_KEY is not set")

    # highlight-start
    avatar = AvatarSession(
        license_key=license_key,  # Your License Key
        avatar_id=avatar_id,  # Avatar identifier (Name of .hvia file)
        avatar_server_url=avatar_server_url,
    )
    # Start the avatar and wait for it to join
    await avatar.start(agent_session=session, room=ctx.room)
    # highlight-end

    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        ),
    )
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)
