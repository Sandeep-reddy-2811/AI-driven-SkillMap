skill_graph = {

    # ---- TECHNICAL SKILLS ----
    "Programming": [],                          # No prerequisites
    "Reading Comprehension": [],                # No prerequisites
    "Critical Thinking": [],                    # No prerequisites
    "Mathematics": [],                          # No prerequisites
    "Writing": [],                              # No prerequisites
    "Active Listening": [],                     # No prerequisites

    "Systems Analysis": ["Critical Thinking"],
    "Systems Evaluation": ["Systems Analysis"],
    "Complex Problem Solving": ["Critical Thinking", "Systems Analysis"],
    "Troubleshooting": ["Systems Analysis", "Programming"],
    "Technology Design": ["Programming", "Systems Analysis"],
    "Operations Analysis": ["Mathematics", "Systems Analysis"],
    "Quality Control Analysis": ["Operations Analysis"],
    "Judgment and Decision Making": ["Critical Thinking"],

    # ---- BUSINESS SKILLS ----
    "Coordination": [],                         # No prerequisites
    "Social Perceptiveness": [],                # No prerequisites
    "Speaking": [],                             # No prerequisites
    "Negotiation": ["Active Listening", "Speaking"],
    "Instructing": ["Speaking", "Reading Comprehension"],
    "Service Orientation": ["Active Listening", "Social Perceptiveness"],
    "Management of Personnel Resources": ["Coordination", "Judgment and Decision Making"],
    "Management of Financial Resources": ["Mathematics", "Judgment and Decision Making"],
    "Management of Material Resources": ["Coordination", "Operations Analysis"],
    "Time Management": ["Coordination"],
    "Monitoring": ["Critical Thinking", "Reading Comprehension"],

    # ---- OPERATIONAL SKILLS ----
    "Equipment Selection": ["Operations Analysis"],
    "Equipment Maintenance": ["Troubleshooting"],
    "Operation Monitoring": ["Monitoring", "Critical Thinking"],
    "Operation and Control": ["Operation Monitoring", "Equipment Selection"],
    "Repairing": ["Troubleshooting", "Equipment Maintenance"],
    "Installation": ["Technology Design", "Equipment Selection"],
}

# Builds a complete learning path by recursively collecting all required skills in the correct order.

def get_all_prerequisites(skill, graph, visited=None):
    """
    Recursively find ALL prerequisites for a skill
    including prerequisites of prerequisites
    """
    if visited is None:
        visited = set()

    prerequisites = []

    for prereq in graph.get(skill, []):
        if prereq not in visited:
            visited.add(prereq)
            # Recursively get prereqs of prereqs
            deeper = get_all_prerequisites(prereq, graph, visited)
            prerequisites.extend(deeper)
            prerequisites.append(prereq)

    return prerequisites

# Creates the correct order to learn skills by ensuring all prerequisites are completed first
def topological_sort(skills_needed, graph):
    """
    Sort skills so prerequisites always come first.
    Uses DFS-based topological sort.
    """
    visited = set()
    ordered = []

    def dfs(skill):
        if skill in visited:
            return
        visited.add(skill)
        # Visit all prerequisites first
        for prereq in graph.get(skill, []):
            dfs(prereq)
        ordered.append(skill)

    for skill in skills_needed:
        dfs(skill)

    return ordered

def expand_skills_with_prerequisites(skill_gaps, graph):
    """
    Take a list of skill gaps and automatically add
    any missing prerequisites the person also needs.
    
    Input:  [{"skill": "Deep Learning", ...}]
    Output: expanded list with prerequisites added
    """
    # Get names of skills person already has gaps in
    gap_skill_names = [g["skill"] for g in skill_gaps]

    # Find all prerequisites needed
    all_skills_needed = set(gap_skill_names)

    for skill in gap_skill_names:
        prereqs = get_all_prerequisites(skill, graph)
        for prereq in prereqs:
            all_skills_needed.add(prereq)

    # Topologically sort all skills
    ordered_skills = topological_sort(list(all_skills_needed), graph)

    # Build expanded gap list
    expanded_gaps = []
    existing_gap_names = {g["skill"]: g for g in skill_gaps}

    for skill in ordered_skills:
        if skill in existing_gap_names:
            # Use original gap data
            expanded_gaps.append(existing_gap_names[skill])
        else:
            # This is an auto-added prerequisite
            expanded_gaps.append({
                "skill": skill,
                "current_level": 0,
                "required_level": 1,
                "gap_size": 1,
                "auto_added": True,  # flag so we know it was added by graph
                "reason": f"Prerequisite automatically added for learning path"
            })

    return expanded_gaps

if __name__ == "__main__":

    print("=" * 50)
    print("PREREQUISITE GRAPH TEST")
    print("=" * 50)

    # Simulate skill gaps from AI Engineer 1
    sample_gaps = [
        {"skill": "Complex Problem Solving", "current_level": 0, "required_level": 2, "gap_size": 2},
        {"skill": "Management of Personnel Resources", "current_level": 0, "required_level": 3, "gap_size": 3},
        {"skill": "Troubleshooting", "current_level": 1, "required_level": 3, "gap_size": 2},
    ]

    print("\nOriginal skill gaps:")
    for g in sample_gaps:
        print(f"  - {g['skill']} (gap size: {g['gap_size']})")

    print("\nExpanding with prerequisites...")
    expanded = expand_skills_with_prerequisites(sample_gaps, skill_graph)

    print("\nExpanded and ordered learning path:")
    for i, g in enumerate(expanded, 1):
        auto = " ← AUTO ADDED (prerequisite)" if g.get("auto_added") else ""
        print(f"  {i}. {g['skill']}{auto}")