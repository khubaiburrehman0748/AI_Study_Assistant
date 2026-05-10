"""
forgetting_curve.py
Ebbinghaus Forgetting Curve for smart revision suggestions.

The forgetting curve formula:
    R(t) = e^(-t / S)

Where:
    R = retention (0 to 1, i.e. 0% to 100% remembered)
    t = time elapsed since last study (in hours)
    S = stability factor (how well the topic was learned)

A topic with R < 0.6 (60% retention) should be revised soon.
"""



import math

import json

import os

from datetime import datetime, timezone

from typing import Optional



                                                                                

DEFAULT_STABILITY   = 24.0                                      

RETENTION_THRESHOLD = 0.60                                

DIFFICULTY_STABILITY = {

    1: 36.0,                                  

    2: 28.0,

    3: 20.0,

    4: 14.0,

    5: 10.0,                                 

}



DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "data")

TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")





                                                                                



def retention(hours_elapsed: float, stability: float) -> float:

    """
    R(t) = e^(-t / S)
    Returns a value in [0, 1].
    """

    if hours_elapsed <= 0:

        return 1.0

    return math.exp(-hours_elapsed / stability)





def hours_since(iso_timestamp: str) -> float:

    """Calculate hours elapsed since an ISO timestamp string."""

    if not iso_timestamp:

        return float("inf")

    try:

        dt = datetime.fromisoformat(iso_timestamp)

        if dt.tzinfo is None:

            dt = dt.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)

        return (now - dt).total_seconds() / 3600.0

    except (ValueError, TypeError):

        return float("inf")





def get_topic_stability(topic: str, difficulty: int = 2) -> float:

    """Return stability for a topic based on its difficulty."""

    return DIFFICULTY_STABILITY.get(difficulty, DEFAULT_STABILITY)





                                                                                

_DIFFICULTY_MAP = {

    "Variables & Data Types": 1, "Control Flow (if/else/loops)": 1,

    "SQL Basics (SELECT, INSERT)": 1, "Relational Model & Keys": 1,

    "Functions & Scope": 2, "Lists, Tuples & Dictionaries": 2,

    "File I/O": 2, "Error Handling": 2, "Modules & Packages": 2,

    "Searching Algorithms": 2, "NoSQL Concepts": 2, "ER Diagrams": 2,

    "I/O Management": 2, "Data Preprocessing": 2, "Processes & Threads": 2,

    "Object-Oriented Programming": 3, "List Comprehensions": 3,

    "Arrays & Linked Lists": 2, "Stacks & Queues": 2,

    "Trees (Binary, BST)": 3, "Heaps & Priority Queues": 3,

    "Hash Tables": 3, "Sorting Algorithms": 3,

    "Joins & Subqueries": 3, "Normalization (1NF, 2NF, 3NF)": 3,

    "Transactions & ACID": 3, "CPU Scheduling Algorithms": 3,

    "Memory Management": 3, "File Systems": 3,

    "Math Foundations (Linear Algebra, Probability)": 3,

    "Regression (Linear, Logistic)": 3,

    "Decision Trees & Random Forests": 3, "SVM & KNN": 3,

    "Overfitting & Regularization": 3, "Clustering (K-Means)": 3,

    "Model Evaluation & Metrics": 2,

    "Graphs (BFS/DFS)": 4, "Indexing & Query Optimization": 4,

    "Virtual Memory & Paging": 4, "Deadlocks": 4, "Synchronization": 4,

    "Neural Networks Basics": 4,

    "Dynamic Programming Basics": 5,

}





def _get_difficulty(topic: str) -> int:

    return _DIFFICULTY_MAP.get(topic, 2)





                                                                                



def get_retention_scores(subject: Optional[str] = None) -> list:

    """
    Calculate retention for every completed task using the Ebbinghaus formula.

    Returns a list of dicts sorted by retention ascending (most forgotten first):
    [
      {
        "task_id":        "abc123",
        "topic":          "Graphs (BFS/DFS)",
        "subject":        "Data Structures",
        "retention_pct":  42.1,
        "needs_revision": True,
        "urgency":        "high"
      },
      ...
    ]
    """

    try:

        with open(TASKS_FILE, "r") as f:

            tasks = json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):

        return []



    results = []

    for task in tasks:

        if task.get("status") != "done":

            continue

        if subject and task.get("subject", "").lower() != subject.lower():

            continue



        completed_at = task.get("completed_at")

        topic        = task.get("topic", "")

        difficulty   = _get_difficulty(topic)

        stability    = get_topic_stability(topic, difficulty)

        elapsed      = hours_since(completed_at)

        R            = retention(elapsed, stability)



        if elapsed == float("inf"):

            urgency = "high"

        elif R < 0.40:

            urgency = "high"

        elif R < RETENTION_THRESHOLD:

            urgency = "medium"

        else:

            urgency = "low"



        results.append({

            "task_id":        task["id"],

            "topic":          topic,

            "subject":        task.get("subject", ""),

            "retention":      round(R, 3),

            "retention_pct":  round(R * 100, 1),

            "hours_elapsed":  round(elapsed, 1) if elapsed != float("inf") else None,

            "difficulty":     difficulty,

            "needs_revision": R < RETENTION_THRESHOLD,

            "urgency":        urgency

        })



    results.sort(key=lambda x: x["retention"])

    return results





def get_forgetting_curve_suggestion(subject: Optional[str] = None) -> dict:

    """
    Smart suggestion using the forgetting curve.
    Returns the topic with the lowest retention that needs revision most.
    """

    scores = get_retention_scores(subject)

    urgent = [s for s in scores if s["needs_revision"]]



    if not urgent:

        return {

            "type":    "retention_ok",

            "message": "🧠 Great memory! All completed topics have retention above 60%. Keep up the regular study sessions."

        }



    most_forgotten = urgent[0]

    R_pct          = most_forgotten["retention_pct"]

    topic          = most_forgotten["topic"]

    urgency        = most_forgotten["urgency"]



    if urgency == "high":

        emoji = "🚨"

        verb  = "urgently needs"

    else:

        emoji = "⚠️"

        verb  = "should be"



    msg = (

        f"{emoji} **Forgetting Curve Alert**: *{topic}* {verb} revised — "

        f"you've retained only **{R_pct}%** of it.\n\n"

        f"📖 Review it now for 15-20 minutes to reset your memory retention back to 100%."

    )



    if len(urgent) > 1:

        others = [u["topic"] for u in urgent[1:3]]

        msg += f"\n\n📋 Also fading: {', '.join(others)}"



    return {

        "type":          "forgetting_curve",

        "topic":         topic,

        "retention_pct": R_pct,

        "urgency":       urgency,

        "all_urgent":    urgent,

        "message":       msg

    }
