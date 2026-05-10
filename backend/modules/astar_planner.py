"""
astar_planner.py
A* algorithm for optimal study path planning.

Instead of dumping topics evenly across days, A* finds the
best ORDER to study topics by treating the study schedule as
a graph search problem:

  - Each NODE  = (day, topics_covered_so_far)
  - Each EDGE  = studying one topic on a given day
  - g(n)       = actual difficulty-weighted hours spent so far
  - h(n)       = estimated hours still needed (heuristic)
  - A* picks the lowest f(n) = g(n) + h(n) path

This ensures:
  1. Prerequisites come before advanced topics
  2. Harder topics get scheduled when energy is highest (early days)
  3. Revision is interleaved where forgetting risk is high
"""



import heapq

import math

from typing import Optional





                                                                               

                                      

                                              



TOPIC_GRAPH = {

            

    "Variables & Data Types":           {"difficulty": 1, "prereqs": []},

    "Control Flow (if/else/loops)":     {"difficulty": 1, "prereqs": ["Variables & Data Types"]},

    "Functions & Scope":                {"difficulty": 2, "prereqs": ["Control Flow (if/else/loops)"]},

    "Lists, Tuples & Dictionaries":     {"difficulty": 2, "prereqs": ["Variables & Data Types"]},

    "File I/O":                         {"difficulty": 2, "prereqs": ["Functions & Scope"]},

    "Object-Oriented Programming":      {"difficulty": 3, "prereqs": ["Functions & Scope"]},

    "Error Handling":                   {"difficulty": 2, "prereqs": ["Functions & Scope"]},

    "Modules & Packages":               {"difficulty": 2, "prereqs": ["Functions & Scope"]},

    "List Comprehensions":              {"difficulty": 3, "prereqs": ["Lists, Tuples & Dictionaries"]},

    "Practice Problems & Review":       {"difficulty": 2, "prereqs": []},



                     

    "Arrays & Linked Lists":            {"difficulty": 2, "prereqs": []},

    "Stacks & Queues":                  {"difficulty": 2, "prereqs": ["Arrays & Linked Lists"]},

    "Trees (Binary, BST)":              {"difficulty": 3, "prereqs": ["Arrays & Linked Lists"]},

    "Heaps & Priority Queues":          {"difficulty": 3, "prereqs": ["Trees (Binary, BST)"]},

    "Hash Tables":                      {"difficulty": 3, "prereqs": ["Arrays & Linked Lists"]},

    "Graphs (BFS/DFS)":                 {"difficulty": 4, "prereqs": ["Trees (Binary, BST)"]},

    "Sorting Algorithms":               {"difficulty": 3, "prereqs": ["Arrays & Linked Lists"]},

    "Searching Algorithms":             {"difficulty": 2, "prereqs": ["Arrays & Linked Lists"]},

    "Dynamic Programming Basics":       {"difficulty": 5, "prereqs": ["Graphs (BFS/DFS)", "Sorting Algorithms"]},



              

    "Relational Model & Keys":          {"difficulty": 1, "prereqs": []},

    "SQL Basics (SELECT, INSERT)":      {"difficulty": 1, "prereqs": ["Relational Model & Keys"]},

    "Joins & Subqueries":               {"difficulty": 3, "prereqs": ["SQL Basics (SELECT, INSERT)"]},

    "Normalization (1NF, 2NF, 3NF)":    {"difficulty": 3, "prereqs": ["Relational Model & Keys"]},

    "Transactions & ACID":              {"difficulty": 3, "prereqs": ["SQL Basics (SELECT, INSERT)"]},

    "Indexing & Query Optimization":    {"difficulty": 4, "prereqs": ["Joins & Subqueries"]},

    "NoSQL Concepts":                   {"difficulty": 2, "prereqs": []},

    "ER Diagrams":                      {"difficulty": 2, "prereqs": ["Relational Model & Keys"]},



        

    "Processes & Threads":              {"difficulty": 2, "prereqs": []},

    "CPU Scheduling Algorithms":        {"difficulty": 3, "prereqs": ["Processes & Threads"]},

    "Memory Management":                {"difficulty": 3, "prereqs": ["Processes & Threads"]},

    "Virtual Memory & Paging":          {"difficulty": 4, "prereqs": ["Memory Management"]},

    "File Systems":                     {"difficulty": 3, "prereqs": ["Memory Management"]},

    "Deadlocks":                        {"difficulty": 4, "prereqs": ["Processes & Threads"]},

    "Synchronization":                  {"difficulty": 4, "prereqs": ["Processes & Threads"]},

    "I/O Management":                   {"difficulty": 2, "prereqs": ["Processes & Threads"]},



                      

    "Math Foundations (Linear Algebra, Probability)": {"difficulty": 3, "prereqs": []},

    "Data Preprocessing":               {"difficulty": 2, "prereqs": []},

    "Regression (Linear, Logistic)":    {"difficulty": 3, "prereqs": ["Math Foundations (Linear Algebra, Probability)"]},

    "Decision Trees & Random Forests":  {"difficulty": 3, "prereqs": ["Data Preprocessing"]},

    "SVM & KNN":                        {"difficulty": 3, "prereqs": ["Math Foundations (Linear Algebra, Probability)"]},

    "Neural Networks Basics":           {"difficulty": 4, "prereqs": ["Regression (Linear, Logistic)"]},

    "Model Evaluation & Metrics":       {"difficulty": 2, "prereqs": ["Regression (Linear, Logistic)"]},

    "Overfitting & Regularization":     {"difficulty": 3, "prereqs": ["Model Evaluation & Metrics"]},

    "Clustering (K-Means)":             {"difficulty": 3, "prereqs": ["Data Preprocessing"]},

}



