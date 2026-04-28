print(f"LOADING learning_path.py from: {__file__}")
import sys
import os

# ── Point Python to bo's ai_engine folder ────────────────────────
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AI_ENGINE_PATH = os.path.join(BACKEND_DIR, 'ai_engine')
sys.path.insert(0, AI_ENGINE_PATH)

# ── Import bo's master pipeline ───────────────────────────────────
from main import run_ai_pipeline


# ─────────────────────────────────────────────
# HELPER: Convert ta's gap format to bo's format
# ─────────────────────────────────────────────

def _convert_gaps_to_bo_format(gaps: list, gap_severity: str) -> list:
    """
    ta returns gaps as simple strings:
        ["Programming", "Critical Thinking"]

    bo expects gaps as dicts with levels:
        [{"skill": "Programming", "current_level": 0, "required_level": 2}]

    This function converts between the two formats safely.
    Handles strings, dicts, and any unexpected formats.
    """
    severity_to_level = {
        "low":    1,
        "medium": 2,
        "high":   3
    }
    required_level = severity_to_level.get(gap_severity, 2)

    converted = []
    for skill in gaps:

        # Handle if skill is a dict instead of a string
        if isinstance(skill, dict):
            skill_name = (
                skill.get("skill") or
                skill.get("name") or
                skill.get("skill_name") or
                str(skill)
            )

        # Handle normal string
        elif isinstance(skill, str):
            skill_name = skill

        # Handle anything else
        else:
            skill_name = str(skill)

        # Skip empty skills
        if not skill_name or skill_name.strip() == "":
            continue

        converted.append({
            "skill":          skill_name.strip(),
            "current_level":  0,
            "required_level": required_level,
            "gap_size":       required_level
        })

    return converted


# ─────────────────────────────────────────────
# MAIN FUNCTION: generate_learning_path
# Called by views.py with ta's skill gap output
# ─────────────────────────────────────────────

def generate_learning_path(skill_gap_data: dict) -> dict:
    """
    Called by views.py with ta's skill gap output.
    Converts ta's format to bo's format then calls bo's pipeline.

    Args:
        skill_gap_data: dict from ta's analyze_skill_gap()
        {
            "matching_skills": ["Critical Thinking"],
            "gaps": ["Programming", "Troubleshooting"],
            "gap_severity": "high",
            "job_title": "Software Developer"
        }

    Returns:
        {
            "steps": [...],
            "reasoning_trace": "...",
            "summary": {...}
        }
    """

    # Step 1: Extract data from ta's output
    gaps         = skill_gap_data.get("gaps", [])
    gap_severity = skill_gap_data.get("gap_severity", "medium")
    job_title    = skill_gap_data.get("job_title", "Professional Role")

    # Step 2: If no gaps found return empty result
    if not gaps:
        return {
            "steps": [],
            "reasoning_trace": "No skill gaps found. Candidate is a great match!",
            "summary": {
                "original_gaps": 0,
                "total_steps": 0,
                "total_weeks": 0
            }
        }

    # Step 3: Convert ta's simple string gaps to bo's dict format
    bo_gaps = _convert_gaps_to_bo_format(gaps, gap_severity)

    # Debug print — remove after testing
    print("bo_gaps being sent:", bo_gaps)

    # Step 4: If conversion resulted in empty list return safe response
    if not bo_gaps:
        return {
            "steps": [],
            "reasoning_trace": "Could not process skill gaps.",
            "summary": {}
        }

    # Step 5: Call bo's master pipeline
    try:
        result = run_ai_pipeline(bo_gaps, job_title)
    except Exception as e:
        raise Exception(f"bo pipeline crashed: {str(e)}")

    # Step 6: Check if bo's pipeline succeeded
    if not result.get("success"):
        raise Exception(
            "bo pipeline failed: " + result.get("error", "unknown error")
        )

    # Step 7: Return clean result to views.py
    return {
        "steps":           result.get("learning_path", []),
        "reasoning_trace": result.get("reasoning_trace", ""),
        "summary":         result.get("summary", {})
    }