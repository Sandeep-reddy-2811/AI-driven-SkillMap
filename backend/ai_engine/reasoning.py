# reasoning.py
import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"


def generate_reasoning_trace(
    original_gaps,
    expanded_gaps,
    learning_path,
    job_title
):
    """
    Generate a human-readable reasoning trace explaining:
    - Why this path was created
    - Why prerequisites were added
    - Why the order makes sense
    - What the candidate achieves at the end
    """

    # Prepare data for prompt
    original_text = json.dumps(original_gaps, indent=2)
    expanded_text = json.dumps(expanded_gaps, indent=2)

    path_summary = []
    for step in learning_path:
        path_summary.append(
            f"Step {step['step_number']}: "
            f"{step['course_title']} ({step['level']}, "
            f"{step['duration_weeks']} week)"
        )
    path_text = "\n".join(path_summary)

    total_weeks = sum(s.get("duration_weeks", 0) for s in learning_path)

    prompt = f"""
You are an expert corporate learning coach writing a 
professional onboarding report.

A new hire is targeting the role of: {job_title}

Their ORIGINAL skill gaps identified from resume:
{original_text}

After prerequisite analysis, EXPANDED gaps became:
{expanded_text}

The personalized learning path generated:
{path_text}

Total duration: {total_weeks} weeks

Write a professional reasoning trace that explains:
1. What skills the candidate is currently missing
2. Why certain prerequisite skills were automatically added
3. Why the learning path is ordered the way it is
4. How this path is more efficient than a generic onboarding
5. What the candidate will be capable of after completion

Rules:
- Write in clear professional English
- Be specific about skill names and reasons
- Length: 4-6 sentences
- Do NOT use bullet points
- Do NOT use headers
- Return plain paragraph text only
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()


def generate_skill_gap_summary(original_gaps, job_title):
    """
    Generate a short summary of what gaps were found
    """

    gaps_text = json.dumps(original_gaps, indent=2)

    prompt = f"""
You are an expert HR analyst.

A candidate applying for {job_title} has these skill gaps:
{gaps_text}

Write ONE short sentence summarizing the overall 
skill gap situation for this candidate.
Be specific, professional, and concise.
Return plain text only.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


# ============================================
# TEST
# ============================================
if __name__ == "__main__":

    # Simulate data from previous steps
    original_gaps = [
        {
            "skill": "Programming",
            "current_level": 0,
            "required_level": 3,
            "gap_size": 3
        },
        {
            "skill": "Troubleshooting",
            "current_level": 0,
            "required_level": 2,
            "gap_size": 2
        },
        {
            "skill": "Complex Problem Solving",
            "current_level": 1,
            "required_level": 3,
            "gap_size": 2
        }
    ]

    expanded_gaps = [
        {"skill": "Critical Thinking", "current_level": 0, "required_level": 1, "auto_added": True},
        {"skill": "Systems Analysis", "current_level": 0, "required_level": 1, "auto_added": True},
        {"skill": "Programming", "current_level": 0, "required_level": 3},
        {"skill": "Troubleshooting", "current_level": 0, "required_level": 2},
        {"skill": "Complex Problem Solving", "current_level": 1, "required_level": 3}
    ]

    learning_path = [
        {"step_number": 1, "course_title": "Critical Thinking - Fundamentals", "level": "beginner", "duration_weeks": 1},
        {"step_number": 2, "course_title": "Systems Analysis - Fundamentals", "level": "beginner", "duration_weeks": 1},
        {"step_number": 3, "course_title": "Programming - Fundamentals", "level": "beginner", "duration_weeks": 1},
        {"step_number": 4, "course_title": "Troubleshooting - Fundamentals", "level": "beginner", "duration_weeks": 1},
        {"step_number": 5, "course_title": "Programming - Intermediate", "level": "intermediate", "duration_weeks": 2},
        {"step_number": 6, "course_title": "Troubleshooting - Intermediate", "level": "intermediate", "duration_weeks": 2},
        {"step_number": 7, "course_title": "Complex Problem Solving - Intermediate", "level": "intermediate", "duration_weeks": 2},
        {"step_number": 8, "course_title": "Programming - Advanced", "level": "expert", "duration_weeks": 3},
        {"step_number": 9, "course_title": "Complex Problem Solving - Advanced", "level": "expert", "duration_weeks": 3}
    ]

    job_title = "Software Developer"

    print("Generating reasoning trace...")
    print("=" * 50)

    # Generate gap summary
    summary = generate_skill_gap_summary(original_gaps, job_title)
    print(f"\nSkill Gap Summary:")
    print(f"  {summary}")

    # Generate full reasoning trace
    trace = generate_reasoning_trace(
        original_gaps,
        expanded_gaps,
        learning_path,
        job_title
    )

    print(f"\nReasoning Trace:")
    print(f"\n{trace}")

    # Save output
    output = {
        "job_title": job_title,
        "skill_gap_summary": summary,
        "reasoning_trace": trace
    }

    with open("reasoning_output.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Saved to reasoning_output.json")