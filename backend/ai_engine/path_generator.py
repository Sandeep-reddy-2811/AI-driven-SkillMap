# path_generator.py
import json
from groq import Groq
from rag import retrieve_all_courses, format_courses_for_prompt, load_catalog
from skill_graph import expand_skills_with_prerequisites, skill_graph

import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"


# ---- Generate Learning Path ----
def generate_learning_path(skill_gaps, job_title, catalog):
    """
    Full pipeline:
    1. Expand gaps with prerequisites (skill graph)
    2. Retrieve matching courses (RAG)
    3. Ask LLM to generate ordered path
    """

    print(f"\nGenerating learning path for: {job_title}")
    print("=" * 50)

    # Step 1 — Expand with prerequisites
    print("\nStep 1: Expanding with prerequisites...")
    expanded_gaps = expand_skills_with_prerequisites(skill_gaps, skill_graph)
    print(f"  Original gaps: {len(skill_gaps)}")
    print(f"  After prerequisites: {len(expanded_gaps)}")

    # Step 2 — RAG retrieval
    print("\nStep 2: Retrieving matching courses...")
    matched_courses = retrieve_all_courses(expanded_gaps, catalog)
    formatted_courses = format_courses_for_prompt(matched_courses)

    if not matched_courses:
        print("  ⚠ No courses matched!")
        return None

    # Step 3 — Build prompt
    gaps_text = json.dumps(expanded_gaps, indent=2)

    prompt = f"""
You are an expert corporate learning coach.

A new hire is preparing for the role of: {job_title}

Their skill gaps (ordered by prerequisites) are:
{gaps_text}

Available courses to recommend from (ONLY use these courses, 
do NOT invent any course outside this list):
{formatted_courses}

Your task:
Create a personalized step-by-step learning roadmap.

Rules:
1. ONLY recommend courses from the list above
2. Order steps from most fundamental to most advanced
3. Prerequisites must always come before dependent skills
4. Skip any skill the candidate already has (current_level > 0)
5. For each step, pick exactly ONE course from the list
6. NEVER recommend the same course twice
7. For prerequisite skills (auto_added: true), ONLY recommend the beginner course — do NOT add intermediate unless required_level > 1
8. Keep the total number of steps as small as possible — only include what is strictly necessary

Return ONLY a valid JSON array with this exact structure, 
nothing else, no explanation, no markdown:
[
  {{
    "step_number": 1,
    "course_id": 7,
    "course_title": "Programming - Fundamentals",
    "skill": "Programming",
    "level": "beginner",
    "duration_weeks": 1,
    "reason": "Why this step comes at this position"
  }}
]
"""

    # Step 4 — Call Groq LLM
    print("\nStep 3: Calling LLM to generate path...")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3  # low temperature = more focused output
    )

    raw_output = response.choices[0].message.content

    # Step 5 — Parse JSON response
    try:
        # Clean response in case LLM adds markdown
        clean = raw_output.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        clean = clean.strip()

        learning_path = json.loads(clean)
        print(f"  ✅ Generated {len(learning_path)} steps")
        return learning_path

    except json.JSONDecodeError as e:
        print(f"  ⚠ JSON parse error: {e}")
        print(f"  Raw output: {raw_output}")
        try:
            import re
            json_match = re.search(r'\[.*\]', raw_output, re.DOTALL)
            if json_match:
                learning_path = json.loads(json_match.group())
                print(f"  ✅ Recovered JSON with regex")
                return learning_path
        except:
            pass
        return None


# ---- Pretty Print Path ----
def print_learning_path(learning_path, job_title):
    if not learning_path:
        print("No learning path generated.")
        return

    print(f"\n{'='*50}")
    print(f"PERSONALIZED LEARNING PATH")
    print(f"Role: {job_title}")
    print(f"{'='*50}")

    total_weeks = 0
    for step in learning_path:
        print(f"\nStep {step['step_number']}: {step['course_title']}")
        print(f"  Skill    : {step['skill']}")
        print(f"  Level    : {step['level']}")
        print(f"  Duration : {step['duration_weeks']} week(s)")
        resources = step.get("resources", [])
        link = resources[0]["link"] if resources else step.get("link", "N/A")
        print(f"  Link     : {link}")
        print(f"  Reason   : {step['reason']}")
        total_weeks += step.get("duration_weeks", 0)

    print(f"\n{'='*50}")
    print(f"Total Duration: {total_weeks} weeks")
    print(f"Total Steps: {len(learning_path)}")


# ============================================
# TEST
# ============================================
if __name__ == "__main__":

    # Load catalog
    catalog = load_catalog()

    # Simulate skill gaps from AI Engineer 1
    sample_gaps = [
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

    job_title = "Software Developer"

    # Generate path
    learning_path = generate_learning_path(
        sample_gaps,
        job_title,
        catalog
    )

    # Print result
    print_learning_path(learning_path, job_title)

    # Save output
    if learning_path:
        output = {
            "job_title": job_title,
            "total_steps": len(learning_path),
            "total_weeks": sum(s.get("duration_weeks", 0) for s in learning_path),
            "learning_path": learning_path
        }
        with open("learning_path_output.json", "w") as f:
            json.dump(output, f, indent=2)
        print("\n✅ Saved to learning_path_output.json")