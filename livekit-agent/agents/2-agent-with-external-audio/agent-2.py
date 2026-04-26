import asyncio
import os

import external_audio_sender
from avaluma_livekit_plugin import AvatarSession
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
)

load_dotenv(".env.local")
agent_name = "agent-2"
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


async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    session = AgentSession()

    if license_key is None:
        raise ValueError("AVALUMA_LICENSE_KEY is not set")

    avatar = AvatarSession(
        license_key=license_key,  # Your License Key
        avatar_id=avatar_id,  # Avatar identifier (Name of .hvia file)
        avatar_server_url=avatar_server_url,
    )
    await avatar.start(agent_session=session, room=ctx.room)

    await session.start(
        agent=Assistant(),
        room=ctx.room,
    )
    await ctx.connect()

    # Audio from an external service via DataStream, bypassing AgentSession.
    # In production, external_audio_sender.run() would live in a separate process/service
    # and connect to the room independently — started here only for local simulation.
    asyncio.create_task(external_audio_sender.run(ctx.room.name))


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint,
            agent_name=agent_name,
        )
    )