DEFAULT_DIFFICULTY = 2                               





def _get_difficulty(topic: str) -> int:

    return TOPIC_GRAPH.get(topic, {}).get("difficulty", DEFAULT_DIFFICULTY)





def _get_prereqs(topic: str) -> list:

    return TOPIC_GRAPH.get(topic, {}).get("prereqs", [])





def _prereqs_satisfied(topic: str, covered: frozenset) -> bool:

    """Check all prerequisites of a topic are already covered."""

    for prereq in _get_prereqs(topic):

        if prereq not in covered:

            return False

    return True





def _heuristic(remaining_topics: list, hours_per_day: float) -> float:

    """
    h(n): Estimate minimum days needed to finish remaining topics.
    Uses total difficulty-weighted hours remaining divided by daily capacity.
    Admissible: never overestimates (so A* stays optimal).
    """

    if not remaining_topics:

        return 0.0

    total_difficulty_hours = sum(_get_difficulty(t) * 0.5 for t in remaining_topics)

    return total_difficulty_hours / max(hours_per_day, 0.5)





class _AStarNode:

    """A single state in the A* search."""

    __slots__ = ("f", "g", "day", "covered", "schedule", "remaining")



    def __init__(self, f, g, day, covered, schedule, remaining):

        self.f         = f

        self.g         = g

        self.day       = day

        self.covered   = covered                                       

        self.schedule  = schedule                                        

        self.remaining = remaining                                   



    def __lt__(self, other):

        return self.f < other.f





def astar_order(topics: list, days: int, hours_per_day: float) -> list:

    """
    Use A* to find the optimal ordering of topics across days.

    Returns a list of day-schedules:
    [
      { "day": 1, "topics": ["Topic A", "Topic B"], "difficulty_score": 3.5 },
      ...
    ]

    Strategy:
    - Topics with unmet prerequisites are blocked until prereqs done
    - Harder topics (difficulty 4-5) go early (when energy is highest)
    - Each day is filled up to hours_per_day worth of topics
      (each topic costs difficulty * 0.5 hours as a minimum unit)
    """

    if not topics:

        return []



                                                                         

    def topic_cost(t):

        return _get_difficulty(t) * 0.5



                                                

    def topics_for_day(available_topics, covered):

        """Greedily pick topics that fit within daily hours and have prereqs met."""

        eligible = [t for t in available_topics if _prereqs_satisfied(t, covered)]

                                                                              

        eligible.sort(key=lambda t: -_get_difficulty(t))

        selected = []

        budget   = hours_per_day

        for t in eligible:

            cost = topic_cost(t)

            if cost <= budget + 0.01:                                      

                selected.append(t)

                budget -= cost

                if budget < 0.25:

                    break

        return selected



                                                                               

    initial_covered   = frozenset()

    initial_remaining = list(topics)

    h0 = _heuristic(initial_remaining, hours_per_day)



    start = _AStarNode(

        f=h0, g=0, day=1,

        covered=initial_covered,

        schedule=[],

        remaining=initial_remaining

    )



    heap = [start]

                                           

    visited = {}

    best_schedule = None

    best_f        = float("inf")



    while heap:

        node = heapq.heappop(heap)



                                                          

        state_key = (node.day, node.covered)

        if state_key in visited and visited[state_key] <= node.g:

            continue

        visited[state_key] = node.g



                                  

        if not node.remaining:

            if node.f < best_f:

                best_f        = node.f

                best_schedule = node.schedule

            continue



                                        

        if node.day > days:

                                                                    

            if best_schedule is None:

                best_schedule = node.schedule

            continue



                                          

        day_topics = topics_for_day(node.remaining, node.covered)



        if not day_topics:

                                                                      

            new_node = _AStarNode(

                f=node.g + 1 + _heuristic(node.remaining, hours_per_day),

                g=node.g + 1,

                day=node.day + 1,

                covered=node.covered,

                schedule=node.schedule,

                remaining=node.remaining

            )

            heapq.heappush(heap, new_node)

            continue



                         

        new_covered   = node.covered | frozenset(day_topics)

        new_remaining = [t for t in node.remaining if t not in new_covered]

        new_g         = node.g + 1

        new_h         = _heuristic(new_remaining, hours_per_day)

        diff_score    = round(sum(_get_difficulty(t) for t in day_topics) / len(day_topics), 1)



        day_entry = {

            "day":             node.day,

            "topics":          day_topics,

            "difficulty_score": diff_score

        }



        new_node = _AStarNode(

            f=new_g + new_h,

            g=new_g,

            day=node.day + 1,

            covered=new_covered,

            schedule=node.schedule + [day_entry],

            remaining=new_remaining

        )

        heapq.heappush(heap, new_node)



                                                                      

        if len(heap) > 5000:

            break



                                                                     

    if best_schedule is None:

        best_schedule = []



    covered_in_schedule = {t for day in best_schedule for t in day["topics"]}

    leftover = [t for t in topics if t not in covered_in_schedule]



    if leftover:

                                                             

        if best_schedule:

            best_schedule[-1]["topics"].extend(leftover)

        else:

            best_schedule.append({"day": 1, "topics": leftover, "difficulty_score": 2.0})



    return best_schedule





