import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Llama 3.1 8B is the fastest free model on Groq — good enough for narrative text.
# Switch to "llama-3.1-70b-versatile" if you want richer language (slower, still free).
MODEL = "llama-3.1-8b-instant"


def _ask(prompt: str, max_tokens: int = 400) -> list[str]:
    """
    Send one prompt, get back a list of bullet-point strings.
    We always ask the model to return a numbered list so parsing is reliable
    even if it adds extra words around the JSON.
    """
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        temperature=0.7,          # some variation so reports don't all sound identical
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an academic performance analyst writing concise, specific "
                    "bullet points for a student analytics report. "
                    "Always write in third person. "
                    "Always return ONLY a numbered list (1. 2. 3.) with no preamble, "
                    "no headers, no extra text. Each point is 1-2 sentences maximum."
                )
            },
            {"role": "user", "content": prompt}
        ]
    )
    raw = response.choices[0].message.content.strip()
    # Parse "1. text\n2. text\n3. text" into a list of strings
    lines = [
        line.split(". ", 1)[1].strip()
        for line in raw.splitlines()
        if line.strip() and line.strip()[0].isdigit() and ". " in line
    ]
    return lines if lines else [raw]  # fallback: return raw if parsing fails


def generate_zone1_narrative(overview: dict) -> list[str]:
    score = overview["composite_score"]
    band = overview["band_label"]
    attempt_rate = overview["attempt_rate"]
    avg = overview["avg_score_pct"]
    class_avg = overview["class_avg"]
    topper = overview["branch_topper"]
    name = overview["student_name"].split()[0]
    above_below = "above" if avg > class_avg else "below"

    return _ask(f"""
Write exactly 3 bullet points for Zone 1 — Overall Performance Score.

Student: {name}
Composite score: {score:.0f}/100 (band: {band})
Tests taken: {overview['tests_taken']} at {attempt_rate}% attempt rate
Average score: {avg}% — {above_below} class average of {class_avg:.0f}%
Best score: {overview['best_score_pct']}%
Branch topper score: {topper:.0f}

Bullet 1: State the composite score, attempt rate, and how avg compares to class avg.
Bullet 2: Interpret what the performance band means and identify the key strength or weakness.
Bullet 3: Give one specific, actionable recommendation tied to the actual numbers above.
""")


def generate_zone2_narrative(rank: dict) -> list[str]:
    return _ask(f"""
Write exactly 3 bullet points for Zone 2 — Rank and Percentile.

Class rank: {rank['class_rank']} (top {100 - rank['class_percentile']:.0f}%)
Branch rank: {rank['branch_rank']} (top {100 - rank['branch_percentile']:.0f}%)
Platform rank: {rank['platform_rank']} (top {100 - rank['platform_percentile']:.0f}%)

Bullet 1: Describe class and branch standing — is this strong, mid-range, or needs work?
Bullet 2: Comment on platform rank and what it indicates about competitiveness beyond class.
Bullet 3: One specific benchmark action to improve ranking.
""")


def generate_zone3_narrative(quadrant: dict) -> list[str]:
    fc = quadrant["fast_correct"]
    fw = quadrant["fast_wrong"]
    sc = quadrant["slow_correct"]
    sw = quadrant["slow_wrong"]
    total = fc + fw + sc + sw
    dominant = max(
        [("fast & correct (ideal)", fc), ("fast & wrong (rushing)", fw),
         ("slow & correct (careful)", sc), ("slow & wrong (struggling)", sw)],
        key=lambda x: x[1]
    )

    return _ask(f"""
Write exactly 3 bullet points for Zone 3 — Speed vs Accuracy Matrix.

Fast & Correct: {fc} (ideal)
Fast & Wrong: {fw} (rushing)
Slow & Correct: {sc} (careful)
Slow & Wrong: {sw} (struggling)
Total questions: {total}
Dominant quadrant: {dominant[0]} with {dominant[1]} questions

Bullet 1: Describe the overall speed-accuracy pattern using the actual numbers.
Bullet 2: Name the specific problem (rushing / struggling / good balance) with evidence.
Bullet 3: One concrete technique to shift more answers into the fast & correct quadrant.
""")


def generate_zone4_narrative(mastery: list[dict]) -> list[str]:
    """Returns topic-table rows (same shape as before) plus 2 summary bullets."""
    weak = sorted([t for t in mastery if t["mastery_pct"] < 40],
                  key=lambda t: t["mastery_pct"])
    strong = sorted([t for t in mastery if t["mastery_pct"] >= 70],
                    key=lambda t: t["mastery_pct"], reverse=True)

    weak_str = ", ".join(f"{t['topic']} ({t['mastery_pct']:.0f}%)" for t in weak[:3])
    strong_str = ", ".join(f"{t['topic']} ({t['mastery_pct']:.0f}%)" for t in strong[:3])

    return _ask(f"""
Write exactly 2 bullet points summarising Zone 4 — Topic Mastery.

Weakest topics (need immediate attention): {weak_str or 'none below 40%'}
Strongest topics (above 70%): {strong_str or 'none above 70%'}
Total topics assessed: {len(mastery)}

Bullet 1: Highlight the weakest topics with specific percentages and urgency.
Bullet 2: Acknowledge the strongest topic(s) and give a focused next-step recommendation.
""", max_tokens=200)


