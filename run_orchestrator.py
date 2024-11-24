import asyncio
from src.orchestrator import process_submitted_video


async def process(video_id: str):
    print(f"Processing video ID: {video_id}")
    await process_submitted_video(video_id)


if __name__ == "__main__":
    asyncio.run(process("67430d2d5ed8d665005a5361"))
