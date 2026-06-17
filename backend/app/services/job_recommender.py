"""
job_recommender.py
==================
Agent 1 — Job Recommender

Intelligence layers:
  1. Extract skills + experience level from CV (reuses nlp_service logic)
  2. Score CV against every job profile using weighted matching
  3. Rank and categorise into Best Match / Good Match / Stretch Goal
  4. For each job: explain WHY it matched and WHAT to learn to improve
"""

from app.services.job_profiles import JOB_PROFILES
from app.services.nlp_service  import (
    extract_skills,
    detect_experience_level,
    extract_sections,
    SKILL_ONTOLOGY,
    CAREER_GUIDANCE,
    DEFAULT_GUIDANCE,
)


# ── Scoring weights ────────────────────────────────────────────────────────

CORE_WEIGHT  = 3.0   # must-have skills
GOOD_WEIGHT  = 1.5   # important but not critical
BONUS_weight = 0.5   # nice to have


def score_job(cv_skills: set, job: dict) -> tuple:
    """
    Returns (score_0_to_100, matched_skills, missing_core, missing_good)
    """
    core   = set(job["core_skills"])
    good   = set(job["good_skills"])
    bonus  = set(job.get("bonus_skills", []))

    all_required = core | good | bonus

    matched_core  = cv_skills & core
    matched_good  = cv_skills & good
    matched_bonus = cv_skills & bonus
    matched_all   = cv_skills & all_required

    missing_core = core  - cv_skills
    missing_good = good  - cv_skills

    # Weighted score
    max_score = (
        len(core)  * CORE_WEIGHT  +
        len(good)  * GOOD_WEIGHT  +
        len(bonus) * BONUS_weight
    )

    if max_score == 0:
        return 0, [], list(missing_core), list(missing_good)

    earned = (
        len(matched_core)  * CORE_WEIGHT  +
        len(matched_good)  * GOOD_WEIGHT  +
        len(matched_bonus) * BONUS_weight
    )

    raw_score = (earned / max_score) * 100

    # Penalty: if missing ALL core skills → cap at 35%
    if len(matched_core) == 0:
        raw_score = min(raw_score, 35)
    # Bonus: if ALL core skills present → small boost
    elif len(matched_core) == len(core):
        raw_score = min(raw_score * 1.08, 100)

    return (
        round(raw_score),
        sorted(matched_all),
        sorted(missing_core),
        sorted(missing_good),
    )


def get_match_label(score: int) -> str:
    if score >= 75: return "Best Match"
    if score >= 50: return "Good Match"
    if score >= 30: return "Stretch Goal"
    return "Not Recommended"


def get_match_color(score: int) -> str:
    if score >= 75: return "#10B981"
    if score >= 50: return "#3B82F6"
    if score >= 30: return "#F59E0B"
    return "#EF4444"


def career_tip(missing_core: list, missing_good: list, job_title: str) -> str:
    """Generate a specific learning tip for this job based on missing skills."""
    all_missing = missing_core + missing_good
    if not all_missing:
        return f"You are well-qualified for {job_title}. Polish your GitHub and apply now."

    # Pick the most impactful missing skill
    top = missing_core[0] if missing_core else missing_good[0]
    guidance = CAREER_GUIDANCE.get(top, DEFAULT_GUIDANCE)
    course   = guidance["courses"][0]
    timeline = guidance["timeline"]

    if missing_core:
        return (
            f"Focus on {top} first — it's a core requirement. "
            f"Recommended: {course}. Timeline: {timeline}."
        )
    return (
        f"You have the core skills. Add {top} to strengthen your profile. "
        f"Recommended: {course}. Timeline: {timeline}."
    )


def recommend_jobs(cv_text: str) -> dict:
    """
    Main agent function.
    Returns structured recommendations grouped by match level.
    """

    # ── Step 1: Understand the CV ─────────────────────────────────────────
    cv_skills = extract_skills(cv_text)
    exp_level, exp_score, exp_explanation = detect_experience_level(cv_text)
    sections  = extract_sections(cv_text)

    # ── Step 2: Score every job profile ──────────────────────────────────
    scored = []
    for job in JOB_PROFILES:
        score, matched, miss_core, miss_good = score_job(cv_skills, job)
        if score < 20:
            continue   # skip irrelevant jobs entirely

        tip = career_tip(miss_core, miss_good, job["title"])

        scored.append({
            "title":         job["title"],
            "category":      job["category"],
            "emoji":         job["emoji"],
            "description":   job["description"],
            "score":         score,
            "matchLabel":    get_match_label(score),
            "matchColor":    get_match_color(score),
            "matchedSkills": matched[:8],
            "missingCore":   miss_core[:4],
            "missingGood":   miss_good[:4],
            "salaryPKR":     job["salary_pkr"],
            "salaryUSD":     job["salary_usd"],
            "demand":        job["demand"],
            "tip":           tip,
        })

    # ── Step 3: Sort and group ────────────────────────────────────────────
    scored.sort(key=lambda x: -x["score"])

    best    = [j for j in scored if j["score"] >= 75][:5]
    good    = [j for j in scored if 50 <= j["score"] < 75][:5]
    stretch = [j for j in scored if 30 <= j["score"] < 50][:4]

    # ── Step 4: Profile summary ───────────────────────────────────────────
    top_categories = {}
    for j in best + good:
        cat = j["category"]
        top_categories[cat] = top_categories.get(cat, 0) + 1
    primary_field = max(top_categories, key=top_categories.get) if top_categories else "General"

    return {
        "cvSkills":       sorted(cv_skills),
        "experienceLevel": exp_level,
        "primaryField":   primary_field,
        "totalMatched":   len(scored),
        "best":           best,
        "good":           good,
        "stretch":        stretch,
        "summary": (
            f"Based on your CV, you are a strong fit for {primary_field} roles "
            f"at {exp_level} level with {len(cv_skills)} detected skills. "
            f"Found {len(best)} best matches, {len(good)} good matches, "
            f"and {len(stretch)} stretch opportunities."
        ),
    }
