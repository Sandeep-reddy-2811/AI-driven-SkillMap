import pdfplumber
import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _get_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def ask_ai(prompt):
    client = _get_client()
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return response.choices[0].message.content.strip()


def _extract_text_from_pdf(pdf_file) -> str:
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.encode("utf-8", errors="ignore").decode("utf-8").strip()


def _clean_json(result):
    result = result.replace("```json", "").replace("```", "").strip()
    return result


# ─────────────────────────────────────────────
# SKILL MAPPING — Raw → O*NET Names
# ─────────────────────────────────────────────

SKILL_MAPPING = {
    # Programming
    "python": "Programming",
    "java": "Programming",
    "c++": "Programming",
    "c": "Programming",
    "c#": "Programming",
    "javascript": "Programming",
    "typescript": "Programming",
    "html": "Programming",
    "css": "Programming",
    "sql": "Programming",
    "mysql": "Programming",
    "postgresql": "Programming",
    "mongodb": "Programming",
    "coding": "Programming",
    "software development": "Programming",
    "web development": "Programming",
    "backend": "Programming",
    "frontend": "Programming",
    "fullstack": "Programming",
    "node.js": "Programming",
    "react": "Programming",
    "django": "Programming",
    "flask": "Programming",
    "spring": "Programming",
    "ruby": "Programming",
    "php": "Programming",
    "swift": "Programming",
    "kotlin": "Programming",
    "rust": "Programming",
    "go": "Programming",
    "scala": "Programming",
    "r": "Programming",
    "matlab": "Programming",

    # Complex Problem Solving
    "problem solving": "Complex Problem Solving",
    "algorithms": "Complex Problem Solving",
    "data structures": "Complex Problem Solving",
    "competitive programming": "Complex Problem Solving",
    "leetcode": "Complex Problem Solving",
    "dynamic programming": "Complex Problem Solving",
    "graph algorithms": "Complex Problem Solving",
    "optimization": "Complex Problem Solving",
    "object-oriented programming": "Complex Problem Solving",
    "oop": "Complex Problem Solving",
    "design patterns": "Complex Problem Solving",

    # Operations Analysis
    "data analysis": "Operations Analysis",
    "pandas": "Operations Analysis",
    "numpy": "Operations Analysis",
    "matplotlib": "Operations Analysis",
    "seaborn": "Operations Analysis",
    "scikit-learn": "Operations Analysis",
    "tableau": "Operations Analysis",
    "power bi": "Operations Analysis",
    "data visualization": "Operations Analysis",
    "exploratory data analysis": "Operations Analysis",
    "eda": "Operations Analysis",
    "business analysis": "Operations Analysis",
    "reporting": "Operations Analysis",

    # Systems Evaluation
    "model evaluation": "Systems Evaluation",
    "testing": "Systems Evaluation",
    "unit testing": "Systems Evaluation",
    "integration testing": "Systems Evaluation",
    "hyperparameter tuning": "Systems Evaluation",
    "benchmarking": "Systems Evaluation",
    "performance testing": "Systems Evaluation",
    "quality assurance": "Systems Evaluation",
    "qa": "Systems Evaluation",
    "feature engineering": "Systems Evaluation",
    "model selection": "Systems Evaluation",

    # Mathematics
    "statistics": "Mathematics",
    "probability": "Mathematics",
    "discrete mathematics": "Mathematics",
    "linear algebra": "Mathematics",
    "calculus": "Mathematics",
    "probability & statistics": "Mathematics",
    "math": "Mathematics",
    "numerical methods": "Mathematics",

    # Troubleshooting
    "debugging": "Troubleshooting",
    "error fixing": "Troubleshooting",
    "issue resolution": "Troubleshooting",
    "bug fixing": "Troubleshooting",
    "root cause analysis": "Troubleshooting",

    # Critical Thinking
    "analytical thinking": "Critical Thinking",
    "logic": "Critical Thinking",
    "reasoning": "Critical Thinking",
    "analysis": "Critical Thinking",
    "critical analysis": "Critical Thinking",

    # Systems Analysis
    "system design": "Systems Analysis",
    "architecture": "Systems Analysis",
    "software architecture": "Systems Analysis",
    "requirements analysis": "Systems Analysis",
    "uml": "Systems Analysis",
    "api design": "Systems Analysis",
    "microservices": "Systems Analysis",

    # Machine Learning / AI
    "machine learning": "Operations Analysis",
    "deep learning": "Operations Analysis",
    "nlp": "Operations Analysis",
    "natural language processing": "Operations Analysis",
    "computer vision": "Operations Analysis",
    "reinforcement learning": "Operations Analysis",
    "supervised learning": "Operations Analysis",
    "unsupervised learning": "Operations Analysis",
    "neural networks": "Operations Analysis",
    "tensorflow": "Operations Analysis",
    "pytorch": "Operations Analysis",
    "keras": "Operations Analysis",
    "opencv": "Operations Analysis",
    "ultralytics": "Operations Analysis",
    "yolo": "Operations Analysis",
    "transformers": "Operations Analysis",
    "llm": "Operations Analysis",

    # DevOps / Cloud
    "git": "Systems Analysis",
    "docker": "Systems Analysis",
    "kubernetes": "Systems Analysis",
    "aws": "Systems Analysis",
    "azure": "Systems Analysis",
    "gcp": "Systems Analysis",
    "ci/cd": "Systems Analysis",
    "linux": "Systems Analysis",
    "devops": "Systems Analysis",

    # Streamlit / Dashboards
    "streamlit": "Systems Evaluation",
    "gradio": "Systems Evaluation",
    "dashboard": "Systems Evaluation",
}

