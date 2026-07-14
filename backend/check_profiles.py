import numpy as np
from sqlalchemy import select
from app.db import engine, metadata
from app.generator.ability_model import generate_ability_profiles

profiles_t = metadata.tables["profiles"]

with engine.connect() as conn:
    students = conn.execute(
        select(profiles_t).where(profiles_t.c.role == "student")
    ).mappings().all()

profiles = generate_ability_profiles(students)

sample = students[0]
sample_profile = profiles[sample["id"]]

print(f"Sample student: {sample['full_name']} ({sample['branch']}-{sample['section']})")
print(f"Speed tendency: {sample_profile['speed_tendency']:.2f}  (-1 = rusher, +1 = careful)")
print(f"Consistency:    {sample_profile['consistency']:.2f}  (0 = volatile, 1 = stable)")
print("Topic abilities:")
for topic, ability in sorted(sample_profile["topic_ability"].items(), key=lambda x: -x[1]):
    trend = sample_profile["topic_trend"][topic]
    direction = "up" if trend > 0.005 else "down" if trend < -0.005 else "flat"
    print(f"  {topic:25s} {ability:.2f}  trend: {direction}")

all_abilities = [a for p in profiles.values() for a in p["topic_ability"].values()]
print(f"\nAcross all {len(students)} students, all topics:")
print(f"  mean ability: {np.mean(all_abilities):.2f}")
print(f"  min: {np.min(all_abilities):.2f}  max: {np.max(all_abilities):.2f}")