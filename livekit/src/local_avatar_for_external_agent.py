import os

from avaluma_livekit_plugin import LocalAvatarSession
from dotenv import load_dotenv
from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
)

load_dotenv(".env.local")
agent_name = os.getenv("AGENT_NAME", "")
license_key = os.getenv("LICENSE_KEY", "")


async def entrypoint(ctx: JobContext):
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    avatar = LocalAvatarSession(
        license_key=license_key,
        avatar_id="2025-09-06-Kadda_very_long_DS_v2_release_v5_gcs",  # Avatar identifier
        assets_dir=os.path.join(os.path.dirname(__file__), "..", "assets"),
    )
    await avatar.start(room=ctx.room)

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint, job_memory_warn_mb=4096, agent_name=agent_name
        )
    )