# Non-technical skills to ALWAYS filter out for technical roles
NON_TECHNICAL_SKILLS = [
    "active listening",
    "reading comprehension",
    "writing",
    "coordination",
    "monitoring",
    "judgment and decision making",
    "negotiation",
    "management of personnel resources",
    "social perceptiveness",
    "instructing",
    "service orientation",
    "speaking",
    "time management",
    "persuasion",
]

# Technical role keywords
TECHNICAL_KEYWORDS = [
    "developer", "engineer", "programmer", "data scientist",
    "machine learning", "software", "devops", "backend",
    "frontend", "fullstack", "analyst", "architect", "ml",
    "data engineer", "cloud", "security", "network", "system",
    "database", "web", "mobile", "ai", "research", "intern"
]


def _is_technical_role(job_title: str) -> bool:
    job_title_lower = job_title.lower()
    return any(kw in job_title_lower for kw in TECHNICAL_KEYWORDS)


# ─────────────────────────────────────────────
# FUNCTION 1: parse_resume
# ─────────────────────────────────────────────

def parse_resume(pdf_file) -> dict:
    resume_text = _extract_text_from_pdf(pdf_file)

    prompt = f"""
You are an expert HR analyst with 25 years experience.
Analyze this resume and return ONLY a JSON object.

SCORING RULES:
- Each year at real company = 10 points
- Each year at internship = 5 points
- College/university = 0 points
- Real project with users = 15 points
- Personal project = 5 points
- College project = 2 points
- Led team at real company = 15 points
- Led team at internship = 7 points
- Led college team = 1 point

LEVEL FROM SCORE:
- 0-10 = fresher
- 11-25 = junior
- 26-45 = mid
- 46+ = senior

Return ONLY this JSON:
{{
    "name": "full name",
    "email": "email or null",
    "skills": ["skill1", "skill2"],
    "experience": {{
        "total_years": 0,
        "breakdown": [
            {{
                "company": "name",
                "role": "title",
                "type": "real_company or internship or college",
                "duration_years": 0,
                "points": 0
            }}
        ]
    }},
    "projects": [
        {{
            "name": "project name",
            "type": "real_company or personal or college",
            "scale": "users or null",
            "technologies": ["tech1"],
            "points": 0
        }}
    ],
    "leadership": {{
        "has_leadership": false,
        "details": []
    }},
    "scoring_summary": {{
        "experience_points": 0,
        "project_points": 0,
        "leadership_points": 0,
        "total_points": 0,
        "level": "fresher",
        "level_reason": "reason here"
    }}
}}

Resume:
{resume_text}

Return ONLY JSON. No explanation. No markdown.
"""

    result = ask_ai(prompt)
    result = _clean_json(result)

    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {
            "name": "Unknown",
            "email": None,
            "skills": [],
            "experience": {"total_years": 0, "breakdown": []},
            "projects": [],
            "leadership": {"has_leadership": False, "details": []},
            "scoring_summary": {
                "experience_points": 0,
                "project_points": 0,
                "leadership_points": 0,
                "total_points": 0,
                "level": "fresher",
                "level_reason": "Could not parse resume"
            }
        }


# ─────────────────────────────────────────────
# FUNCTION 2: parse_jd
# ─────────────────────────────────────────────

