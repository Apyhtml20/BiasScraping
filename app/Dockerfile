FROM python:3.12-slim

# opencv needs these system libs to import at runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /srv

# This image has no GPU: skip torch's CUDA wheel + its nvidia-*/triton
# dependencies (several GB, otherwise pulled in unconditionally by uv.lock)
# and install the CPU-only build instead.
ARG SKIP_CUDA="--no-install-package torch --no-install-package torchvision \
    --no-install-package triton --no-install-package nvidia-cublas \
    --no-install-package nvidia-cuda-cupti --no-install-package nvidia-cuda-nvrtc \
    --no-install-package nvidia-cuda-runtime --no-install-package nvidia-cudnn-cu13 \
    --no-install-package nvidia-cufft --no-install-package nvidia-cufile \
    --no-install-package nvidia-curand --no-install-package nvidia-cusolver \
    --no-install-package nvidia-cusparse --no-install-package nvidia-cusparselt-cu13 \
    --no-install-package nvidia-ml-py --no-install-package nvidia-nccl-cu13 \
    --no-install-package nvidia-nvjitlink --no-install-package nvidia-nvshmem-cu13 \
    --no-install-package nvidia-nvtx"

# --inexact: uv sync prunes anything not in its own target set by default,
# which would otherwise immediately remove the CPU torch installed right after it.
# Install dependencies first so this layer is cached across source changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev --inexact $SKIP_CUDA \
    && uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

COPY app ./app

RUN uv sync --frozen --no-dev --inexact $SKIP_CUDA

EXPOSE 8000

# --no-sync: `uv run` normally re-syncs against uv.lock before every invocation,
# which would re-trigger the CUDA download this Dockerfile just avoided.
CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
