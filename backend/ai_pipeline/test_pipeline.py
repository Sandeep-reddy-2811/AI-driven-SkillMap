import os
import sys
from dotenv import load_dotenv

load_dotenv()

from parser import parse_resume, parse_jd, analyze_skill_gap
from learning_path import generate_learning_path

# Test with actual files
resume_path = "../resume.pdf"
jd_path = "../job_description.pdf"

print("="*60)
print("STEP 1: Parsing Resume...")
print("="*60)
resume_data = parse_resume(resume_path)
print(f"Name: {resume_data['name']}")
print(f"Skills found: {len(resume_data['skills'])}")
for s in resume_data['skills']:
    print(f"  ✓ {s['skill']} → {s['level']}")
    print(f"    Evidence: {s['evidence']}")

print("\n" + "="*60)
print("STEP 2: Parsing Job Description...")
print("="*60)
jd_data = parse_jd(jd_path)
print(f"Job: {jd_data['job_title']} at {jd_data['company']}")
print(f"Required skills: {len(jd_data['required_skills'])}")
for s in jd_data['required_skills']:
    print(f"  → {s['skill']} : {s['required_level']}")

print("\n" + "="*60)
print("STEP 3: Analyzing Skill Gaps...")
print("="*60)
gap_data = analyze_skill_gap(resume_data, jd_data)
print(f"Matched: {len(gap_data['matched_skills'])} skills")
print(f"Gaps: {len(gap_data['gaps'])} skills")
print(f"Severity: {gap_data['gap_severity']}")
print("\nMatched skills:")
for s in gap_data['matched_skills']:
    print(f"  ✅ {s}")
print("\nSkill gaps:")
for g in gap_data['gaps']:
    print(f"  ❌ {g['skill']} (current: {g['current_level']}, need: {g['required_level']})")

print("\n" + "="*60)
print("STEP 4: Generating Learning Path...")
print("="*60)
result = generate_learning_path(gap_data)
print(f"Steps: {len(result['steps'])}")
print(f"\nReasoning Trace:")
print(result['reasoning_trace'])