def generate_zone4_table(mastery: list[dict]) -> list[dict]:
    """
    Per-topic rows with AI-generated status and focus text.
    Falls back to rule-based if Groq fails — important for reliability.
    """
    rows = []
    for t in mastery:
        pct = t["mastery_pct"]
        topic = t["topic"]
        try:
            result = _ask(f"""
One topic entry for a mastery table. Topic: {topic}, Mastery: {pct:.0f}%.

Write exactly 2 lines:
1. Current Status: one sentence describing what {pct:.0f}% mastery means for {topic}.
2. Improvement Focus: one specific action to improve {topic} mastery.
""", max_tokens=120)
            status = result[0] if len(result) > 0 else f"{pct:.0f}% mastery — developing."
            focus = result[1] if len(result) > 1 else "Practise with targeted exercises."
        except Exception:
            # rule-based fallback
            if pct < 35:
                status = f"Needs immediate attention with {pct:.0f}% mastery. Core concepts not yet understood."
                focus = "Revise fundamentals and solve beginner-level practice questions."
            elif pct < 60:
                status = f"Developing knowledge at {pct:.0f}% mastery, approaching proficiency."
                focus = "Strengthen concepts through revision and targeted MCQs."
            else:
                status = f"Strong performance at {pct:.0f}% mastery with solid understanding."
                focus = "Maintain momentum through regular practice and mock tests."
        rows.append({"topic": topic, "mastery_pct": pct, "status": status, "focus": focus})
    return rows


def generate_zone5_narrative(radar: list[dict]) -> list[dict]:
    """Per-subject bullets for the peer comparison zone."""
    rows = []
    for r in radar:
        subject = r["subject"]
        you = r["you"]
        avg = r["class_avg"]
        topper = r["topper"]
        gap_to_avg = avg - you
        gap_to_topper = topper - you

        try:
            result = _ask(f"""
Two bullet points for subject {subject} in a peer comparison section.

Student score: {you:.0f}
Class average: {avg:.0f} (gap: {gap_to_avg:.0f} points {'below' if gap_to_avg > 0 else 'above'} average)
Branch topper: {topper:.0f} (gap to topper: {gap_to_topper:.0f} points)

Bullet 1: Describe standing vs class average specifically.
Bullet 2: One targeted action to close the gap to the class average or topper.
""", max_tokens=120)
            status = result[0] if result else f"Scoring {you:.0f}, gap of {gap_to_avg:.0f} to class avg."
            focus = result[1] if len(result) > 1 else "Focus on closing the gap through targeted revision."
        except Exception:
            status = f"{'Above' if you >= avg else 'Below'} class average by {abs(gap_to_avg):.0f} points."
            focus = "Focus on foundational concepts and gradual progression."

        rows.append({"subject": subject, "status": status, "focus": focus})
    return rows


def generate_zone5_summary(radar: list[dict]) -> list[str]:
    above = [r["subject"] for r in radar if r["you"] >= r["class_avg"]]
    below = [r["subject"] for r in radar if r["you"] < r["class_avg"]]
    best = max(radar, key=lambda r: r["you"])
    worst = min(radar, key=lambda r: r["you"])

    return _ask(f"""
Write exactly 3 bullet points summarising Zone 5 — Peer Comparison across all subjects.

Subjects above class average: {above or 'none'}
Subjects below class average: {below or 'none'}
Best performing: {best['subject']} ({best['you']:.0f} vs topper {best['topper']:.0f})
Weakest: {worst['subject']} ({worst['you']:.0f} vs class avg {worst['class_avg']:.0f})

Bullet 1: Overall peer comparison standing across all subjects.
Bullet 2: Highlight the strongest subject relative to peers.
Bullet 3: Identify the highest-priority subject to close the gap and why.
""")


