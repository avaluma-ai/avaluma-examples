import sys

from avaluma_livekit_plugin import LocalAvatarSession
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel


async def entrypoint(ctx: JobContext):
    pass


if __name__ == "__main__":
    sys.argv.append("download-files")
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
