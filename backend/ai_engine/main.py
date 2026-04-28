# main.py
import json
from skill_graph import expand_skills_with_prerequisites, skill_graph
from rag import retrieve_all_courses, format_courses_for_prompt, load_catalog
from path_generator import generate_learning_path, client, MODEL
from reasoning import generate_reasoning_trace, generate_skill_gap_summary


# ============================================
# MASTER PIPELINE FUNCTION
# This is what Django backend will call
# ============================================

def run_ai_pipeline(skill_gaps, job_title):
    """
    Full AI Engine Pipeline:

    Input:
        skill_gaps  → list of skill gaps from AI Engineer 1
        job_title   → string e.g. "Software Developer"

    Output:
        Complete JSON with learning path + reasoning trace
    """

    print("\n" + "=" * 60)
    print("   AI ADAPTIVE ONBOARDING ENGINE")
    print("=" * 60)
    print(f"   Candidate Role : {job_title}")
    print(f"   Skill Gaps     : {len(skill_gaps)}")
    print("=" * 60)

    # ---- Step 1: Load Catalog ----
    print("\n[1/5] Loading course catalog...")
    catalog = load_catalog()
    print(f"      ✅ {len(catalog)} courses loaded")

    # ---- Step 2: Expand with Prerequisites ----
    print("\n[2/5] Running prerequisite skill graph...")
    expanded_gaps = expand_skills_with_prerequisites(
        skill_gaps,
        skill_graph
    )
    added = len(expanded_gaps) - len(skill_gaps)
    print(f"      ✅ {len(skill_gaps)} gaps → "
          f"{len(expanded_gaps)} after adding "
          f"{added} prerequisites")

    # ---- Step 3: RAG Retrieval ----
    print("\n[3/5] Running RAG retrieval...")
    matched_courses = retrieve_all_courses(expanded_gaps, catalog)
    formatted_courses = format_courses_for_prompt(matched_courses)
    print(f"      ✅ {len(matched_courses)} courses matched")

    if not matched_courses:
        return {
            "success": False,
            "error": "No courses found for the given skill gaps",
            "job_title": job_title
        }

    # ---- Step 4: Generate Learning Path ----
    print("\n[4/5] Generating personalized learning path...")
    learning_path = generate_learning_path(
        skill_gaps,
        job_title,
        catalog
    )

    if not learning_path:
        return {
            "success": False,
            "error": "Failed to generate learning path",
            "job_title": job_title
        }

    print(f"      ✅ {len(learning_path)} steps generated")

    # ---- Step 5: Generate Reasoning Trace ----
    print("\n[5/5] Generating reasoning trace...")
    skill_gap_summary = generate_skill_gap_summary(
        skill_gaps,
        job_title
    )
    reasoning_trace = generate_reasoning_trace(
        skill_gaps,
        expanded_gaps,
        learning_path,
        job_title
    )
    print(f"      ✅ Reasoning trace generated")

    # ---- Build Final Output ----
    total_weeks = sum(
        s.get("duration_weeks", 0)
        for s in learning_path
    )

    final_output = {
        "success": True,
        "job_title": job_title,
        "summary": {
            "original_gaps": len(skill_gaps),
            "expanded_gaps": len(expanded_gaps),
            "prerequisites_added": added,
            "total_steps": len(learning_path),
            "total_weeks": total_weeks,
            "skill_gap_summary": skill_gap_summary
        },
        "skill_gaps": skill_gaps,
        "expanded_gaps": expanded_gaps,
        "learning_path": learning_path,
        "reasoning_trace": reasoning_trace
    }

    return final_output


# ============================================
# SAVE OUTPUT
# ============================================

def save_output(output, path="final_output.json"):
    with open(path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n✅ Final output saved to {path}")


# ============================================
# PRINT FINAL REPORT
# ============================================

def print_final_report(output):

    if not output["success"]:
        print(f"\n❌ Error: {output['error']}")
        return

    print("\n" + "=" * 60)
    print("   FINAL ONBOARDING REPORT")
    print("=" * 60)

    s = output["summary"]
    print(f"\n   Role             : {output['job_title']}")
    print(f"   Skill Gaps Found : {s['original_gaps']}")
    print(f"   Prerequisites    : {s['prerequisites_added']} auto-added")
    print(f"   Training Steps   : {s['total_steps']}")
    print(f"   Total Duration   : {s['total_weeks']} weeks")

    print(f"\n   Gap Summary:")
    print(f"   {s['skill_gap_summary']}")

    print(f"\n{'=' * 60}")
    print(f"   PERSONALIZED LEARNING PATH")
    print(f"{'=' * 60}")

    for step in output["learning_path"]:
        auto = " 🔁" if any(
            g.get("auto_added") and g["skill"] == step["skill"]
            for g in output["expanded_gaps"]
        ) else ""
        print(f"\n   Step {step['step_number']}{auto}")
        print(f"   Course   : {step['course_title']}")
        print(f"   Level    : {step['level']}")
        print(f"   Duration : {step['duration_weeks']} week(s)")
        print(f"   Link     : {step['link']}")
        print(f"   Reason   : {step['reason']}")

    print(f"\n{'=' * 60}")
    print(f"   REASONING TRACE")
    print(f"{'=' * 60}")
    print(f"\n{output['reasoning_trace']}")


# ============================================
# TEST — 3 DIFFERENT JOB ROLES
# ============================================

if __name__ == "__main__":

    # ---- Test 1: Technical Role ----
    print("\n\n🔷 TEST 1: TECHNICAL ROLE")
    gaps_technical = [
        {"skill": "Programming", "current_level": 0, "required_level": 3, "gap_size": 3},
        {"skill": "Troubleshooting", "current_level": 0, "required_level": 2, "gap_size": 2},
        {"skill": "Complex Problem Solving", "current_level": 1, "required_level": 3, "gap_size": 2}
    ]
    output1 = run_ai_pipeline(gaps_technical, "Software Developer")
    print_final_report(output1)
    save_output(output1, "output_technical.json")

    # ---- Test 2: Business Role ----
    print("\n\n🔷 TEST 2: BUSINESS ROLE")
    gaps_business = [
        {"skill": "Management of Personnel Resources", "current_level": 0, "required_level": 3, "gap_size": 3},
        {"skill": "Negotiation", "current_level": 1, "required_level": 3, "gap_size": 2},
        {"skill": "Monitoring", "current_level": 0, "required_level": 2, "gap_size": 2}
    ]
    output2 = run_ai_pipeline(gaps_business, "HR Manager")
    print_final_report(output2)
    save_output(output2, "output_business.json")

    # ---- Test 3: Operational Role ----
    print("\n\n🔷 TEST 3: OPERATIONAL ROLE")
    gaps_operational = [
        {"skill": "Operation and Control", "current_level": 0, "required_level": 2, "gap_size": 2},
        {"skill": "Equipment Maintenance", "current_level": 0, "required_level": 2, "gap_size": 2},
        {"skill": "Quality Control Analysis", "current_level": 1, "required_level": 3, "gap_size": 2}
    ]
    output3 = run_ai_pipeline(gaps_operational, "Production Supervisor")
    print_final_report(output3)
    save_output(output3, "output_operational.json")

    print("\n\n✅ ALL 3 TESTS COMPLETE")
    print("   output_technical.json")
    print("   output_business.json")
    print("   output_operational.json")