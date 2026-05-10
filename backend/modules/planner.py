"""
planner.py
Generates structured multi-day study plans.
Pure Python logic — no LLM involved.
"""



import math

from typing import Optional



                                                                                

                                                                    



SUBJECT_TOPICS = {

    "python": [

        "Variables & Data Types", "Control Flow (if/else/loops)",

        "Functions & Scope", "Lists, Tuples & Dictionaries",

        "File I/O", "Object-Oriented Programming",

        "Error Handling", "Modules & Packages",

        "List Comprehensions", "Practice Problems & Review"

    ],

    "data structures": [

        "Arrays & Linked Lists", "Stacks & Queues",

        "Trees (Binary, BST)", "Heaps & Priority Queues",

        "Hash Tables", "Graphs (BFS/DFS)",

        "Sorting Algorithms", "Searching Algorithms",

        "Dynamic Programming Basics", "Practice Problems & Review"

    ],

    "database": [

        "Relational Model & Keys", "SQL Basics (SELECT, INSERT)",

        "Joins & Subqueries", "Normalization (1NF, 2NF, 3NF)",

        "Transactions & ACID", "Indexing & Query Optimization",

        "NoSQL Concepts", "ER Diagrams", "Practice Queries & Review"

    ],

    "machine learning": [

        "Math Foundations (Linear Algebra, Probability)",

        "Data Preprocessing", "Regression (Linear, Logistic)",

        "Decision Trees & Random Forests", "SVM & KNN",

        "Neural Networks Basics", "Model Evaluation & Metrics",

        "Overfitting & Regularization", "Clustering (K-Means)",

        "Practice Projects & Review"

    ],

    "os": [

        "Processes & Threads", "CPU Scheduling Algorithms",

        "Memory Management", "Virtual Memory & Paging",

        "File Systems", "Deadlocks", "Synchronization",

        "I/O Management", "Security Basics", "Review & Mock Questions"

    ],

    "networking": [

        "OSI & TCP/IP Models", "IP Addressing & Subnetting",

        "DNS & DHCP", "TCP vs UDP", "HTTP/HTTPS & Web",

        "Routing Protocols", "Network Security Basics",

        "Firewalls & VPN", "Wireless Networks", "Review"

    ],

    "mathematics": [

        "Sets & Logic", "Functions & Relations",

        "Probability & Statistics", "Linear Algebra Basics",

        "Calculus Fundamentals", "Discrete Mathematics",

        "Number Theory", "Graph Theory", "Practice Problems", "Review"

    ],

    "default": [

        "Introduction & Core Concepts", "Fundamentals Part 1",

        "Fundamentals Part 2", "Intermediate Concepts",

        "Key Theories & Models", "Applications & Examples",

        "Problem Solving Practice", "Advanced Topics",

        "Common Exam Questions", "Full Revision & Review"

    ]

}





def _get_topics(subject: str, custom_topics: Optional[list] = None) -> list:

    """Return topic list: custom if provided, else subject bank, else default."""

    if custom_topics:

        return custom_topics



    subject_key = subject.lower().strip()

    for key in SUBJECT_TOPICS:

        if key in subject_key or subject_key in key:

            return SUBJECT_TOPICS[key]



    return SUBJECT_TOPICS["default"]





def generate_plan(

    subject: str,

    days: int,

    hours_per_day: float,

    goal: str = "Exam Preparation",

    custom_topics: Optional[list] = None

) -> dict:

    """
    Generate a structured multi-day study plan.

    Args:
        subject:       Subject name (e.g., "Python", "Database")
        days:          Number of days available
        hours_per_day: Study hours available per day
        goal:          What the user is preparing for
        custom_topics: Optional list of specific topics to cover

    Returns:
        dict with plan metadata and daily schedule
    """

                     

    days = max(1, min(days, 30))

    hours_per_day = max(0.5, min(hours_per_day, 12))



    topics = _get_topics(subject, custom_topics)

    total_hours = days * hours_per_day

    total_topics = len(topics)



                                   

                                                    

    revision_days = max(1, math.ceil(days * 0.2))

    study_days = days - revision_days



    if study_days < 1:

        study_days = days

        revision_days = 0



                          

    topics_per_day = math.ceil(total_topics / max(study_days, 1))

    hours_per_topic = round(hours_per_day / max(topics_per_day, 1), 1)



    schedule = []

    topic_index = 0



    for day_num in range(1, days + 1):

        is_revision_day = day_num > study_days



        if is_revision_day:

                                    

            day_topics = []

            covered = topics[:topic_index] if topic_index > 0 else topics

                                          

            half = len(covered) // 2

            if day_num == study_days + 1:

                revision_topics = covered[:half] if half else covered

            else:

                revision_topics = covered[half:] if half else covered



            sessions = [{

                "topic": t,

                "duration_hours": round(hours_per_day / max(len(revision_topics), 1), 1),

                "type": "revision",

                "status": "pending"

            } for t in revision_topics] if revision_topics else [{

                "topic": "Full Subject Revision",

                "duration_hours": hours_per_day,

                "type": "revision",

                "status": "pending"

            }]



            schedule.append({

                "day": day_num,

                "label": f"Day {day_num} — Revision",

                "focus": "Revision & Practice",

                "total_hours": hours_per_day,

                "sessions": sessions,

                "tip": _get_revision_tip(day_num, days)

            })



        else:

                               

            day_topic_list = topics[topic_index: topic_index + topics_per_day]

            topic_index += topics_per_day



            if not day_topic_list:

                day_topic_list = ["Practice Problems & Review"]



            sessions = [{

                "topic": t,

                "duration_hours": hours_per_topic,

                "type": "study",

                "status": "pending"

            } for t in day_topic_list]



            schedule.append({

                "day": day_num,

                "label": f"Day {day_num} — {day_topic_list[0]}" if len(day_topic_list) == 1 else f"Day {day_num} — {len(day_topic_list)} Topics",

                "focus": day_topic_list[0] if day_topic_list else "Study",

                "total_hours": hours_per_day,

                "sessions": sessions,

                "tip": _get_study_tip(day_num, days, hours_per_day)

            })



    return {

        "subject": subject,

        "goal": goal,

        "days": days,

        "hours_per_day": hours_per_day,

        "total_hours": round(total_hours, 1),

        "total_topics": total_topics,

        "revision_days": revision_days,

        "schedule": schedule,

        "summary": f"Study {subject} for {days} days ({hours_per_day}h/day) covering {total_topics} topics with {revision_days} revision day(s)."

    }





def _get_study_tip(day: int, total_days: int, hours: float) -> str:

    """Return a contextual tip for the study day."""

    if hours > 6:

        return "Long session today — take a 10-min break every 45 minutes (Pomodoro technique)."

    if day == 1:

        return "Start with the big picture before diving into details. Build a mental map."

    if day <= total_days // 3:

        return "Focus on understanding concepts, not memorizing. Write notes in your own words."

    if day <= (total_days * 2) // 3:

        return "Try solving practice problems after each topic — active recall beats re-reading."

    return "You're in the final stretch. Prioritize weak areas identified earlier."





def _get_revision_tip(day: int, total_days: int) -> str:

    """Return a tip for revision days."""

    tips = [

        "Use spaced repetition: review what you found hardest first.",

        "Try teaching the topic out loud — if you can explain it, you understand it.",

        "Focus on past exam questions and identify patterns.",

        "Create a one-page summary cheat sheet for each topic.",

        "Rest well tonight — sleep consolidates memory."

    ]

    return tips[(day - 1) % len(tips)]

