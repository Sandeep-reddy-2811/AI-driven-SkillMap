from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ai_pipeline.parser import parse_resume, parse_jd, analyze_skill_gap
from ai_pipeline.learning_path import generate_learning_path


@api_view(['GET'])
def health_check(request):
    return Response({
        "status": "ok",
        "message": "Adaptive Onboarding Engine API is running."
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def analyze_and_generate(request):

    resume_file = request.FILES.get('resume')
    jd_file     = request.FILES.get('job_description')
    resume_text = request.data.get('resume_text', '').strip()
    jd_text     = request.data.get('jd_text', '').strip()

    # ── Your correct validation ───────────────────────────────
    has_resume = resume_file or resume_text
    has_jd     = jd_file    or jd_text

    if not has_resume:
        return Response(
            {"error": "Please provide your resume — upload a PDF or paste the text."},
            status=status.HTTP_400_BAD_REQUEST
        )
    if not has_jd:
        return Response(
            {"error": "Please provide the job description — upload a PDF or paste the text."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ── Parse resume ──────────────────────────────────────────
    try:
        if resume_file:
            resume_data = parse_resume(resume_file)
        else:
            resume_data = parse_resume_text(resume_text)
    except Exception as e:
        return Response(
            {"error": "Failed to parse resume.", "details": str(e)},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    # ── Parse JD ──────────────────────────────────────────────
    try:
        if jd_file:
            jd_data = parse_jd(jd_file)
        else:
            jd_data = parse_jd_text(jd_text)
    except Exception as e:
        return Response(
            {"error": "Failed to parse job description.", "details": str(e)},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    # ── Normalize skills to simple strings for analyze_skill_gap
    # Friend's prompts return dicts — flatten them here
    raw_candidate_skills = resume_data.get("skills", [])
    if raw_candidate_skills and isinstance(raw_candidate_skills[0], dict):
        resume_data["skills"] = [s["skill"] for s in raw_candidate_skills if "skill" in s]

    raw_required_skills = jd_data.get("required_skills", [])
    if raw_required_skills and isinstance(raw_required_skills[0], dict):
        jd_data["required_skills"] = [s["skill"] for s in raw_required_skills if "skill" in s]

    # ── Skill gap analysis ────────────────────────────────────
    try:
        skill_gap_data = analyze_skill_gap(resume_data, jd_data)
    except Exception as e:
        return Response(
            {"error": "Skill gap analysis failed.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # ── Generate learning path ────────────────────────────────
    try:
        learning_path = generate_learning_path(skill_gap_data)
    except Exception as e:
        return Response(
            {"error": "Learning path generation failed.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # ── Return response ───────────────────────────────────────
    return Response({
        "candidate_name":   resume_data.get("name", "Candidate"),
        "experience_years": resume_data.get("experience_years", 0),
        "experience_level": resume_data.get("experience_level", "fresher"),
        "job_title":        jd_data.get("job_title", "Target Role"),
        "candidate_skills": resume_data.get("skills", []),
        "required_skills":  jd_data.get("required_skills", []),
        "skill_gaps":       skill_gap_data.get("gaps", []),
        "matched_skills":   skill_gap_data.get("matched_skills", []),
        "gap_severity":     skill_gap_data.get("gap_severity", "medium"),
        "learning_path":    learning_path.get("steps", []),
        "reasoning_trace":  learning_path.get("reasoning_trace", ""),
        "summary":          learning_path.get("summary", {}),
    }, status=status.HTTP_200_OK)


# ── Text parsers — friend's improved O*NET prompts ────────────

def parse_resume_text(text: str) -> dict:
    from groq import Groq
    import os, json

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    prompt = f"""
You are an expert resume parser and skills assessor.

Analyze this resume and extract the candidate's skills.
Map each skill to the closest O*NET standard skill name from this list:

O*NET Standard Skill Names (use EXACTLY these names):
- "Programming" (Python, Java, C++, coding, software development)
- "Critical Thinking" (problem solving, analytical thinking, logic)
- "Systems Analysis" (system design, architecture, requirements analysis)
- "Reading Comprehension" (technical documentation, research, reading)
- "Active Listening" (communication, teamwork, collaboration)
- "Troubleshooting" (debugging, issue resolution, error fixing)
- "Complex Problem Solving" (algorithms, competitive programming, optimization)
- "Systems Evaluation" (testing, performance evaluation, benchmarking)
- "Mathematics" (statistics, discrete math, probability, calculus)
- "Operations Analysis" (data analysis, business analysis, reporting)
- "Monitoring" (project tracking, performance monitoring, dashboards)
- "Judgment and Decision Making" (decision making, prioritization)
- "Coordination" (project management, team coordination, agile)
- "Writing" (documentation, technical writing, reports)

Rules:
1. Only include skills CLEARLY evidenced in the resume
2. Use EXACTLY the O*NET skill names from the list above
3. Return ONLY valid JSON, nothing else

Resume:
{text}

Return ONLY this exact JSON:
{{
    "name": "candidate full name",
    "experience_years": 0,
    "experience_level": "fresher",
    "skills": ["O*NET skill name 1", "O*NET skill name 2"]
}}
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def parse_jd_text(text: str) -> dict:
    from groq import Groq
    import os, json

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    prompt = f"""
You are an expert HR analyst and job description parser.

Analyze this job description and extract required skills.
Map each skill to the closest O*NET standard skill name from this list:

O*NET Standard Skill Names (use EXACTLY these names):
- "Programming" (Python, Java, C++, coding, software development)
- "Critical Thinking" (problem solving, analytical thinking, logic)
- "Systems Analysis" (system design, architecture, requirements analysis)
- "Reading Comprehension" (technical documentation, research, reading)
- "Active Listening" (communication, teamwork, collaboration)
- "Troubleshooting" (debugging, issue resolution, error fixing)
- "Complex Problem Solving" (algorithms, competitive programming, optimization)
- "Systems Evaluation" (testing, performance evaluation, benchmarking)
- "Mathematics" (statistics, discrete math, probability, calculus)
- "Operations Analysis" (data analysis, business analysis, reporting)
- "Monitoring" (project tracking, performance monitoring)
- "Judgment and Decision Making" (decision making, prioritization)
- "Coordination" (project management, team coordination, agile)
- "Writing" (documentation, technical writing)

Rules:
1. Map ALL required skills from the JD to O*NET names
2. Use EXACTLY the O*NET skill names from the list above
3. Return ONLY valid JSON, nothing else

Job Description:
{text}

Return ONLY this exact JSON:
{{
    "job_title": "exact job title",
    "experience_required": "X-Y years",
    "required_skills": ["O*NET skill name 1", "O*NET skill name 2"]
}}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())