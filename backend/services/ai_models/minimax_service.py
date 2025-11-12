"""
Minimax Video Generation Service
"""
from __future__ import annotations

import os
import time
import uuid
from typing import Optional

import requests
from loguru import logger

from core.config import settings


class MinimaxVideoService:
    """Generate videos using Minimax text-to-video API."""

    def __init__(self) -> None:
        self.api_key = settings.MINIMAX_API_KEY
        self.base_url = settings.MINIMAX_BASE_URL.rstrip("/")
        self.model = settings.MINIMAX_MODEL
        self.poll_interval = settings.MINIMAX_POLL_INTERVAL
        self.max_wait = settings.MINIMAX_MAX_WAIT

        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY not set in environment")

    def generate(self, prompt: str, duration: int, resolution: str) -> str:
        """Trigger video generation and download the resulting file."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "duration": duration,
            "resolution": resolution,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        logger.info(f"Calling Minimax API with model={self.model}, duration={duration}, resolution={resolution}")
        response = requests.post(
            f"{self.base_url}/video_generation",
            json=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        video_url = self._extract_video_url(data)
        task_id = data.get("task_id") or data.get("id")

        if not video_url and task_id:
            logger.info(f"Polling Minimax task {task_id}")
            video_url = self._poll_for_video(task_id, headers)

        if not video_url:
            raise ValueError("Minimax did not return a video URL")

        return self._download_video(video_url)

    def _poll_for_video(self, task_id: str, headers: dict) -> Optional[str]:
        """Poll Minimax for a finished video."""
        poll_url = f"{self.base_url}/video_generation/{task_id}"
        waited = 0.0

        while waited < self.max_wait:
            time.sleep(self.poll_interval)
            waited += self.poll_interval

            resp = requests.get(poll_url, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            video_url = self._extract_video_url(data)
            status = data.get("status")
            if video_url:
                return video_url
            if status in {"failed", "canceled"}:
                raise ValueError(f"Minimax task {task_id} failed with status {status}")

            logger.debug(f"Awaiting Minimax task {task_id}, status={status}")

        raise TimeoutError(f"Minimax task {task_id} timed out after {self.max_wait} seconds")

    @staticmethod
    def _extract_video_url(data: dict) -> Optional[str]:
        """Try to find a video URL in Minimax response."""
        if not data:
            return None
        # Direct field
        if isinstance(data.get("video_url"), str):
            return data["video_url"]
        # Nested outputs
        result = data.get("result") or data.get("data") or {}
        if isinstance(result, dict):
            videos = result.get("videos") or result.get("video_list") or []
            if isinstance(videos, list) and videos:
                first = videos[0]
                if isinstance(first, str):
                    return first
                if isinstance(first, dict):
                    return first.get("url") or first.get("video_url")
        return None

    def _download_video(self, video_url: str) -> str:
        """Download video from URL and store in outputs directory."""
        logger.info(f"Downloading Minimax video from {video_url}")
        resp = requests.get(video_url, timeout=120)
        resp.raise_for_status()

        filename = f"video_minimax_{uuid.uuid4().hex[:16]}.mp4"
        output_path = os.path.join(settings.OUTPUT_DIR, filename)
        with open(output_path, "wb") as f:
            f.write(resp.content)

        logger.info(f"Video downloaded to {output_path}")
        return output_path


