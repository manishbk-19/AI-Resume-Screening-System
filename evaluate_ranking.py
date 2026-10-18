import ast
import pandas as pd

from services.data_processor import (
    parse_list_field,
    rank_candidates
)


# 1. Load the datasets
resumes = pd.read_csv("data/resumes.csv")
jobs = pd.read_csv("data/jobs.csv")
matches = pd.read_csv("data/matches.csv")

# 2. Convert skill fields into Python lists
resumes["skills"] = resumes["skills"].apply(parse_list_field)
jobs["must_have_skills"] = jobs["must_have_skills"].apply(parse_list_field)
jobs["nice_to_have_skills"] = jobs["nice_to_have_skills"].apply(parse_list_field)

# 3. Select the first job
job_id = "J_000000"

job = jobs.loc[jobs["job_id"] == job_id].iloc[0]

# 4. Get the known relevant resume IDs
match_row = matches.loc[matches["job_id"] == job_id].iloc[0]

relevant_ids = set(
    parse_list_field(match_row["relevant_resume_ids"])
)

# 5. Rank candidates using our algorithm
ranked_candidates = rank_candidates(
    resumes,
    job,
    top_n=len(resumes)
)

top_10 = ranked_candidates[:10]

# 6. Compare the top 10 with the known relevant candidates

# Evaluate only the first 10 candidates
top_ids = [
    candidate["resume_id"]
    for candidate in top_10
]

relevant_in_top_10 = [
    resume_id
    for resume_id in top_ids
    if resume_id in relevant_ids
]

precision_at_10 = len(relevant_in_top_10) / 10

recall_at_10 = (
    len(relevant_in_top_10) / len(relevant_ids)
    if relevant_ids
    else 0
)

# Find where the known relevant candidates appear
relevant_ranks = [
    (rank, candidate)
    for rank, candidate in enumerate(ranked_candidates, start=1)
    if candidate["resume_id"] in relevant_ids
]

print("\n===== DIAGNOSTIC RESULTS =====")
print("Relevant candidates found in all rankings:", len(relevant_ranks))

print("\nFirst 10 relevant candidates in the ranking:")
for rank, candidate in relevant_ranks[:10]:
    print(
        f"Rank: {rank} | "
        f"ID: {candidate['resume_id']} | "
        f"Score: {candidate['score']}% | "
        f"Skills: {candidate['skill_score']}% | "
        f"Role: {candidate['role_score']}% | "
        f"Seniority: {candidate['seniority_score']}"
    )

print("\nRelevant candidates scoring 100%:",
      sum(1 for _, candidate in relevant_ranks
          if candidate["score"] == 100.0))


relevant_in_top_10 = [
    resume_id
    for resume_id in top_ids
    if resume_id in relevant_ids
]

# 7. Calculate evaluation metrics
precision_at_10 = len(relevant_in_top_10) / 10

# Check where relevant candidates appear in the full ranking
relevant_ranks = [
    (rank, candidate)
    for rank, candidate in enumerate(ranked_candidates, start=1)
    if candidate["resume_id"] in relevant_ids
]

print("\n===== DIAGNOSTIC RESULTS =====")
print("Relevant candidates found:", len(relevant_ranks))

print("\nFirst 10 relevant candidates in the ranking:")

for rank, candidate in relevant_ranks[:10]:
    print(
        f"Rank: {rank} | "
        f"ID: {candidate['resume_id']} | "
        f"Score: {candidate['score']}% | "
        f"Skills: {candidate['skill_score']}% | "
        f"Role: {candidate['role_score']}% | "
        f"Seniority: {candidate['seniority_score']}"
    )

recall_at_10 = (
    len(relevant_in_top_10) / len(relevant_ids)
    if relevant_ids
    else 0
)

# 8. Display results
print("\n===== RANKING EVALUATION =====")
print("Job ID:", job_id)
print("Job title:", job["job_title"])
print("Known relevant resumes:", len(relevant_ids))
print("Candidates ranked:", len(ranked_candidates))
print("Relevant candidates in top 10:", len(relevant_in_top_10))

print("\nTop 10 resume IDs:")
top_10 = ranked_candidates[:10]

for rank, candidate in enumerate(top_10, start=1):
    relevant = candidate["resume_id"] in relevant_ids

    print(
        f"{rank}. {candidate['resume_id']} | "
        f"Score: {candidate['score']}% | "
        f"Relevant: {relevant}"
    )

print("\nPrecision@10:", round(precision_at_10 * 100, 2), "%")
print("Recall@10:", round(recall_at_10 * 100, 2), "%")


print("\n===== CANDIDATE COMPARISON =====")
print("Job industry:", job["industry"])
print("Job seniority:", job["seniority"])

# Inspect the current top 10
print("\n--- Current Top 10 ---")

for candidate in ranked_candidates[:10]:
    row = resumes.loc[
        resumes["resume_id"] == candidate["resume_id"]
    ].iloc[0]

    print(
        f"ID: {row['resume_id']} | "
        f"Role: {row['role']} | "
        f"Seniority: {row['seniority']} | "
        f"Industry: {row['industry']} | "
        f"Experience: {row['years_experience']} years | "
        f"Relevant: {row['resume_id'] in relevant_ids}"
    )

# Inspect relevant candidates with perfect scores
print("\n--- Relevant Candidates Scoring 100% ---")

count = 0

for rank, candidate in relevant_ranks:
    if candidate["score"] == 100.0:
        row = resumes.loc[
            resumes["resume_id"] == candidate["resume_id"]
        ].iloc[0]

        print(
            f"Rank: {rank} | "
            f"ID: {row['resume_id']} | "
            f"Role: {row['role']} | "
            f"Seniority: {row['seniority']} | "
            f"Industry: {row['industry']} | "
            f"Experience: {row['years_experience']} years"
        )

        count += 1

        if count == 5:
            break


print("\n===== GROUND-TRUTH CHECK =====")

# Inspect the 30 candidates marked relevant by the dataset.
relevant_resume_rows = resumes[
    resumes["resume_id"].isin(relevant_ids)
]

print("Relevant IDs in matches.csv:", len(relevant_ids))
print("Relevant IDs found in resumes.csv:", len(relevant_resume_rows))

print("\nFirst 10 relevant candidates and their attributes:")

for _, row in relevant_resume_rows.head(10).iterrows():
    print(
        f"ID: {row['resume_id']} | "
        f"Role: {row['role']} | "
        f"Seniority: {row['seniority']} | "
        f"Industry: {row['industry']} | "
        f"Experience: {row['years_experience']} years"
    )


print("\n===== SKILL RELEVANCE CHECK =====")

print("\nJob required skills:")
print(job["must_have_skills"])

print("\nJob nice-to-have skills:")
print(job["nice_to_have_skills"])

print("\nFirst 10 relevant candidates: skill comparison")

for rank, candidate in relevant_ranks[:10]:
    print(f"\nRank: {rank} | ID: {candidate['resume_id']}")
    print("Overall score:", candidate["score"])
    print("Matched required skills:", candidate["matched_skills"])
    print("Missing required skills:", candidate["missing_skills"])