def generate_adaptive_recommendations(
    mastery: list[dict],
    quadrant: dict,
    overview: dict
) -> list[dict]:
    """
    Zone 7 — fully AI-generated recommendation cards.
    This is where Groq makes the biggest difference over rule-based:
    each recommendation is specific to this student's actual pattern,
    not a template filled with numbers.
    """
    name = overview["student_name"].split()[0]
    weak_topics = sorted(
        [t for t in mastery if t["mastery_pct"] < 60],
        key=lambda t: t["mastery_pct"]
    )[:4]  # top 4 weakest
    strong_topics = [t for t in mastery if t["mastery_pct"] >= 70]
    rushing = quadrant["fast_wrong"] > quadrant["fast_correct"] * 0.2

    prompt = f"""
Generate recommendation cards for a student analytics report for {name}.

Student profile:
- Composite score: {overview['composite_score']:.0f}/100 ({overview['band_label']})
- Weakest topics: {[(t['topic'], round(t['mastery_pct'])) for t in weak_topics]}
- Strongest topics: {[(t['topic'], round(t['mastery_pct'])) for t in strong_topics]}
- Rushing pattern: {'YES — ' + str(quadrant['fast_wrong']) + ' fast+wrong answers' if rushing else 'No'}
- Negative marks lost: {overview['neg_marks_lost']:.0f} points
- Streak: {overview['streak_count']} consecutive tests

Generate exactly {len(weak_topics) + (2 if rushing else 1)} recommendations.
Format each as:

CATEGORY: [CRITICAL or IMPROVE or REINFORCE]
TITLE: [short action title, 4-6 words]
DESCRIPTION: [one strictly short sentence combining evidence and action, under 12 words]

CRITICAL = mastery below 35% or severe rushing
IMPROVE = mastery 35-60% or moderate issue
REINFORCE = a strength to maintain
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=600,
            temperature=0.6,
            messages=[
                {
                    "role": "system",
                    "content": "You are an academic coach. Return ONLY the formatted recommendation cards, no extra text."
                },
                {"role": "user", "content": prompt}
            ]
        )
        raw = response.choices[0].message.content.strip()

        # Parse the structured output
        recs = []
        # Split by CATEGORY instead of --- because LLMs often omit the divider
        blocks = raw.split("CATEGORY:")
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            
            # Reconstruct the line for the parser
            block = "CATEGORY: " + block
            
            lines = {}
            for line in block.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    lines[key.strip().upper()] = val.strip()
            
            if "CATEGORY" in lines and "TITLE" in lines:
                cat_val = lines.get("CATEGORY", "IMPROVE").upper()
                recs.append({
                    "category": cat_val,
                    "topic": lines.get("TITLE", "Recommendation"),
                    "evidence_text": lines.get("DESCRIPTION", lines.get("EVIDENCE", "")),
                    "action_text": lines.get("ACTION", ""),
                    "priority": 1 if "CRITICAL" in cat_val else 2 if "IMPROVE" in cat_val else 3,
                })
        recs.sort(key=lambda r: r["priority"])
        return recs if recs else _fallback_recommendations(mastery, quadrant, overview)

    except Exception:
        return _fallback_recommendations(mastery, quadrant, overview)


def _fallback_recommendations(mastery, quadrant, overview):
    """Rule-based fallback if Groq fails — ensures report always generates."""
    recs = []
    for t in sorted(mastery, key=lambda x: x["mastery_pct"])[:3]:
        pct = t["mastery_pct"]
        cat = "CRITICAL" if pct < 35 else "IMPROVE"
        recs.append({
            "category": cat,
            "topic": t["topic"],
            "evidence_text": f"{t['topic']} at {pct:.1f}% needs attention; revise fundamentals.",
            "action_text": "",
            "priority": 1 if cat == "CRITICAL" else 2,
        })
    if quadrant["fast_wrong"] > quadrant["fast_correct"] * 0.2:
        recs.append({
            "category": "CRITICAL",
            "topic": "Speed & Accuracy",
            "evidence_text": f"{quadrant['fast_wrong']} fast & wrong answers; avoid guessing under time pressure.",
            "action_text": "",
            "priority": 1,
        })
    recs.sort(key=lambda r: r["priority"])
    return recs


def generate_zone8_narrative(overview: dict) -> list[str]:
    return _ask(f"""
Write exactly 3 bullet points for Zone 8 — Score Trend and Consistency.

Consistency score: {overview['consistency_score']:.0f}/100
Test streak: {overview['streak_count']} consecutive tests
Negative marks lost: {overview['neg_marks_lost']:.0f} points
Average time per question: {overview['avg_time_per_question']:.0f} seconds

Bullet 1: Describe consistency and streak with the specific numbers.
Bullet 2: Explain what the consistency score and negative marks pattern means for learning.
Bullet 3: One concrete recommendation to improve consistency and reduce negative marking.
""")


def generate_summary_narrative(overview: dict, rank: dict, radar: list[dict]) -> list[str]:
    best_subject = max(radar, key=lambda r: r["you"])["subject"] if radar else "N/A"
    worst_subject = min(radar, key=lambda r: r["you"])["subject"] if radar else "N/A"

    return _ask(f"""
Write exactly 1 paragraph (2-3 sentences) as the executive summary for a student 
analytics report. This appears on the summary page.

Student: {overview['student_name']}
Composite: {overview['composite_score']:.0f}/100 ({overview['band_label']})
Class rank: {rank['class_rank']} (top {100 - rank['class_percentile']:.0f}% of class)
Best subject: {best_subject}
Weakest subject: {worst_subject}
Negative marks lost: {overview['neg_marks_lost']:.0f}

Be specific, encouraging but honest, professional academic tone, third person.
Return ONLY the paragraph text, no numbering.
""", max_tokens=150)