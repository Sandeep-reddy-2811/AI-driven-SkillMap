import pandas as pd
import json

# ---- Load Data ----
def load_data():
    print("Loading O*NET data...")
    skills_df = pd.read_excel("Skills.xlsx")
    occ_df = pd.read_excel("Occupation Data.xlsx")
    
    # Keep only LV (Level) rows — more useful than IM (Importance)
    skills_df = skills_df[skills_df["Scale ID"] == "LV"]
    
    # Keep only useful columns
    skills_df = skills_df[[
        "O*NET-SOC Code", 
        "Title", 
        "Element Name", 
        "Data Value"
    ]]
    
    skills_df.columns = ["job_code", "job_title", "skill", "level_score"]
    
    print(f"Loaded {len(skills_df)} skill rows")
    print(f"Loaded {len(occ_df)} job roles")
    
    return skills_df, occ_df


# ---- Convert Score to Level Label ----
def score_to_level(score):
    if score <= 2.0:
        return "beginner"
    elif score <= 3.5:
        return "intermediate"
    else:
        return "expert"


# ---- Get Skills For a Specific Job ----
def get_skills_for_job(skills_df, job_keyword):
    
    matched = skills_df[
        skills_df["job_title"].str.contains(job_keyword, case=False, na=False)
    ]
    
    if matched.empty:
        print(f"  ⚠ No match found for: {job_keyword}")
        return []
    
    # Take first matched job title
    first_title = matched["job_title"].iloc[0]
    matched = matched[matched["job_title"] == first_title]
    
    print(f"  ✓ Found: {first_title} ({len(matched)} skills)")
    
    skills = []
    for _, row in matched.iterrows():
        skills.append({
            "skill": row["skill"],
            "required_level": score_to_level(row["level_score"]),
            "level_score": round(float(row["level_score"]), 2)
        })
    
    # Sort by level score descending — most important first
    skills.sort(key=lambda x: x["level_score"], reverse=True)
    
    # Return top 8 skills per job
    return skills[:8]


