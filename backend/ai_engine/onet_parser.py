import pandas as pd
import json

# ---- Load Data ----
def load_data():
    print("Loading O*NET data...")
    skills_df = pd.read_excel("Skills.xlsx")
    occ_df = pd.read_excel("Occupation Data.xlsx")

    # Keep only LV (Level) rows
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

    skills.sort(key=lambda x: x["level_score"], reverse=True)
    return skills[:8]


course_links = {

    # ============================================
    # TECHNICAL SKILLS
    # Beginner → Free platforms
    # Intermediate → Udemy / Coursera
    # Expert → edX / LinkedIn Learning / GitHub
    # ============================================

    "Programming": {
        "beginner": [
            {"platform": "Khan Academy", "title": "Intro to Programming", "link": "https://www.khanacademy.org/computing/intro-to-python-fundamentals", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Python Full Course", "link": "https://www.freecodecamp.org/learn/scientific-computing-with-python", "type": "interactive"},
            {"platform": "YouTube", "title": "Python for Beginners - Mosh", "link": "https://www.youtube.com/watch?v=kqtD5dpn9C8", "type": "free video"}
        ],
        "intermediate": [
            {"platform": "Udemy", "title": "Complete Python Bootcamp", "link": "https://www.udemy.com/course/complete-python-bootcamp", "type": "video course"},
            {"platform": "Coursera", "title": "Python for Everybody", "link": "https://www.coursera.org/specializations/python", "type": "video course"},
            {"platform": "Kaggle", "title": "Python Course", "link": "https://www.kaggle.com/learn/python", "type": "interactive"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Python Programming", "link": "https://www.edx.org/learn/computer-programming", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Python Advanced Topics", "link": "https://www.linkedin.com/learning/topics/python", "type": "professional course"},
            {"platform": "GitHub", "title": "Real Python Projects", "link": "https://github.com/topics/python", "type": "hands-on projects"}
        ]
    },

    "Critical Thinking": {
        "beginner": [
            {"platform": "Khan Academy", "title": "Logic and Reasoning", "link": "https://www.khanacademy.org/computing", "type": "free course"},
            {"platform": "YouTube", "title": "Critical Thinking Basics", "link": "https://www.youtube.com/watch?v=Cum3k-Wglfw", "type": "free video"},
            {"platform": "freeCodeCamp", "title": "Think Like a Programmer", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Critical Thinking Skills", "link": "https://www.coursera.org/learn/critical-thinking-skills", "type": "video course"},
            {"platform": "Udemy", "title": "Master Critical Thinking", "link": "https://www.udemy.com/course/critical-thinking", "type": "video course"},
            {"platform": "Coursera", "title": "Problem Solving Skills", "link": "https://www.coursera.org/learn/problem-solving", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Critical Thinking", "link": "https://www.edx.org/learn/critical-thinking", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Strategic Thinking", "link": "https://www.linkedin.com/learning/topics/strategic-thinking", "type": "professional course"},
            {"platform": "edX", "title": "Decision Making and Scenarios", "link": "https://www.edx.org/learn/decision-making", "type": "university course"}
        ]
    },

    "Reading Comprehension": {
        "beginner": [
            {"platform": "Khan Academy", "title": "Reading and Comprehension", "link": "https://www.khanacademy.org/ela", "type": "free course"},
            {"platform": "YouTube", "title": "Reading Comprehension Tips", "link": "https://www.youtube.com/watch?v=xHMDOuYSAaE", "type": "free video"},
            {"platform": "freeCodeCamp", "title": "English Reading Skills", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Academic English Reading", "link": "https://www.coursera.org/learn/academic-english", "type": "video course"},
            {"platform": "Udemy", "title": "Speed Reading Mastery", "link": "https://www.udemy.com/course/speed-reading", "type": "video course"},
            {"platform": "Coursera", "title": "Communication Skills", "link": "https://www.coursera.org/learn/communication-skills", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Reading and Analysis", "link": "https://www.edx.org/learn/reading", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Business Reading Skills", "link": "https://www.linkedin.com/learning/topics/reading-comprehension", "type": "professional course"},
            {"platform": "edX", "title": "Critical Reading Skills", "link": "https://www.edx.org/learn/critical-thinking", "type": "university course"}
        ]
    },

    "Systems Analysis": {
        "beginner": [
            {"platform": "YouTube", "title": "Systems Analysis Basics", "link": "https://www.youtube.com/watch?v=FzKnlJ0OIOU", "type": "free video"},
            {"platform": "Khan Academy", "title": "Systems Thinking Intro", "link": "https://www.khanacademy.org/computing", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Systems Fundamentals", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Udemy", "title": "Systems Analysis and Design", "link": "https://www.udemy.com/course/systems-analysis-and-design", "type": "video course"},
            {"platform": "Coursera", "title": "Systems Thinking", "link": "https://www.coursera.org/learn/systems-thinking", "type": "video course"},
            {"platform": "Coursera", "title": "Business Analysis", "link": "https://www.coursera.org/learn/business-analysis", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Systems Engineering", "link": "https://www.edx.org/learn/systems-engineering", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Advanced Systems Analysis", "link": "https://www.linkedin.com/learning/topics/systems-analysis", "type": "professional course"},
            {"platform": "edX", "title": "Systems Architecture", "link": "https://www.edx.org/learn/systems-engineering", "type": "university course"}
        ]
    },

    "Troubleshooting": {
        "beginner": [
            {"platform": "YouTube", "title": "Troubleshooting Basics", "link": "https://www.youtube.com/watch?v=3RjQoifQKqg", "type": "free video"},
            {"platform": "freeCodeCamp", "title": "IT Support Basics", "link": "https://www.freecodecamp.org", "type": "interactive"},
            {"platform": "Khan Academy", "title": "Problem Diagnosis", "link": "https://www.khanacademy.org/computing", "type": "free course"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "IT Support Professional", "link": "https://www.coursera.org/professional-certificates/google-it-support", "type": "certificate"},
            {"platform": "Udemy", "title": "Advanced Troubleshooting", "link": "https://www.udemy.com/course/troubleshooting-skills", "type": "video course"},
            {"platform": "Coursera", "title": "Technical Support Fundamentals", "link": "https://www.coursera.org/learn/technical-support-fundamentals", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced IT Management", "link": "https://www.edx.org/learn/information-technology", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Expert Troubleshooting", "link": "https://www.linkedin.com/learning/topics/troubleshooting", "type": "professional course"},
            {"platform": "GitHub", "title": "Open Source Debugging Projects", "link": "https://github.com/topics/debugging", "type": "hands-on projects"}
        ]
    },

    "Complex Problem Solving": {
        "beginner": [
            {"platform": "YouTube", "title": "Problem Solving Techniques", "link": "https://www.youtube.com/watch?v=Lkv_Ku5dQEA", "type": "free video"},
            {"platform": "Khan Academy", "title": "Logic and Problem Solving", "link": "https://www.khanacademy.org/computing", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Algorithmic Thinking", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Creative Problem Solving", "link": "https://www.coursera.org/learn/creative-problem-solving", "type": "video course"},
            {"platform": "Udemy", "title": "Problem Solving Masterclass", "link": "https://www.udemy.com/course/problem-solving-skills", "type": "video course"},
            {"platform": "Coursera", "title": "Design Thinking", "link": "https://www.coursera.org/learn/design-thinking", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Problem Solving", "link": "https://www.edx.org/learn/problem-solving", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Executive Problem Solving", "link": "https://www.linkedin.com/learning/topics/problem-solving", "type": "professional course"},
            {"platform": "edX", "title": "Strategic Decision Making", "link": "https://www.edx.org/learn/decision-making", "type": "university course"}
        ]
    },

    "Systems Evaluation": {
        "beginner": [
            {"platform": "YouTube", "title": "Systems Evaluation Intro", "link": "https://www.youtube.com/results?search_query=systems+evaluation+basics", "type": "free video"},
            {"platform": "Khan Academy", "title": "Evaluating Systems", "link": "https://www.khanacademy.org/computing", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "System Design Basics", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Systems Thinking", "link": "https://www.coursera.org/learn/systems-thinking", "type": "video course"},
            {"platform": "Udemy", "title": "Systems Evaluation Methods", "link": "https://www.udemy.com/course/systems-analysis-and-design", "type": "video course"},
            {"platform": "Coursera", "title": "Business Systems Analysis", "link": "https://www.coursera.org/learn/business-analysis", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Systems Engineering", "link": "https://www.edx.org/learn/systems-engineering", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Systems Evaluation Expert", "link": "https://www.linkedin.com/learning/topics/systems-analysis", "type": "professional course"},
            {"platform": "edX", "title": "Enterprise Architecture", "link": "https://www.edx.org/learn/enterprise-architecture", "type": "university course"}
        ]
    },

    "Judgment and Decision Making": {
        "beginner": [
            {"platform": "YouTube", "title": "Decision Making Basics", "link": "https://www.youtube.com/watch?v=d7Jnmi2BkS8", "type": "free video"},
            {"platform": "Khan Academy", "title": "Logical Decision Making", "link": "https://www.khanacademy.org/computing", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Problem Solving Fundamentals", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Decision Making Skills", "link": "https://www.coursera.org/learn/decision-making", "type": "video course"},
            {"platform": "Udemy", "title": "Judgment and Decision Making", "link": "https://www.udemy.com/course/decision-making-skills", "type": "video course"},
            {"platform": "Coursera", "title": "Critical Thinking Skills", "link": "https://www.coursera.org/learn/critical-thinking-skills", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Decision Making", "link": "https://www.edx.org/learn/decision-making", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Executive Decision Making", "link": "https://www.linkedin.com/learning/topics/decision-making", "type": "professional course"},
            {"platform": "edX", "title": "Strategic Leadership", "link": "https://www.edx.org/learn/leadership", "type": "university course"}
        ]
    },

    "Operations Analysis": {
        "beginner": [
            {"platform": "YouTube", "title": "Operations Analysis Intro", "link": "https://www.youtube.com/results?search_query=operations+analysis+basics", "type": "free video"},
            {"platform": "Khan Academy", "title": "Business Operations Basics", "link": "https://www.khanacademy.org/economics-finance-domain", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Data Analysis Basics", "link": "https://www.freecodecamp.org/learn/data-analysis-with-python", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Operations Management", "link": "https://www.coursera.org/learn/operations-management", "type": "video course"},
            {"platform": "Udemy", "title": "Operations Analysis Complete", "link": "https://www.udemy.com/course/operations-analysis", "type": "video course"},
            {"platform": "Coursera", "title": "Supply Chain Operations", "link": "https://www.coursera.org/learn/supply-chain-operations", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Operations Management", "link": "https://www.edx.org/learn/operations-management", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Operations Leadership", "link": "https://www.linkedin.com/learning/topics/operations", "type": "professional course"},
            {"platform": "edX", "title": "Operations Strategy", "link": "https://www.edx.org/learn/operations-management", "type": "university course"}
        ]
    },

    # ============================================
    # BUSINESS SKILLS
    # ============================================

    "Active Listening": {
        "beginner": [
            {"platform": "YouTube", "title": "Active Listening Skills", "link": "https://www.youtube.com/watch?v=rzsVh8YwZEQ", "type": "free video"},
            {"platform": "Khan Academy", "title": "Communication Fundamentals", "link": "https://www.khanacademy.org/ela", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Communication Basics", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Effective Communication", "link": "https://www.coursera.org/learn/communication-skills", "type": "video course"},
            {"platform": "Udemy", "title": "Active Listening Masterclass", "link": "https://www.udemy.com/course/active-listening-skills", "type": "video course"},
            {"platform": "Coursera", "title": "Business Communication", "link": "https://www.coursera.org/learn/effective-communication", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Leadership Communication", "link": "https://www.edx.org/learn/leadership", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Executive Listening Skills", "link": "https://www.linkedin.com/learning/topics/active-listening", "type": "professional course"},
            {"platform": "edX", "title": "Influencing and Persuasion", "link": "https://www.edx.org/learn/communication", "type": "university course"}
        ]
    },

    "Speaking": {
        "beginner": [
            {"platform": "YouTube", "title": "Public Speaking for Beginners", "link": "https://www.youtube.com/watch?v=AykYRO5d_lI", "type": "free video"},
            {"platform": "Khan Academy", "title": "Grammar and Speaking", "link": "https://www.khanacademy.org/ela", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Communication Skills", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Public Speaking", "link": "https://www.coursera.org/learn/public-speaking", "type": "video course"},
            {"platform": "Udemy", "title": "Public Speaking Complete", "link": "https://www.udemy.com/course/public-speaking-complete", "type": "video course"},
            {"platform": "Coursera", "title": "Dynamic Public Speaking", "link": "https://www.coursera.org/specializations/public-speaking", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Executive Communication", "link": "https://www.edx.org/learn/communication", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Executive Presence", "link": "https://www.linkedin.com/learning/topics/public-speaking", "type": "professional course"},
            {"platform": "edX", "title": "Leadership and Influence", "link": "https://www.edx.org/learn/leadership", "type": "university course"}
        ]
    },

    "Negotiation": {
        "beginner": [
            {"platform": "YouTube", "title": "Negotiation Basics", "link": "https://www.youtube.com/watch?v=MKUy12QTJ0A", "type": "free video"},
            {"platform": "Khan Academy", "title": "Conflict Resolution Basics", "link": "https://www.khanacademy.org/ela", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Communication and Persuasion", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Successful Negotiation", "link": "https://www.coursera.org/learn/negotiation", "type": "video course"},
            {"platform": "Udemy", "title": "Negotiation Masterclass", "link": "https://www.udemy.com/course/negotiation-skills", "type": "video course"},
            {"platform": "Coursera", "title": "Business Negotiation", "link": "https://www.coursera.org/learn/negotiation-introduction", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Strategic Negotiation", "link": "https://www.edx.org/learn/negotiation", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Advanced Negotiation", "link": "https://www.linkedin.com/learning/topics/negotiation", "type": "professional course"},
            {"platform": "edX", "title": "Negotiation Mastery", "link": "https://www.edx.org/learn/negotiation", "type": "university course"}
        ]
    },

    "Coordination": {
        "beginner": [
            {"platform": "YouTube", "title": "Team Coordination Basics", "link": "https://www.youtube.com/results?search_query=team+coordination+basics", "type": "free video"},
            {"platform": "Khan Academy", "title": "Teamwork Fundamentals", "link": "https://www.khanacademy.org", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Collaboration Skills", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Leadership and Management", "link": "https://www.coursera.org/learn/leadership-management", "type": "video course"},
            {"platform": "Udemy", "title": "Team Coordination Skills", "link": "https://www.udemy.com/course/team-coordination", "type": "video course"},
            {"platform": "Coursera", "title": "Project Management Basics", "link": "https://www.coursera.org/learn/project-management-foundations", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Leadership", "link": "https://www.edx.org/learn/leadership", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Strategic Coordination", "link": "https://www.linkedin.com/learning/topics/coordination", "type": "professional course"},
            {"platform": "edX", "title": "Organizational Leadership", "link": "https://www.edx.org/learn/organizational-leadership", "type": "university course"}
        ]
    },

    "Social Perceptiveness": {
        "beginner": [
            {"platform": "YouTube", "title": "Emotional Intelligence Basics", "link": "https://www.youtube.com/watch?v=Y7m9eNoB3NU", "type": "free video"},
            {"platform": "Khan Academy", "title": "Social Skills Fundamentals", "link": "https://www.khanacademy.org/ela", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Interpersonal Skills", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Emotional Intelligence", "link": "https://www.coursera.org/learn/emotional-intelligence", "type": "video course"},
            {"platform": "Udemy", "title": "Social Intelligence", "link": "https://www.udemy.com/course/emotional-intelligence", "type": "video course"},
            {"platform": "Coursera", "title": "Inspiring Leadership", "link": "https://www.coursera.org/learn/inspiring-leadership", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced EQ Leadership", "link": "https://www.edx.org/learn/leadership", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Executive Emotional Intelligence", "link": "https://www.linkedin.com/learning/topics/emotional-intelligence", "type": "professional course"},
            {"platform": "edX", "title": "Organizational Psychology", "link": "https://www.edx.org/learn/psychology", "type": "university course"}
        ]
    },

    "Instructing": {
        "beginner": [
            {"platform": "YouTube", "title": "Teaching and Instructing Basics", "link": "https://www.youtube.com/results?search_query=how+to+teach+effectively", "type": "free video"},
            {"platform": "Khan Academy", "title": "Communication for Teaching", "link": "https://www.khanacademy.org/ela", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Presentation Skills", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Teaching Skills", "link": "https://www.coursera.org/learn/teaching-skills", "type": "video course"},
            {"platform": "Udemy", "title": "Instructional Design", "link": "https://www.udemy.com/course/instructional-design", "type": "video course"},
            {"platform": "Coursera", "title": "Learning and Development", "link": "https://www.coursera.org/learn/learning-development", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Instructional Design", "link": "https://www.edx.org/learn/instructional-design", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Corporate Training Expert", "link": "https://www.linkedin.com/learning/topics/instructional-design", "type": "professional course"},
            {"platform": "edX", "title": "Learning Sciences", "link": "https://www.edx.org/learn/education", "type": "university course"}
        ]
    },

    "Service Orientation": {
        "beginner": [
            {"platform": "YouTube", "title": "Customer Service Basics", "link": "https://www.youtube.com/watch?v=whi7JTmNSmA", "type": "free video"},
            {"platform": "Khan Academy", "title": "Communication and Service", "link": "https://www.khanacademy.org/ela", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "People Skills Fundamentals", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Customer Service Excellence", "link": "https://www.coursera.org/learn/customer-service", "type": "video course"},
            {"platform": "Udemy", "title": "Service Quality Management", "link": "https://www.udemy.com/course/customer-service-excellence", "type": "video course"},
            {"platform": "Coursera", "title": "Client Management", "link": "https://www.coursera.org/learn/client-management", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Customer Experience", "link": "https://www.edx.org/learn/customer-experience", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Service Leadership", "link": "https://www.linkedin.com/learning/topics/customer-service", "type": "professional course"},
            {"platform": "edX", "title": "Service Design", "link": "https://www.edx.org/learn/design-thinking", "type": "university course"}
        ]
    },

    "Management of Personnel Resources": {
        "beginner": [
            {"platform": "YouTube", "title": "HR Management Basics", "link": "https://www.youtube.com/watch?v=5vDfDNFMHtg", "type": "free video"},
            {"platform": "Khan Academy", "title": "Leadership Fundamentals", "link": "https://www.khanacademy.org", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Team Management Basics", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Human Resource Management", "link": "https://www.coursera.org/learn/human-resource-management", "type": "video course"},
            {"platform": "Udemy", "title": "HR Management Complete", "link": "https://www.udemy.com/course/hr-management", "type": "video course"},
            {"platform": "Coursera", "title": "Managing People", "link": "https://www.coursera.org/learn/managing-people", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Strategic HR Management", "link": "https://www.edx.org/learn/human-resources", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Advanced People Management", "link": "https://www.linkedin.com/learning/topics/people-management", "type": "professional course"},
            {"platform": "edX", "title": "People Analytics", "link": "https://www.edx.org/learn/people-analytics", "type": "university course"}
        ]
    },

    "Management of Financial Resources": {
        "beginner": [
            {"platform": "YouTube", "title": "Finance Basics", "link": "https://www.youtube.com/watch?v=WEDIj9JBTC8", "type": "free video"},
            {"platform": "Khan Academy", "title": "Personal Finance", "link": "https://www.khanacademy.org/college-careers-more/personal-finance", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Financial Literacy", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Financial Management", "link": "https://www.coursera.org/learn/finance-for-non-finance", "type": "video course"},
            {"platform": "Udemy", "title": "Business Finance Masterclass", "link": "https://www.udemy.com/course/financial-management", "type": "video course"},
            {"platform": "Coursera", "title": "Business Finance", "link": "https://www.coursera.org/learn/business-finance", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Financial Management", "link": "https://www.edx.org/learn/finance", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "CFO Level Finance", "link": "https://www.linkedin.com/learning/topics/finance", "type": "professional course"},
            {"platform": "edX", "title": "Corporate Finance", "link": "https://www.edx.org/learn/corporate-finance", "type": "university course"}
        ]
    },

    "Time Management": {
        "beginner": [
            {"platform": "YouTube", "title": "Time Management Tips", "link": "https://www.youtube.com/watch?v=iDbdXTMnOmE", "type": "free video"},
            {"platform": "Khan Academy", "title": "Study and Time Skills", "link": "https://www.khanacademy.org/college-careers-more", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Productivity Basics", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Work Smarter Not Harder", "link": "https://www.coursera.org/learn/work-smarter-not-harder", "type": "video course"},
            {"platform": "Udemy", "title": "Time Management Mastery", "link": "https://www.udemy.com/course/time-management-mastery", "type": "video course"},
            {"platform": "Coursera", "title": "Productivity and Time", "link": "https://www.coursera.org/learn/productivity", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Productivity", "link": "https://www.edx.org/learn/productivity", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Executive Time Management", "link": "https://www.linkedin.com/learning/topics/time-management", "type": "professional course"},
            {"platform": "edX", "title": "Strategic Planning", "link": "https://www.edx.org/learn/strategic-management", "type": "university course"}
        ]
    },

    "Monitoring": {
        "beginner": [
            {"platform": "YouTube", "title": "Project Monitoring Basics", "link": "https://www.youtube.com/results?search_query=project+monitoring+basics", "type": "free video"},
            {"platform": "Khan Academy", "title": "Planning and Tracking", "link": "https://www.khanacademy.org", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Data Tracking Basics", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Project Execution", "link": "https://www.coursera.org/learn/project-execution", "type": "video course"},
            {"platform": "Udemy", "title": "Project Monitoring and Control", "link": "https://www.udemy.com/course/project-monitoring", "type": "video course"},
            {"platform": "Coursera", "title": "Project Management Foundations", "link": "https://www.coursera.org/learn/project-management-foundations", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Project Management", "link": "https://www.edx.org/learn/project-management", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Strategic Monitoring", "link": "https://www.linkedin.com/learning/topics/monitoring", "type": "professional course"},
            {"platform": "edX", "title": "PMP Certification Prep", "link": "https://www.edx.org/learn/project-management", "type": "university course"}
        ]
    },

    "Writing": {
        "beginner": [
            {"platform": "YouTube", "title": "Writing Skills Basics", "link": "https://www.youtube.com/watch?v=8RRmSMdcpWc", "type": "free video"},
            {"platform": "Khan Academy", "title": "Grammar and Writing", "link": "https://www.khanacademy.org/ela", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Technical Writing Basics", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Business Writing", "link": "https://www.coursera.org/learn/writing-skills", "type": "video course"},
            {"platform": "Udemy", "title": "Professional Writing", "link": "https://www.udemy.com/course/business-writing", "type": "video course"},
            {"platform": "Coursera", "title": "Academic Writing", "link": "https://www.coursera.org/learn/academic-english", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Professional Writing", "link": "https://www.edx.org/learn/writing", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Executive Writing", "link": "https://www.linkedin.com/learning/topics/writing", "type": "professional course"},
            {"platform": "edX", "title": "Content Strategy", "link": "https://www.edx.org/learn/content-strategy", "type": "university course"}
        ]
    },

    # ============================================
    # OPERATIONAL SKILLS
    # ============================================

    "Equipment Maintenance": {
        "beginner": [
            {"platform": "YouTube", "title": "Equipment Maintenance Basics", "link": "https://www.youtube.com/results?search_query=equipment+maintenance+basics", "type": "free video"},
            {"platform": "Khan Academy", "title": "Basic Mechanics", "link": "https://www.khanacademy.org/science/physics", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Technical Skills Basics", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Maintenance Management", "link": "https://www.coursera.org/learn/maintenance-management", "type": "video course"},
            {"platform": "Udemy", "title": "Equipment Maintenance Complete", "link": "https://www.udemy.com/course/equipment-maintenance", "type": "video course"},
            {"platform": "Coursera", "title": "Industrial Safety", "link": "https://www.coursera.org/learn/industrial-safety", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Reliability Engineering", "link": "https://www.edx.org/learn/engineering", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Maintenance Strategy", "link": "https://www.linkedin.com/learning/topics/maintenance", "type": "professional course"},
            {"platform": "edX", "title": "Asset Management", "link": "https://www.edx.org/learn/asset-management", "type": "university course"}
        ]
    },

    "Quality Control Analysis": {
        "beginner": [
            {"platform": "YouTube", "title": "Quality Control Basics", "link": "https://www.youtube.com/watch?v=JTRMjHb0MXA", "type": "free video"},
            {"platform": "Khan Academy", "title": "Statistics for Quality", "link": "https://www.khanacademy.org/math/statistics-probability", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Data Analysis Basics", "link": "https://www.freecodecamp.org/learn/data-analysis-with-python", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Six Sigma Principles", "link": "https://www.coursera.org/learn/six-sigma-principles", "type": "video course"},
            {"platform": "Udemy", "title": "Quality Management Complete", "link": "https://www.udemy.com/course/quality-management", "type": "video course"},
            {"platform": "Coursera", "title": "Lean Six Sigma Green Belt", "link": "https://www.coursera.org/learn/six-sigma-green-belt", "type": "certificate"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Quality Engineering", "link": "https://www.edx.org/learn/quality-management", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Quality Strategy", "link": "https://www.linkedin.com/learning/topics/quality-management", "type": "professional course"},
            {"platform": "edX", "title": "Six Sigma Black Belt", "link": "https://www.edx.org/learn/six-sigma", "type": "university course"}
        ]
    },

    "Equipment Selection": {
        "beginner": [
            {"platform": "YouTube", "title": "Equipment Selection Guide", "link": "https://www.youtube.com/results?search_query=industrial+equipment+selection", "type": "free video"},
            {"platform": "Khan Academy", "title": "Physics and Engineering Basics", "link": "https://www.khanacademy.org/science/physics", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Technical Analysis Basics", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Industrial Equipment Management", "link": "https://www.coursera.org/learn/industrial-equipment", "type": "video course"},
            {"platform": "Udemy", "title": "Equipment Management", "link": "https://www.udemy.com/course/equipment-management", "type": "video course"},
            {"platform": "Coursera", "title": "Operations Management", "link": "https://www.coursera.org/learn/operations-management", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Equipment Engineering", "link": "https://www.edx.org/learn/engineering", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Equipment Strategy", "link": "https://www.linkedin.com/learning/topics/equipment-management", "type": "professional course"},
            {"platform": "edX", "title": "Asset Management", "link": "https://www.edx.org/learn/asset-management", "type": "university course"}
        ]
    },

    "Operation and Control": {
        "beginner": [
            {"platform": "YouTube", "title": "Operations Control Basics", "link": "https://www.youtube.com/results?search_query=operations+control+basics", "type": "free video"},
            {"platform": "Khan Academy", "title": "Systems and Control", "link": "https://www.khanacademy.org/science/physics", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Process Control Basics", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Operations Management", "link": "https://www.coursera.org/learn/operations-management", "type": "video course"},
            {"platform": "Udemy", "title": "Production Control", "link": "https://www.udemy.com/course/operations-control", "type": "video course"},
            {"platform": "Coursera", "title": "Supply Chain Operations", "link": "https://www.coursera.org/learn/supply-chain-operations", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Operations", "link": "https://www.edx.org/learn/operations-management", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Operations Leadership", "link": "https://www.linkedin.com/learning/topics/operations", "type": "professional course"},
            {"platform": "edX", "title": "Industrial Operations", "link": "https://www.edx.org/learn/operations-management", "type": "university course"}
        ]
    },

    "Mathematics": {
        "beginner": [
            {"platform": "Khan Academy", "title": "Basic Mathematics", "link": "https://www.khanacademy.org/math", "type": "free course"},
            {"platform": "YouTube", "title": "Math for Beginners", "link": "https://www.youtube.com/watch?v=OmJ-4B-mS-Y", "type": "free video"},
            {"platform": "freeCodeCamp", "title": "Mathematics Fundamentals", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Mathematics for Engineers", "link": "https://www.coursera.org/learn/mathematics-for-engineers", "type": "video course"},
            {"platform": "Udemy", "title": "Applied Mathematics", "link": "https://www.udemy.com/course/applied-mathematics", "type": "video course"},
            {"platform": "Khan Academy", "title": "Algebra and Statistics", "link": "https://www.khanacademy.org/math/algebra", "type": "free course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Mathematics", "link": "https://www.edx.org/learn/mathematics", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Applied Math for Professionals", "link": "https://www.linkedin.com/learning/topics/mathematics", "type": "professional course"},
            {"platform": "edX", "title": "Mathematical Thinking", "link": "https://www.edx.org/learn/mathematics", "type": "university course"}
        ]
    },

    "Operation Monitoring": {
        "beginner": [
            {"platform": "YouTube", "title": "Operation Monitoring Intro", "link": "https://www.youtube.com/results?search_query=operation+monitoring+basics", "type": "free video"},
            {"platform": "Khan Academy", "title": "Data Tracking Basics", "link": "https://www.khanacademy.org", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Monitoring Systems Basics", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Operations Management", "link": "https://www.coursera.org/learn/operations-management", "type": "video course"},
            {"platform": "Udemy", "title": "Industrial Monitoring", "link": "https://www.udemy.com/course/operations-monitoring", "type": "video course"},
            {"platform": "Coursera", "title": "Process Monitoring", "link": "https://www.coursera.org/learn/process-improvement", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Operations Monitoring", "link": "https://www.edx.org/learn/operations-management", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Monitoring and Control Expert", "link": "https://www.linkedin.com/learning/topics/monitoring", "type": "professional course"},
            {"platform": "edX", "title": "Industrial Automation", "link": "https://www.edx.org/learn/automation", "type": "university course"}
        ]
    },

    "Management of Material Resources": {
        "beginner": [
            {"platform": "YouTube", "title": "Inventory Management Basics", "link": "https://www.youtube.com/results?search_query=inventory+management+basics", "type": "free video"},
            {"platform": "Khan Academy", "title": "Supply Chain Basics", "link": "https://www.khanacademy.org/economics-finance-domain", "type": "free course"},
            {"platform": "freeCodeCamp", "title": "Resource Management Basics", "link": "https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": "Supply Chain Management", "link": "https://www.coursera.org/learn/supply-chain-management", "type": "video course"},
            {"platform": "Udemy", "title": "Inventory Management", "link": "https://www.udemy.com/course/inventory-management", "type": "video course"},
            {"platform": "Coursera", "title": "Operations and Supply Chain", "link": "https://www.coursera.org/learn/operations-supply-chain", "type": "video course"}
        ],
        "expert": [
            {"platform": "edX", "title": "Advanced Supply Chain", "link": "https://www.edx.org/learn/supply-chain-management", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": "Supply Chain Strategy", "link": "https://www.linkedin.com/learning/topics/supply-chain", "type": "professional course"},
            {"platform": "edX", "title": "Logistics and Distribution", "link": "https://www.edx.org/learn/logistics", "type": "university course"}
        ]
    },
}


# ---- Default Resources (fallback for skills not in course_links) ----
def get_default_resources(skill_name, level):
    level_platforms = {
        "beginner": [
            {"platform": "YouTube", "title": f"{skill_name} for Beginners", "link": f"https://www.youtube.com/results?search_query={skill_name.replace(' ', '+')}+for+beginners", "type": "free video"},
            {"platform": "Khan Academy", "title": f"{skill_name} Basics", "link": f"https://www.khanacademy.org", "type": "free course"},
            {"platform": "freeCodeCamp", "title": f"{skill_name} Fundamentals", "link": f"https://www.freecodecamp.org", "type": "interactive"}
        ],
        "intermediate": [
            {"platform": "Coursera", "title": f"{skill_name} - Intermediate", "link": f"https://www.coursera.org/search?query={skill_name.replace(' ', '+')}", "type": "video course"},
            {"platform": "Udemy", "title": f"{skill_name} Complete Course", "link": f"https://www.udemy.com/courses/search/?q={skill_name.replace(' ', '+')}", "type": "video course"},
            {"platform": "Kaggle", "title": f"{skill_name} Practice", "link": f"https://www.kaggle.com/search?q={skill_name.replace(' ', '+')}", "type": "interactive"}
        ],
        "expert": [
            {"platform": "edX", "title": f"Advanced {skill_name}", "link": f"https://www.edx.org/search?q={skill_name.replace(' ', '+')}", "type": "university course"},
            {"platform": "LinkedIn Learning", "title": f"{skill_name} Professional", "link": f"https://www.linkedin.com/learning/search?keywords={skill_name.replace(' ', '+')}", "type": "professional course"},
            {"platform": "GitHub", "title": f"{skill_name} Projects", "link": f"https://github.com/topics/{skill_name.replace(' ', '-').lower()}", "type": "hands-on projects"}
        ]
    }
    return level_platforms.get(level, level_platforms["beginner"])

# ---- Build Full Course Catalog ----
def build_catalog(skills_df):

    target_jobs = {
        "technical": [
            "Software Developers",
            "Computer Network Architects",
            "Network and Computer Systems Administrators"
        ],
        "business": [
            "Human Resources Managers",
            "Marketing Managers",
            "Financial Managers"
        ],
        "operational": [
            "First-Line Supervisors of Production and Operating Workers",
            "Logisticians",
            "Industrial Production Managers"
        ]
    }

    domain_skills = {}
    job_skill_map = {}

    for domain, jobs in target_jobs.items():
        print(f"\nProcessing {domain} domain...")
        domain_skills[domain] = {}

        for job_keyword in jobs:
            skills = get_skills_for_job(skills_df, job_keyword)
            if skills:
                job_skill_map[job_keyword] = skills
                for s in skills:
                    skill_name = s["skill"]
                    if skill_name not in domain_skills[domain]:
                        domain_skills[domain][skill_name] = s["required_level"]

    catalog = []
    course_id = 1
    level_order = {"beginner": 1, "intermediate": 2, "expert": 3}

    for domain, skills in domain_skills.items():
        for skill_name, max_level in skills.items():

            skill_resources = course_links.get(skill_name, {})

            # Always add beginner
            beginner_resources = skill_resources.get(
                "beginner",
                get_default_resources(skill_name, "beginner")
            )
            catalog.append({
                "id": course_id,
                "title": f"{skill_name} - Fundamentals",
                "skill": skill_name,
                "level": "beginner",
                "domain": domain,
                "duration_weeks": 1,
                "resources": beginner_resources
            })
            course_id += 1

            # Add intermediate if needed
            if level_order[max_level] >= 2:
                intermediate_resources = skill_resources.get(
                    "intermediate",
                    get_default_resources(skill_name, "intermediate")
                )
                catalog.append({
                    "id": course_id,
                    "title": f"{skill_name} - Intermediate",
                    "skill": skill_name,
                    "level": "intermediate",
                    "domain": domain,
                    "duration_weeks": 2,
                    "resources": intermediate_resources
                })
                course_id += 1

            # Add expert if needed
            if level_order[max_level] >= 3:
                expert_resources = skill_resources.get(
                    "expert",
                    get_default_resources(skill_name, "expert")
                )
                catalog.append({
                    "id": course_id,
                    "title": f"{skill_name} - Advanced",
                    "skill": skill_name,
                    "level": "expert",
                    "domain": domain,
                    "duration_weeks": 3,
                    "resources": expert_resources
                })
                course_id += 1

    return catalog, job_skill_map

# ---- Manually Add Missing Operational Courses ----
def add_missing_courses(catalog):
    
    missing_skills = [
        ("Mathematics", "operational"),
        ("Equipment Selection", "operational"),
        ("Operation and Control", "operational"),
        ("Quality Control Analysis", "operational"),
        ("Equipment Maintenance", "operational"),
        ("Negotiation", "business"),
    ]
    
    last_id = max(c["id"] for c in catalog)
    course_id = last_id + 1
    
    level_order = {"beginner": 1, "intermediate": 2, "expert": 3}
    
    for skill_name, domain in missing_skills:
        skill_resources = course_links.get(skill_name, {})
        
        for level in ["beginner", "intermediate", "expert"]:
            resources = skill_resources.get(
                level,
                get_default_resources(skill_name, level)
            )
            catalog.append({
                "id": course_id,
                "title": f"{skill_name} - {'Fundamentals' if level == 'beginner' else 'Intermediate' if level == 'intermediate' else 'Advanced'}",
                "skill": skill_name,
                "level": level,
                "domain": domain,
                "duration_weeks": 1 if level == "beginner" else 2 if level == "intermediate" else 3,
                "resources": resources
            })
            course_id += 1
    
    return catalog

# ---- Save Results ----
def save_results(catalog, job_skill_map):
    with open("course_catalog.json", "w") as f:
        json.dump(catalog, f, indent=2)
    with open("job_skill_map.json", "w") as f:
        json.dump(job_skill_map, f, indent=2)
    print(f"\n✅ Saved course_catalog.json with {len(catalog)} courses")
    print(f"✅ Saved job_skill_map.json with {len(job_skill_map)} job roles")


# ---- Preview Results ----
def preview_results(catalog, job_skill_map):
    print("\n" + "="*50)
    print("CATALOG PREVIEW")
    print("="*50)

    domains = {}
    for c in catalog:
        domains[c["domain"]] = domains.get(c["domain"], 0) + 1
    for domain, count in domains.items():
        print(f"  {domain}: {count} courses")
    print(f"\nTotal: {len(catalog)} courses")

    print("\nSample course with resources:")
    sample = catalog[0]
    print(f"  [{sample['domain']}] {sample['title']} ({sample['level']})")
    for r in sample["resources"]:
        print(f"    → {r['platform']}: {r['title']}")

    print("\n" + "="*50)
    print("JOB SKILL MAP PREVIEW")
    print("="*50)
    for job, skills in list(job_skill_map.items())[:2]:
        print(f"\n{job}:")
        for s in skills[:4]:
            print(f"  - {s['skill']} → {s['required_level']} (score: {s['level_score']})")


# ---- Main ----
if __name__ == "__main__":
    skills_df, occ_df = load_data()
    catalog, job_skill_map = build_catalog(skills_df)
    catalog = add_missing_courses(catalog)
    save_results(catalog, job_skill_map)
    preview_results(catalog, job_skill_map)