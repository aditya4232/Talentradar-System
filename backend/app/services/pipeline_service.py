"""
Pipeline Service: Manages hiring pipeline stage transitions, SLA tracking, activity logging.
"""

from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Stage order for funnel tracking
STAGE_ORDER = [
    "SOURCED", "APPROACHED", "RESPONDED", "SCREENING_SCHEDULED",
    "SCREENING_DONE", "SHORTLISTED", "L1_INTERVIEW", "L2_INTERVIEW",
    "OFFER_SENT", "OFFER_ACCEPTED", "JOINED"
]

TERMINAL_STAGES = ["REJECTED", "ON_HOLD"]

# SLA days per stage (days to complete before escalation)
STAGE_SLA_DAYS = {
    "SOURCED": 3,
    "APPROACHED": 5,
    "RESPONDED": 2,
    "SCREENING_SCHEDULED": 3,
    "SCREENING_DONE": 2,
    "SHORTLISTED": 5,
    "L1_INTERVIEW": 7,
    "L2_INTERVIEW": 7,
    "OFFER_SENT": 5,
    "OFFER_ACCEPTED": 30,
    "JOINED": None,
}

STAGE_DISPLAY_NAMES = {
    "SOURCED": "Sourced",
    "APPROACHED": "Approached",
    "RESPONDED": "Responded",
    "SCREENING_SCHEDULED": "Screening Scheduled",
    "SCREENING_DONE": "Screening Done",
    "SHORTLISTED": "Shortlisted",
    "L1_INTERVIEW": "L1 Interview",
    "L2_INTERVIEW": "L2 Interview",
    "OFFER_SENT": "Offer Sent",
    "OFFER_ACCEPTED": "Offer Accepted",
    "JOINED": "Joined",
    "REJECTED": "Rejected",
    "ON_HOLD": "On Hold",
}


def get_stage_index(stage: str) -> int:
    try:
        return STAGE_ORDER.index(stage)
    except ValueError:
        return -1


def is_valid_transition(from_stage: str, to_stage: str) -> tuple[bool, str]:
    """Check if a stage transition is valid."""
    if to_stage in TERMINAL_STAGES:
        return True, "ok"
    if from_stage in TERMINAL_STAGES and to_stage not in TERMINAL_STAGES:
        # Allow revival from on_hold
        if from_stage == "ON_HOLD":
            return True, "ok"
        return False, f"Cannot move from {from_stage} to {to_stage}"

    from_idx = get_stage_index(from_stage)
    to_idx = get_stage_index(to_stage)

    if from_idx == -1 or to_idx == -1:
        return True, "ok"  # Unknown stages, allow

    # Allow forward or backward movement (for corrections)
    return True, "ok"


def compute_sla_status(entry_updated_at: datetime, current_stage: str) -> dict:
    """Compute SLA status for a pipeline entry."""
    sla_days = STAGE_SLA_DAYS.get(current_stage)
    if not sla_days:
        return {"status": "N/A", "days_remaining": None, "overdue": False}

    if not entry_updated_at:
        return {"status": "unknown", "days_remaining": None, "overdue": False}

    deadline = entry_updated_at + timedelta(days=sla_days)
    now = datetime.utcnow()
    days_remaining = (deadline - now).days

    if days_remaining < 0:
        return {"status": "overdue", "days_remaining": days_remaining, "overdue": True}
    elif days_remaining <= 1:
        return {"status": "urgent", "days_remaining": days_remaining, "overdue": False}
    elif days_remaining <= 3:
        return {"status": "warning", "days_remaining": days_remaining, "overdue": False}
    else:
        return {"status": "ok", "days_remaining": days_remaining, "overdue": False}


def compute_funnel_data(pipeline_entries: list) -> list:
    """Compute funnel conversion data from pipeline entries."""
    stage_counts = {stage: 0 for stage in STAGE_ORDER + TERMINAL_STAGES}

    for entry in pipeline_entries:
        stage = entry.stage if hasattr(entry, "stage") else entry.get("stage")
        if stage in stage_counts:
            stage_counts[stage] += 1

    funnel = []
    for stage in STAGE_ORDER:
        funnel.append({
            "stage": stage,
            "display_name": STAGE_DISPLAY_NAMES.get(stage, stage),
            "count": stage_counts[stage],
        })
    return funnel


def get_priority_actions(pipeline_entries: list, jobs: list) -> list:
    """Generate today's priority action list for the recruiter dashboard."""
    priorities = []
    now = datetime.utcnow()

    for entry in pipeline_entries:
        stage = entry.stage if hasattr(entry, "stage") else entry.get("stage")
        updated_at = entry.updated_at if hasattr(entry, "updated_at") else entry.get("updated_at")
        candidate = entry.candidate if hasattr(entry, "candidate") else entry.get("candidate", {})
        job = entry.job if hasattr(entry, "job") else entry.get("job", {})

        if stage in TERMINAL_STAGES:
            continue

        sla = compute_sla_status(updated_at, stage)

        if sla["overdue"] or sla["status"] in ("urgent", "warning"):
            candidate_name = getattr(candidate, "name", None) or (candidate.get("name") if isinstance(candidate, dict) else "Unknown")
            job_title = getattr(job, "title", None) or (job.get("title") if isinstance(job, dict) else "Unknown")

            priorities.append({
                "type": "sla_alert",
                "priority": "high" if sla["overdue"] else "medium",
                "message": f"Follow up with {candidate_name} for {job_title} - stage: {STAGE_DISPLAY_NAMES.get(stage, stage)}",
                "sla_status": sla,
                "candidate_name": candidate_name,
                "job_title": job_title,
                "stage": stage,
            })

    # Sort by priority
    priorities.sort(key=lambda x: 0 if x["priority"] == "high" else 1)
    return priorities[:10]
