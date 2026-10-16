# Onboarding

Welcome to Mobile Service Suite. Read this end-to-end before touching a device.

## Day 1 — environment

```bash
git clone <your-fork> mobile-service-suite
cd mobile-service-suite
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
pytest -q