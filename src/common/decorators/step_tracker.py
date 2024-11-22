from functools import wraps
from datetime import datetime
import pytz
import traceback
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


class StepInProgressError(Exception):
    """Custom exception for step already in progress"""
    pass


class StepDependencyError(Exception):
    """Custom exception for dependency validation failures"""
    pass


class StepTracker:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.ist_timezone = pytz.timezone("Asia/Kolkata")

    async def _get_video_status(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Fetch video processing status from database"""
        return await self.db.videos.find_one({"_id": ObjectId(video_id)})

    async def _check_step_in_progress(self, video_id: str, step_name: str) -> None:
        """Check if step is already in progress or completed"""
        video_status = await self._get_video_status(video_id)
        if video_status:
            steps_status = video_status.get("steps_status", {})
            if steps_status.get(f"{step_name}_inProgress") or steps_status.get(f"{step_name}_completed"):
                raise StepInProgressError(
                    f"Step '{step_name}' is already in progress or completed for video {video_id}")

    async def _log_error(self, video_id: str, step_name: str, error_logs: str) -> None:
        """Log error to pipeline_errors collection"""
        await self.db.pipeline_errors.insert_one({
            "video_id": ObjectId(video_id),
            "step_name": step_name,
            "error_logs": error_logs,
            "error_timestamp": datetime.now(self.ist_timezone)
        })

    async def _update_step_status(
        self,
        video_id: str,
        step_name: str,
        status: Dict[str, bool],
        timestamp_key: str,
        unset_status: Optional[Dict[str, bool]] = {},
        execution_time: Optional[float] = None
    ):
        """Update step status in database"""
        set_dict = {
            f"timestamps.{timestamp_key}": datetime.now(self.ist_timezone)
        }

        # Update status flags
        for status_key, status_value in status.items():
            set_dict[f"steps_status.{status_key}"] = status_value

        if execution_time is not None:
            set_dict[f"execution_times.{step_name}"] = execution_time

        # Unset status flags
        unset_dict = {}
        for unset_key, unset_value in unset_status.items():
            unset_dict[f"steps_status.{unset_key}"] = unset_value

        update_dict = {
            "$set": set_dict
        }

        if unset_dict:
            update_dict["$unset"] = unset_dict

        if unset_dict:
            await self.db.videos.update_one(
                {"_id": ObjectId(video_id)},
                update_dict,
                upsert=True
            )
        # # Remove in_progress flag if step is completed
        # if f"{step_name}_completed" in status and status[f"{step_name}_completed"]:
        #     await self.db.videos.update_one(
        #         {"_id": ObjectId(video_id)},
        #         {
        #             "$set": update_dict,
        #             "$unset": {f"steps_status.{step_name}_inProgress": "", f"steps_status.{step_name}_error": ""}
        #         },
        #         upsert=True
        #     )
        # else:
        #     await self.db.videos.update_one(
        #         {"_id": ObjectId(video_id)},
        #         {"$set": update_dict},
        #         upsert=True
        #     )

    async def _validate_dependencies(self, video_id: str, step_name: str) -> None:
        """Validate step dependencies before execution"""
        from ..static import STEP_DEPENDENCIES

        if step_name in STEP_DEPENDENCIES:
            video_status = await self._get_video_status(video_id)
            if not video_status:
                raise StepDependencyError(f"No video found with id {video_id}")

            for dep_step in STEP_DEPENDENCIES[step_name]:
                if not video_status.get("steps_status", {}).get(f"{dep_step}_completed"):
                    raise StepDependencyError(
                        f"Dependency '{dep_step}' not completed for step '{
                            step_name}'"
                    )


def track_step(func):
    """
    Decorator to track execution of video processing steps
    """
    @wraps(func)
    async def wrapper(video_id: str, db: AsyncIOMotorDatabase, *args, **kwargs):
        step_name = func.__name__
        tracker = StepTracker(db)

        # Check if step is already in progress
        try:
            await tracker._check_step_in_progress(video_id, step_name)
            await tracker._validate_dependencies(video_id, step_name)
        except (StepInProgressError, StepDependencyError) as e:
            await tracker._log_error(video_id, step_name, str(e))
            await tracker._update_step_status(
                video_id,
                step_name,
                {f"{step_name}_completed": False, f"{step_name}_error": True},
                f"{step_name}_error_time"
            )
            raise

        # Set in-progress flag
        start_time = datetime.now(tracker.ist_timezone)
        await tracker._update_step_status(
            video_id,
            step_name,
            {f"{step_name}_inProgress": True},
            f"{step_name}_start_time",
            {f"{step_name}_completed": "", f"{step_name}_error": ""}
        )

        try:
            # Execute the step
            result = await func(video_id=video_id, db=db, *args, **kwargs)

            # Record successful completion
            end_time = datetime.now(tracker.ist_timezone)
            execution_time = (end_time - start_time).total_seconds()

            await tracker._update_step_status(
                video_id,
                step_name,
                {f"{step_name}_completed": True},
                f"{step_name}_end_time",
                {f"{step_name}_inProgress": ""},
                execution_time=execution_time
            )

            return result

        except Exception as e:
            # Record error and log to pipeline_errors
            error_time = datetime.now(tracker.ist_timezone)
            error_message = f"{str(e)}\n{traceback.format_exc()}"

            await tracker._log_error(video_id, step_name, error_message)
            await tracker._update_step_status(
                video_id,
                step_name,
                {f"{step_name}_completed": False, f"{step_name}_error": True},
                f"{step_name}_error_time",
                {f"{step_name}_inProgress": ""},
                execution_time=(error_time - start_time).total_seconds()
            )
            raise

    return wrapper
