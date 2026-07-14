import random
import numpy as np
from app import config

TOPIC_NOISE_STD = 0.15  # how much ability varies topic-to-topic around a student's overall aptitude


def generate_ability_profiles(students):
    all_topics = set()
    for course in config.COURSES:
        all_topics.update(course["topics"])

    profiles = {}
    for student in students:
        general_ability = float(np.random.beta(a=3, b=2))  # this student's overall aptitude

        topic_ability = {}
        topic_trend = {}

        for topic in all_topics:
            noise = np.random.normal(0, TOPIC_NOISE_STD)
            topic_ability[topic] = float(np.clip(general_ability + noise, 0.0, 1.0))

            roll = random.random()
            if roll < 0.25:
                slope = np.random.uniform(0.01, 0.03)
            elif roll < 0.45:
                slope = np.random.uniform(-0.03, -0.01)
            else:
                slope = np.random.uniform(-0.005, 0.005)
            topic_trend[topic] = float(slope)

        profiles[student["id"]] = {
            "general_ability": general_ability,
            "topic_ability": topic_ability,
            "topic_trend": topic_trend,
            "speed_tendency": float(np.random.uniform(-1, 1)),
            "consistency": float(np.random.beta(a=3, b=2)),
        }

    return profiles