def parse_jd(pdf_file) -> dict:
    jd_text = _extract_text_from_pdf(pdf_file)

    prompt = f"""
You are an expert HR analyst with 25 years experience.
Analyze this job description carefully and return ONLY a JSON object.

Map required skills to O*NET standard names based on role type:

For TECHNICAL roles (Software Developer, Data Scientist, ML Engineer, etc):
ONLY use these technical skills — do NOT include soft skills:
- "Programming" (Python, Java, C++, coding, software development)
- "Systems Analysis" (system design, architecture, requirements analysis)
- "Troubleshooting" (debugging, issue resolution, error fixing)
- "Complex Problem Solving" (algorithms, data structures, optimization)
- "Systems Evaluation" (testing, model evaluation, benchmarking)
- "Mathematics" (statistics, discrete math, probability, calculus)
- "Operations Analysis" (data analysis, ML, reporting)
- "Critical Thinking" (analytical thinking, logic, reasoning)

For BUSINESS roles (HR Manager, Marketing Manager, Financial Analyst, etc):
ONLY use these business skills:
- "Active Listening" (communication, teamwork, collaboration)
- "Reading Comprehension" (documentation, research, reading)
- "Writing" (documentation, technical writing, reports)
- "Coordination" (project management, team coordination, agile)
- "Judgment and Decision Making" (decision making, prioritization)
- "Monitoring" (project tracking, performance monitoring)
- "Management of Personnel Resources" (HR management, people management)
- "Negotiation" (conflict resolution, negotiation skills)

For OPERATIONAL roles (Production Supervisor, Logistics Manager, etc):
ONLY use these operational skills:
- "Operations Analysis" (data analysis, operational analysis)
- "Equipment Maintenance" (maintenance, equipment handling)
- "Quality Control Analysis" (quality control, six sigma)
- "Equipment Selection" (equipment management)
- "Operation and Control" (production control, operations)
- "Mathematics" (statistics, calculations)

CRITICAL RULE: For technical roles like Software Developer, Data Engineer,
ML Engineer — do NOT include Active Listening, Reading Comprehension,
Writing, Coordination or any other soft skills in required_skills.

Return this EXACT JSON:
{{
    "job_title": "exact job title",
    "company": "company name or null",
    "required_skills": ["skill1", "skill2", "skill3"],
    "preferred_skills": ["skill1", "skill2"],
    "experience_needed": {{
        "min_years": 0,
        "max_years": 0,
        "level": "fresher or junior or mid or senior"
    }},
    "tech_stack": ["Python", "AWS", "Docker"],
    "responsibilities": ["responsibility 1"],
    "education": "degree requirement or null",
    "job_type": "full-time or part-time or contract"
}}

For level - NEVER return null:
- intern or trainee or 0-1 years or fresh graduate = fresher
- 1-3 years = junior
- 3-6 years = mid
- 6+ years or lead or architect = senior

Job Description:
{jd_text}

Return ONLY JSON. No explanation. No markdown.
"""

    result = ask_ai(prompt)
    result = _clean_json(result)

    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {
            "job_title": "Unknown Role",
            "company": None,
            "required_skills": [],
            "preferred_skills": [],
            "experience_needed": {
                "min_years": 0,
                "max_years": 0,
                "level": "mid"
            },
            "tech_stack": [],
            "responsibilities": [],
            "education": None,
            "job_type": "full-time"
        }


# ─────────────────────────────────────────────
# FUNCTION 3: analyze_skill_gap
# ─────────────────────────────────────────────

