
import re


def parse_list_field(value):
    """
    Convert a skills field stored as text into a Python list.

    Example:
    "['Python' 'SQL' 'Excel']"
    becomes:
    ['Python', 'SQL', 'Excel']
    """

    if not isinstance(value, str) or not value.strip():
        return []

    # Extract text enclosed in single quotes.
    items = re.findall(r"'([^']*)'", value)

    return [item.strip() for item in items if item.strip()]


def normalize_skill(skill):
    """
    Standardize a skill for comparison.
    Example: ' Python ' becomes 'python'.
    """

    return skill.strip().lower()


def calculate_skill_match(
    resume_skills,
    must_have_skills,
    nice_to_have_skills
):
    """
    Compare a candidate's skills with a job's requirements.
    """

    # Normalize skills so comparisons ignore capitalization and spaces.
    candidate_skills = {
        normalize_skill(skill) for skill in resume_skills
    }

    required_skills = {
        normalize_skill(skill) for skill in must_have_skills
    }

    optional_skills = {
        normalize_skill(skill) for skill in nice_to_have_skills
    }

    # Find matching and missing skills.
    matched_required = candidate_skills & required_skills
    missing_required = required_skills - candidate_skills
    matched_optional = candidate_skills & optional_skills

    # Calculate the must-have skill-match percentage.
    if required_skills:
        match_percentage = (
            len(matched_required) / len(required_skills)
        ) * 100
    else:
        match_percentage = 0.0

    return {
        "matched_must_have": sorted(matched_required),
        "missing_must_have": sorted(missing_required),
        "matched_nice_to_have": sorted(matched_optional),
        "skill_match_percentage": round(match_percentage, 2)
    }

    
def rank_candidates(resumes, job, top_n=10):
    """
    Rank resumes for one job by must-have skill match.
    """

    results = []

    for _, resume in resumes.iterrows():
        match = calculate_skill_match(
            resume["skills"],
            job["must_have_skills"],
            job["nice_to_have_skills"]
        )

        results.append({
            "resume_id": resume["resume_id"],
            "role": resume["role"],
            "years_experience": resume["years_experience"],
            "matched_skills": match["matched_must_have"],
            "missing_skills": match["missing_must_have"],
            "score": match["skill_match_percentage"]
        })

    # Highest skill-match score first.
    results.sort(key=lambda candidate: candidate["score"], reverse=True)

    return results[:top_n]

if __name__ == "__main__":
    import pandas as pd

    # Load the datasets
    resumes = pd.read_csv("data/resumes.csv")
    jobs = pd.read_csv("data/jobs.csv")

    # Convert skill fields from strings into Python lists
    resumes["skills"] = resumes["skills"].apply(parse_list_field)

    jobs["must_have_skills"] = jobs["must_have_skills"].apply(
        parse_list_field
    )

    jobs["nice_to_have_skills"] = jobs["nice_to_have_skills"].apply(
        parse_list_field
    )

    # Display the results
    print("Total resumes:", len(resumes))
    print("Total jobs:", len(jobs))

    print("\nFirst resume skills:")
    print(resumes.loc[0, "skills"])

    print("\nFirst job must-have skills:")
    print(jobs.loc[0, "must_have_skills"])

    print("\nFirst job nice-to-have skills:")
    print(jobs.loc[0, "nice_to_have_skills"])

    print("\nData types after processing:")
    print("Resume skills:", type(resumes.loc[0, "skills"]))
    print("Job skills:", type(jobs.loc[0, "must_have_skills"]))

    # Compare the first resume with the first job.
    resume = resumes.loc[0]
    job = jobs.loc[0]

    result = calculate_skill_match(
        resume["skills"],
        job["must_have_skills"],
        job["nice_to_have_skills"]
    )

    print("\n==============================")
    print("SKILL MATCHING RESULT")
    print("==============================")

    print("Candidate:", resume["resume_id"])
    print("Job:", job["job_id"])

    print("Matched must-have skills:",
          result["matched_must_have"])

    print("Missing must-have skills:",
          result["missing_must_have"])

    print("Matched nice-to-have skills:",
          result["matched_nice_to_have"])

    print("Must-have skill match:",
          str(result["skill_match_percentage"]) + "%")


    # Select the first job and rank candidates against it.
    job = jobs.iloc[0]

    ranked_candidates = rank_candidates(
        resumes=resumes,
        job=job,
        top_n=10
    )

    print("\n==============================")
    print("TOP 10 CANDIDATES")
    print("==============================")

    print("Job:", job["job_id"], "-", job["job_title"])
    print("Required skills:", job["must_have_skills"])

    for position, candidate in enumerate(ranked_candidates, start=1):
        print(f"\nRank: {position}")
        print("Resume ID:", candidate["resume_id"])
        print("Current role:", candidate["role"])
        print("Experience:", candidate["years_experience"], "years")
        print("Matched skills:", candidate["matched_skills"])
        print("Missing skills:", candidate["missing_skills"])
        print("Skill-match score:", candidate["score"], "%")