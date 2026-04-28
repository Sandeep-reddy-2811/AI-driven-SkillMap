# rag.py
import json

# ---- Load Catalog ----
def load_catalog(path="course_catalog.json"):
    with open(path, "r") as f:
        return json.load(f)


# ---- Level Map ----
level_map = {
    "beginner": 1,
    "intermediate": 2,
    "expert": 3
}

reverse_level_map = {
    1: "beginner",
    2: "intermediate",
    3: "expert"
}


# ---- Core RAG Function ----
def retrieve_courses_for_gap(gap, catalog):
    """
    For a single skill gap, find all relevant
    courses from the catalog that would help.
    
    Logic:
    - Match by skill name
    - Only return courses ABOVE current level
    - Only return courses UP TO required level
    """
    skill_name = gap["skill"].lower()
    current_level = gap["current_level"]
    required_level = gap["required_level"]

    matched = []
    seen_skill_levels = set()  # prevent duplicates

    for course in catalog:
        course_skill = course["skill"].lower()
        course_level = level_map.get(course["level"], 0)

        # Check if skill name matches
        skill_match = (
            skill_name in course_skill or
            course_skill in skill_name
        )

        # Check if level is in the right range
        level_match = (
            course_level > current_level and
            course_level <= required_level + 1
        )

        # Deduplicate by skill + level combination
        dedup_key = f"{course['skill'].lower()}_{course['level']}"
        not_duplicate = dedup_key not in seen_skill_levels

        if skill_match and level_match and not_duplicate:
            seen_skill_levels.add(dedup_key)
            matched.append(course)

    return matched


# ---- Retrieve For All Gaps ----
def retrieve_all_courses(skill_gaps, catalog):
    """
    For ALL skill gaps, find relevant courses.
    Returns a deduplicated list of matched courses.
    """
    all_matched = []
    seen_ids = set()

    print("\nRAG Retrieval Results:")
    print("=" * 50)

    for gap in skill_gaps:
        courses = retrieve_courses_for_gap(gap, catalog)

        print(f"\nGap: {gap['skill']} "
              f"(level {gap['current_level']} → {gap['required_level']})")

        if courses:
            for course in courses:
                if course["id"] not in seen_ids:
                    seen_ids.add(course["id"])
                    all_matched.append(course)
                    print(f"  ✓ Matched: {course['title']} ({course['level']})")
        else:
            print(f"  ⚠ No courses found for: {gap['skill']}")

    print(f"\nTotal matched courses: {len(all_matched)}")
    return all_matched


# ---- Format for LLM Prompt ----
def format_courses_for_prompt(matched_courses):
    """
    Format the matched courses into clean text
    that can be inserted into an LLM prompt.
    """
    if not matched_courses:
        return "No courses available."

    lines = []
    for course in matched_courses:
        lines.append(
            f"- ID:{course['id']} | "
            f"{course['title']} | "
            f"Level: {course['level']} | "
            f"Duration: {course['duration_weeks']} weeks | "
            f"Domain: {course['domain']} | "
            f"Link: {course['link']}"
        )

    return "\n".join(lines)


# ============================================
# TEST RAG
# ============================================
if __name__ == "__main__":

    # Load catalog
    catalog = load_catalog()
    print(f"Loaded {len(catalog)} courses from catalog")

    # Simulate skill gaps from AI Engineer 1
    # (after going through skill graph in Step 2)
    sample_gaps = [
        {
            "skill": "Programming",
            "current_level": 0,
            "required_level": 3,
            "gap_size": 3
        },
        {
            "skill": "Critical Thinking",
            "current_level": 1,
            "required_level": 3,
            "gap_size": 2
        },
        {
            "skill": "Coordination",
            "current_level": 0,
            "required_level": 2,
            "gap_size": 2
        },
        {
            "skill": "Troubleshooting",
            "current_level": 0,
            "required_level": 2,
            "gap_size": 2
        }
    ]

    # Run RAG
    matched_courses = retrieve_all_courses(sample_gaps, catalog)

    # Format for LLM
    print("\n" + "=" * 50)
    print("FORMATTED FOR LLM PROMPT:")
    print("=" * 50)
    formatted = format_courses_for_prompt(matched_courses)
    print(formatted)