def analyze_skill_gap(resume_data: dict, jd_data: dict) -> dict:
    resume_skills = resume_data.get("skills", [])
    jd_required   = jd_data.get("required_skills", [])
    jd_preferred  = jd_data.get("preferred_skills", [])

    candidate_level_str = resume_data.get(
        "scoring_summary", {}
    ).get("level", "fresher")

    job_level_str = jd_data.get(
        "experience_needed", {}
    ).get("level", "junior")

    job_title    = jd_data.get("job_title", "")
    is_technical = _is_technical_role(job_title)

    # ── Filter non-technical skills from JD for technical roles ──
    filtered_required = []
    for skill in jd_required:
        skill_lower = skill.lower()
        if is_technical:
            is_non_tech = any(nt in skill_lower for nt in NON_TECHNICAL_SKILLS)
            if is_non_tech:
                continue
        filtered_required.append(skill)

    # ── Map resume skills to O*NET names ──────────────────────
    mapped_resume_skills = set()
    for skill in resume_skills:
        skill_lower = skill.lower().strip()
        if skill_lower in SKILL_MAPPING:
            mapped_resume_skills.add(SKILL_MAPPING[skill_lower].lower())
        else:
            mapped_resume_skills.add(skill_lower)

    # ── Use LLM for high level gap analysis ───────────────────
    prompt = f"""
You are an expert career counselor with 20 years experience.

Analyze the skill gap between this candidate and job requirement.

CANDIDATE SKILLS: {resume_skills}
CANDIDATE LEVEL: {candidate_level_str}
JOB REQUIRED SKILLS: {filtered_required}
JOB REQUIRED LEVEL: {job_level_str}

Return ONLY this JSON:
{{
    "matching_skills": ["skill1", "skill2"],
    "missing_required_skills": ["skill1", "skill2"],
    "missing_preferred_skills": [],
    "level_analysis": {{
        "candidate_level": "{candidate_level_str}",
        "job_required_level": "{job_level_str}",
        "is_match": false,
        "comment": "one line explanation"
    }},
    "match_score": 75,
    "match_verdict": "Good Match or Partial Match or Poor Match",
    "overall_advice": "2-3 lines of career advice"
}}

Return ONLY the JSON. No explanation. No markdown.
"""

    result = ask_ai(prompt)
    result = _clean_json(result)

    try:
        gap_data = json.loads(result)
    except json.JSONDecodeError:
        gap_data = {
            "matching_skills": [],
            "missing_required_skills": filtered_required,
            "missing_preferred_skills": [],
            "level_analysis": {
                "candidate_level": candidate_level_str,
                "job_required_level": job_level_str,
                "is_match": False,
                "comment": "Could not analyze"
            },
            "match_score": 0,
            "match_verdict": "Poor Match",
            "overall_advice": "Please try again."
        }

    # Make sure all skill fields are lists
    matching     = gap_data.get("matching_skills", [])
    missing_req  = gap_data.get("missing_required_skills", [])
    missing_pref = gap_data.get("missing_preferred_skills", [])

    if isinstance(matching, dict):
        matching = list(matching.values())
    if isinstance(missing_req, dict):
        missing_req = list(missing_req.values())
    if isinstance(missing_pref, dict):
        missing_pref = list(missing_pref.values())

    matching     = [s if isinstance(s, str) else str(s) for s in matching]
    missing_req  = [s if isinstance(s, str) else str(s) for s in missing_req]
    missing_pref = [s if isinstance(s, str) else str(s) for s in missing_pref]

    # ── Calculate match score ──────────────────────────────────
    match_score = gap_data.get("match_score", 50)
    if isinstance(match_score, str):
        try:
            match_score = int(match_score.replace("%", "").strip())
        except:
            match_score = 50

    if match_score >= 70:
        gap_severity = "low"
    elif match_score >= 40:
        gap_severity = "medium"
    else:
        gap_severity = "high"

    # ── Convert to bo's gap format ─────────────────────────────
    job_level_map = {
        "fresher": 1,
        "junior":  2,
        "mid":     2,
        "senior":  3
    }
    candidate_level_map = {
        "fresher": 0,
        "junior":  1,
        "mid":     2,
        "senior":  3
    }

    required_level  = job_level_map.get(job_level_str, 2)
    candidate_level = candidate_level_map.get(candidate_level_str, 0)

    bo_gaps       = []
    final_matched = []

    for skill in filtered_required:
        skill_lower = skill.lower().strip()

        # Double check filter for technical roles
        if is_technical:
            is_non_tech = any(nt in skill_lower for nt in NON_TECHNICAL_SKILLS)
            if is_non_tech:
                continue

        # Check if candidate has this skill
        # Use mapped skills as primary source of truth
        # not LLM output which can be wrong
        has_skill = skill_lower in mapped_resume_skills

        if has_skill:
            current_level = max(1, candidate_level)
        else:
            current_level = 0

        gap_size = required_level - current_level

        if gap_size <= 0:
            final_matched.append(skill)
        else:
            bo_gaps.append({
                "skill": skill,
                "current_level": current_level,
                "required_level": required_level,
                "gap_size": gap_size
            })

    # Recalculate actual match percentage
    total_skills = len(filtered_required)
    if total_skills > 0:
        actual_match_score = round(
            (len(final_matched) / total_skills) * 100
        )
    else:
        actual_match_score = 100

    return {
        # Original LLM output
        "matching_skills":          final_matched,
        "missing_required_skills":  [g["skill"] for g in bo_gaps],
        "missing_preferred_skills": missing_pref,
        "level_analysis":           gap_data.get("level_analysis", {}),
        "match_score":              actual_match_score,
        "match_verdict":            gap_data.get("match_verdict", ""),
        "overall_advice":           gap_data.get("overall_advice", ""),

        # Fields for bo's pipeline
        "gaps":           bo_gaps,
        "matched_skills": final_matched,
        "gap_severity":   gap_severity,
        "job_title":      job_title,
        "total_gaps":     len(bo_gaps),
        "total_matched":  len(final_matched),
    }