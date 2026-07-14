def generate_zone1_narrative(overview):
    score = overview["composite_score"]
    band = overview["band_label"]
    attempt_rate = overview["attempt_rate"]
    avg_score = overview["avg_score_pct"]
    class_avg = overview["class_avg"]
    above = "above" if avg_score > class_avg else "below"

    return [
        f"{overview['student_name'].split()[0]} has achieved a composite score of "
        f"{score:.0f}/100 with a {attempt_rate}% attempt rate and an average score "
        f"{above} the class average, demonstrating {'strong' if above == 'above' else 'moderate'} "
        f"engagement and potential.",
        f"Performance level is {band}. "
        + (
            "Strong results in key areas show a solid foundation that can be built upon."
            if score >= 60 else
            "Inconsistent performance across subjects is limiting overall score growth."
        ),
        "To improve further, focus on targeted revision and strengthening weaker topics "
        "between tests, helping convert effort into consistently higher scores."
    ]


def generate_zone2_narrative(rank):
    cp = rank["class_percentile"]
    bp = rank["branch_percentile"]
    return [
        f"Ranked {'among the top performers' if cp >= 80 else 'in the top ' + str(int(100-cp)) + '%'} "
        f"in class and showing {'steady' if cp >= 70 else 'developing'} improvement in both "
        f"class and branch rankings.",
        f"Branch percentile stands at {bp:.0f}% — "
        + ("strong performance with room to push further." if bp >= 70 else
           "indicating potential to move into the top-performing range."),
        "To improve further, benchmark against top-performing students and focus on "
        "closing the gap in high-impact topics."
    ]


def generate_zone3_narrative(quadrant):
    fc = quadrant["fast_correct"]
    fw = quadrant["fast_wrong"]
    sc = quadrant["slow_correct"]
    sw = quadrant["slow_wrong"]
    total = fc + fw + sc + sw
    rush_pct = round(100 * fw / total) if total else 0

    rushing = fw > fc * 0.2
    struggling = sw > sc * 0.3

    lines = [
        f"Answers {fc} questions fast & correctly (ideal) and {sc} slowly & correctly (careful). "
        f"{'A rushing pattern is evident with ' + str(fw) + ' fast & wrong answers.' if rushing else 'Speed-accuracy balance is healthy.'}",
    ]
    if rushing:
        lines.append(
            f"{rush_pct}% of fast answers are wrong — certain topics are answered too "
            "quickly, leading to avoidable mistakes."
        )
    if struggling:
        lines.append(
            f"{sw} slow & wrong answers suggest conceptual gaps in some topics requiring "
            "targeted revision."
        )
    lines.append(
        "Focus on improving accuracy in rushed attempts and strengthening understanding "
        "of challenging concepts through targeted practice."
    )
    return lines


def generate_zone4_narrative(mastery_rows):
    weak = [t for t in mastery_rows if t["mastery_pct"] < 40]
    strong = [t for t in mastery_rows if t["mastery_pct"] >= 70]
    rows = []
    for t in mastery_rows:
        pct = t["mastery_pct"]
        if pct < 35:
            status = f"Needs immediate attention with a mastery score of {pct:.0f}%. Core concepts are not yet fully understood."
            focus = "Revise fundamentals and solve beginner-level practice questions regularly."
        elif pct < 55:
            status = f"Developing knowledge at {pct:.0f}% mastery — close to achieving proficiency."
            focus = "Strengthen concepts through revision and targeted MCQs."
        elif pct < 70:
            status = f"Moderate understanding at {pct:.0f}% mastery with room for improvement."
            focus = "Practice under timed conditions to improve speed and accuracy."
        else:
            status = f"Strong performance with {pct:.0f}% mastery and good problem-solving ability."
            focus = "Maintain momentum through regular practice and mock tests."
        rows.append({"topic": t["topic"], "mastery_pct": pct, "status": status, "focus": focus})
    return rows


def generate_zone5_narrative(radar_rows):
    rows = []
    for r in radar_rows:
        you = r["you"]
        avg = r["class_avg"]
        topper = r["topper"]
        if you >= topper * 0.9:
            status = f"Performing close to the Branch Topper and well above the Class Average."
            focus = "Maintain strong performance through regular mock tests and advanced problem-solving."
        elif you >= avg:
            status = f"Performing around or above the Class Average with a stable understanding."
            focus = "Improve accuracy and speed through topic-wise practice and revision."
        else:
            status = f"Currently below the Class Average, indicating gaps in conceptual understanding."
            focus = "Focus on foundational concepts and gradual progression to advanced topics."
        rows.append({"subject": r["subject"], "status": status, "focus": focus})
    return rows


def generate_zone8_narrative(overview):
    streak = overview["streak_count"]
    neg = overview["neg_marks_lost"]
    avg_time = overview["avg_time_per_question"]
    consistency = overview["consistency_score"]

    return [
        f"Maintains a {streak}-test streak and solves questions in {avg_time:.0f}s on average, "
        f"but has lost {neg:.0f} marks due to negative marking.",
        f"Consistency score of {consistency:.0f}/100 — "
        + ("scores are relatively stable." if consistency >= 70 else
           "score fluctuations are limiting overall performance growth."),
        "Focus on balancing speed with accuracy — take more time on challenging questions "
        "and avoid guessing when unsure, to reduce negative marks and improve consistency."
    ]