# ---- Build Full Course Catalog ----
def build_catalog(skills_df):
    
    # Target jobs across 3 domains
    target_jobs = {
    "technical": [
        "Software Developers",
        "Computer Network Architects",
        "Network and Computer Systems Administrators"
    ],
    "business": [
        "Human Resources Managers",
        "Marketing Managers",
        "Financial Managers",
    ],
    "operational": [
        "First-Line Supervisors of Production and Operating Workers",
        "Logisticians",
        "Industrial Production Managers"
    ]
}
    
    # Real course links for common skills
    course_links = {
        "Reading Comprehension":    "https://www.coursera.org/learn/communication-skills",
        "Active Listening":         "https://www.coursera.org/learn/communication-skills",
        "Writing":                  "https://www.coursera.org/learn/writing-skills",
        "Critical Thinking":        "https://www.coursera.org/learn/critical-thinking-skills",
        "Programming":              "https://www.coursera.org/specializations/python",
        "Mathematics":              "https://www.khanacademy.org/math",
        "Systems Analysis":         "https://www.coursera.org/learn/systems-thinking",
        "Operations Analysis":      "https://www.coursera.org/learn/operations-management",
        "Complex Problem Solving":  "https://www.coursera.org/learn/problem-solving",
        "Judgment":                 "https://www.coursera.org/learn/decision-making",
        "Management of Personnel":  "https://www.coursera.org/learn/human-resource-management",
        "Coordination":             "https://www.coursera.org/learn/leadership-management",
        "Monitoring":               "https://www.coursera.org/learn/project-management-foundations",
        "Time Management":          "https://www.coursera.org/learn/work-smarter-not-harder",
        "Social Perceptiveness":    "https://www.coursera.org/learn/communication-skills",
        "Speaking":                 "https://www.coursera.org/learn/public-speaking",
        "Negotiation":              "https://www.coursera.org/learn/negotiation",
        "Instructing":              "https://www.coursera.org/learn/teaching-skills",
        "Service Orientation":      "https://www.coursera.org/learn/customer-service",
        "Quality Control Analysis": "https://www.coursera.org/learn/six-sigma-principles",
    }
    
    default_link = "https://www.coursera.org/search?query={skill}"
    
    # Collect all unique skills per domain
    domain_skills = {}  # {domain: {skill: required_level}}
    job_skill_map = {}  # {job_title: [skills]}
    
    for domain, jobs in target_jobs.items():
        print(f"\nProcessing {domain} domain...")
        domain_skills[domain] = {}
        
        for job_keyword in jobs:
            skills = get_skills_for_job(skills_df, job_keyword)
            if skills:
                job_title = job_keyword
                job_skill_map[job_title] = skills
                for s in skills:
                    skill_name = s["skill"]
                    # Keep highest level if skill appears multiple times
                    if skill_name not in domain_skills[domain]:
                        domain_skills[domain][skill_name] = s["required_level"]
    
    # Build catalog
    catalog = []
    course_id = 1
    
    level_order = {"beginner": 1, "intermediate": 2, "expert": 3}
    
    for domain, skills in domain_skills.items():
        for skill_name, max_level in skills.items():
            
            # Always add beginner course
            link = course_links.get(skill_name, default_link.replace("{skill}", skill_name.replace(" ", "+")))
            
            catalog.append({
                "id": course_id,
                "title": f"{skill_name} - Fundamentals",
                "skill": skill_name,
                "level": "beginner",
                "domain": domain,
                "duration_weeks": 1,
                "platform": "Coursera",
                "link": link
            })
            course_id += 1
            
            # Add intermediate if needed
            if level_order[max_level] >= 2:
                catalog.append({
                    "id": course_id,
                    "title": f"{skill_name} - Intermediate",
                    "skill": skill_name,
                    "level": "intermediate",
                    "domain": domain,
                    "duration_weeks": 2,
                    "platform": "Coursera",
                    "link": link
                })
                course_id += 1
            
            # Add expert if needed
            if level_order[max_level] >= 3:
                catalog.append({
                    "id": course_id,
                    "title": f"{skill_name} - Advanced",
                    "skill": skill_name,
                    "level": "expert",
                    "domain": domain,
                    "duration_weeks": 3,
                    "platform": "Coursera",
                    "link": link
                })
                course_id += 1
    
    return catalog, job_skill_map


# ---- Save Results ----
def save_results(catalog, job_skill_map):
    
    # Save catalog
    with open("course_catalog.json", "w") as f:
        json.dump(catalog, f, indent=2)
    
    # Save job skill map
    with open("job_skill_map.json", "w") as f:
        json.dump(job_skill_map, f, indent=2)
    
    print(f"\n✅ Saved course_catalog.json with {len(catalog)} courses")
    print(f"✅ Saved job_skill_map.json with {len(job_skill_map)} job roles")


# ---- Preview Results ----
def preview_results(catalog, job_skill_map):
    
    print("\n" + "="*50)
    print("CATALOG PREVIEW")
    print("="*50)
    
    # Count by domain
    domains = {}
    for c in catalog:
        domains[c["domain"]] = domains.get(c["domain"], 0) + 1
    
    for domain, count in domains.items():
        print(f"  {domain}: {count} courses")
    
    print(f"\nTotal: {len(catalog)} courses")
    
    print("\nSample courses:")
    for course in catalog[:6]:
        print(f"  [{course['domain']}] {course['title']} ({course['level']})")
    
    print("\n" + "="*50)
    print("JOB SKILL MAP PREVIEW")
    print("="*50)
    for job, skills in list(job_skill_map.items())[:2]:
        print(f"\n{job}:")
        for s in skills[:4]:
            print(f"  - {s['skill']} → {s['required_level']} (score: {s['level_score']})")


# ---- Main ----
if __name__ == "__main__":
    
    # Load data
    skills_df, occ_df = load_data()
    
    # Build catalog
    catalog, job_skill_map = build_catalog(skills_df)
    
    # Save to JSON files
    save_results(catalog, job_skill_map)
    
    # Preview
    preview_results(catalog, job_skill_map)