import numpy as np
from collections import Counter
from sqlalchemy import select
from app.db import engine, metadata
from app.metrics.composite_score import compute_composite_score, band_label_for

enrollments_t = metadata.tables["enrollments"]

with engine.connect() as conn:
    enrollments = conn.execute(select(enrollments_t)).mappings().all()

    print(f"Computing composite score for all {len(enrollments)} student-course pairs...")
    print("(this makes a few DB round-trips per pair, so it'll take a minute or two)")

    scores = []
    for e in enrollments:
        result = compute_composite_score(conn, e["student_id"], e["course_id"])
        if result:
            scores.append(result["composite_score"])

scores = np.array(scores)
print(f"\nComputed for {len(scores)} of {len(enrollments)} enrollments (some may have had no attempts)")
print(f"Mean: {scores.mean():.1f}   Min: {scores.min():.1f}   Max: {scores.max():.1f}   Std: {scores.std():.1f}")

bands = Counter(band_label_for(s) for s in scores)
print("\nBand distribution:")
for label in ["Needs Improvement", "Developing", "Proficient", "Strong", "Excellent"]:
    print(f"  {label:20s} {bands.get(label, 0)}")