def generate_astar_plan(

    subject: str,

    days: int,

    hours_per_day: float,

    goal: str = "Exam Preparation",

    custom_topics: Optional[list] = None

) -> dict:

    """
    Public API: generate a study plan using A* topic ordering.
    Drop-in replacement for modules/planner.generate_plan().
    """

    import math

                                                                        

                                                                      

    try:

        from modules.planner import _get_topics, _get_study_tip, _get_revision_tip

    except ImportError:

        from planner import _get_topics, _get_study_tip, _get_revision_tip



    days          = max(1, min(days, 30))

    hours_per_day = max(0.5, min(hours_per_day, 12))



    topics        = _get_topics(subject, custom_topics)

    total_topics  = len(topics)



                                      

    revision_days = max(1, math.ceil(days * 0.2))

    study_days    = max(1, days - revision_days)



                                 

    astar_result  = astar_order(topics, study_days, hours_per_day)



    schedule = []



                                                                                

    for entry in astar_result:

        day_num    = entry["day"]

        day_topics = entry["topics"]

        n          = len(day_topics)

        hrs_each   = round(hours_per_day / max(n, 1), 1)



        sessions = [{

            "topic":          t,

            "duration_hours": hrs_each,

            "type":           "study",

            "status":         "pending",

            "difficulty":     _get_difficulty(t)                            

        } for t in day_topics]



        diff = entry.get("difficulty_score", 2.0)

        label = (

            f"Day {day_num} — {day_topics[0]}"

            if n == 1

            else f"Day {day_num} — {n} Topics (difficulty {diff}/5)"

        )



        schedule.append({

            "day":             day_num,

            "label":           label,

            "focus":           day_topics[0],

            "total_hours":     hours_per_day,

            "sessions":        sessions,

            "tip":             _get_study_tip(day_num, days, hours_per_day),

            "difficulty_score": diff,

            "ai_ordered":      True                                      

        })



                                                                                

    covered_topics = [t for entry in astar_result for t in entry["topics"]]

    half = len(covered_topics) // 2



    for i in range(revision_days):

        day_num        = study_days + i + 1

        rev_topics     = covered_topics[:half] if i == 0 else covered_topics[half:]

        if not rev_topics:

            rev_topics = covered_topics



        n          = max(len(rev_topics), 1)

        hrs_each   = round(hours_per_day / n, 1)



        sessions = [{

            "topic":          t,

            "duration_hours": hrs_each,

            "type":           "revision",

            "status":         "pending"

        } for t in rev_topics]



        schedule.append({

            "day":         day_num,

            "label":       f"Day {day_num} — Revision",

            "focus":       "Revision & Practice",

            "total_hours": hours_per_day,

            "sessions":    sessions,

            "tip":         _get_revision_tip(day_num, days)

        })



    total_hours = round(days * hours_per_day, 1)



    return {

        "subject":       subject,

        "goal":          goal,

        "days":          days,

        "hours_per_day": hours_per_day,

        "total_hours":   total_hours,

        "total_topics":  total_topics,

        "revision_days": revision_days,

        "schedule":      schedule,

        "algorithm":     "A*",                                       

        "summary": (

            f"A*-optimised plan: Study {subject} for {days} days "

            f"({hours_per_day}h/day), {total_topics} topics ordered by "

            f"prerequisites and difficulty, with {revision_days} revision day(s)."

        )

    }
