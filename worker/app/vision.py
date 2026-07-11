"""Modular AI vision interface.

FootPass version 1 ships with NoAIProvider — NO model is downloaded or required.
A future local multimodal model service (e.g. MedGemma running on the T1000 /
Jetson) would connect through LocalGPUProvider or RemoteLocalNetworkProvider.
See docs/gpu-support.md for the integration point.

Nothing here makes medical diagnoses.
"""
from __future__ import annotations

from typing import Any, Protocol


class VisionProvider(Protocol):
    def analyze_image(self, image_path: str, **kwargs: Any) -> dict: ...
    def compare_images(self, path_a: str, path_b: str, **kwargs: Any) -> dict: ...
    def health_check(self) -> dict: ...


class NoAIProvider:
    """Default. Organizes and compares images with NO AI/model involvement."""

    name = "none"

    def analyze_image(self, image_path: str, **kwargs: Any) -> dict:
        return {"provider": self.name, "analysis": None, "note": "AI disabled in v1."}

    def compare_images(self, path_a: str, path_b: str, **kwargs: Any) -> dict:
        return {"provider": self.name, "comparison": None, "note": "AI disabled in v1."}

    def health_check(self) -> dict:
        return {"provider": self.name, "status": "ok", "ai_enabled": False}


class LocalGPUProvider:
    """Stub: a local model served on this box's GPU (e.g. via vLLM). Not wired in v1."""

    name = "local_gpu"

    def __init__(self, endpoint: str | None = None) -> None:
        self.endpoint = endpoint

    def analyze_image(self, image_path: str, **kwargs: Any) -> dict:
        raise NotImplementedError("LocalGPUProvider is a stub for a future phase.")

    def compare_images(self, path_a: str, path_b: str, **kwargs: Any) -> dict:
        raise NotImplementedError("LocalGPUProvider is a stub for a future phase.")

    def health_check(self) -> dict:
        return {"provider": self.name, "status": "not_configured", "endpoint": self.endpoint}


class RemoteLocalNetworkProvider:
    """Stub: a model service elsewhere on the LAN (e.g. the Foundry rig). Not wired in v1."""

    name = "remote_local_network"

    def __init__(self, endpoint: str | None = None) -> None:
        self.endpoint = endpoint

    def analyze_image(self, image_path: str, **kwargs: Any) -> dict:
        raise NotImplementedError("RemoteLocalNetworkProvider is a stub for a future phase.")

    def compare_images(self, path_a: str, path_b: str, **kwargs: Any) -> dict:
        raise NotImplementedError("RemoteLocalNetworkProvider is a stub for a future phase.")

    def health_check(self) -> dict:
        return {"provider": self.name, "status": "not_configured", "endpoint": self.endpoint}


def get_provider(name: str = "none") -> VisionProvider:
    return {
        "none": NoAIProvider,
        "local_gpu": LocalGPUProvider,
        "remote_local_network": RemoteLocalNetworkProvider,
    }.get(name, NoAIProvider)()
