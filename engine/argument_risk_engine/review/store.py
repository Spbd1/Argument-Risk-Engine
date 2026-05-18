from __future__ import annotations

import json
from pathlib import Path

from argument_risk_engine.review.models import ReviewFeedback


def append_feedback(path: Path, feedback: ReviewFeedback) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        handle.write(json.dumps(feedback.model_dump()) + "\n")
