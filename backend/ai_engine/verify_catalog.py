import json

with open("course_catalog.json", "r") as f:
    catalog = json.load(f)

# Check first 3 courses for resources
print("Checking resources in catalog...\n")
for course in catalog[:3]:
    print(f"Course: {course['title']}")
    print(f"Level: {course['level']}")
    
    if "resources" in course:
        print(f"Resources ({len(course['resources'])}):")
        for r in course["resources"]:
            print(f"  → {r['platform']}: {r['title']}")
    elif "link" in course:
        print(f"  ⚠ Still has old single link: {course['link']}")
    
    print()