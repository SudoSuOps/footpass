# GPU support

**A GPU is not required.** FootPass v1 uses `NoAIProvider` — no model is
downloaded or run. The GPU is only relevant to a *future* local multimodal
vision service.

## Detect the GPU

```bash
make gpu-check      # or: bash scripts/detect-gpu.sh
```

Reports name, driver, CUDA/VRAM, temperature, and power. It also writes
`${FOOTPASS_DATA_DIR}/hardware.json`, which the API reads to show the GPU on the
System Health page. Supported on this box: NVIDIA T1000 · RTX A2000 · RTX 2000
Ada 16GB · RTX 4000 SFF · external RTX 3090 over OCuLink · or none.

## Where a future model service connects

`worker/app/vision.py` defines the interface:

```python
class VisionProvider:
    def analyze_image(...): ...
    def compare_images(...): ...
    def health_check(...): ...
```

Providers:
- **`NoAIProvider`** — default in v1. No AI.
- **`LocalGPUProvider`** — a model served on *this* box's GPU (e.g. vLLM/llama.cpp
  serving a local multimodal model). Point it at a local endpoint.
- **`RemoteLocalNetworkProvider`** — a model service elsewhere on the LAN (e.g.
  the Foundry rig). LAN-only, no cloud.

To enable later: implement one provider, set `FOOTPASS_VISION_PROVIDER` for the
worker, and (optionally) run the stack with the GPU profile:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile gpu up -d
```

This requires the host `nvidia-container-toolkit`. **FootPass does not download
MedGemma or any model automatically** — that is always an explicit, separate step.
