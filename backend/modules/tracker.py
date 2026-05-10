"""
tracker.py
Manages task progress using JSON file storage.
Handles: creating tasks, marking done/pending, fetching progress stats.
"""



import json

import os

import uuid

from datetime import datetime

from typing import Optional



DATA_DIR  = os.path.join(os.path.dirname(__file__), "..", "data")

TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")

PLANS_FILE = os.path.join(DATA_DIR, "plans.json")





def _ensure_data_dir():

    """Create data directory and files if they don't exist."""

    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(TASKS_FILE):

        with open(TASKS_FILE, "w") as f:

            json.dump([], f)

    if not os.path.exists(PLANS_FILE):

        with open(PLANS_FILE, "w") as f:

            json.dump({}, f)





def _read_tasks() -> list:

    _ensure_data_dir()

    try:

        with open(TASKS_FILE, "r") as f:

            return json.load(f)

    except (json.JSONDecodeError, FileNotFoundError):

        return []





def _write_tasks(tasks: list):

    _ensure_data_dir()

    with open(TASKS_FILE, "w") as f:

        json.dump(tasks, f, indent=2)





def _read_plans() -> dict:

    _ensure_data_dir()

    try:

        with open(PLANS_FILE, "r") as f:

            return json.load(f)

    except (json.JSONDecodeError, FileNotFoundError):

        return {}





def _write_plans(plans: dict):

    _ensure_data_dir()

    with open(PLANS_FILE, "w") as f:

        json.dump(plans, f, indent=2)





                                                                                



def create_tasks_from_plan(plan: dict) -> list:

    """
    Convert a generated plan into individual tasks and save to storage.
    Returns the list of created task dicts.
    """

    tasks = _read_tasks()

    new_tasks = []

    plan_id = str(uuid.uuid4())[:8]



    for day in plan["schedule"]:

        for session in day["sessions"]:

            task = {

                "id": str(uuid.uuid4())[:8],

                "plan_id": plan_id,

                "subject": plan["subject"],

                "day": day["day"],

                "day_label": day["label"],

                "topic": session["topic"],

                "duration_hours": session["duration_hours"],

                "type": session["type"],

                "status": "pending",

                "created_at": datetime.now().isoformat(),

                "completed_at": None

            }

            new_tasks.append(task)



    tasks.extend(new_tasks)

    _write_tasks(tasks)



                              

    plans = _read_plans()

    plans[plan_id] = {

        "plan_id": plan_id,

        "subject": plan["subject"],

        "goal": plan["goal"],

        "days": plan["days"],

        "hours_per_day": plan["hours_per_day"],

        "created_at": datetime.now().isoformat(),

        "summary": plan["summary"]

    }

    _write_plans(plans)



    return new_tasks, plan_id





def get_all_tasks(subject: Optional[str] = None, status: Optional[str] = None) -> list:

    """Return tasks, optionally filtered by subject or status."""

    tasks = _read_tasks()



    if subject:

        tasks = [t for t in tasks if t.get("subject", "").lower() == subject.lower()]

    if status:

        tasks = [t for t in tasks if t.get("status") == status]



    return tasks





def mark_task(task_id: str, status: str) -> Optional[dict]:

    """
    Mark a task as 'done' or 'pending'.
    Returns updated task or None if not found.
    """

    if status not in ("done", "pending"):

        raise ValueError("Status must be 'done' or 'pending'")



    tasks = _read_tasks()

    for task in tasks:

        if task["id"] == task_id:

            task["status"] = status

            task["completed_at"] = datetime.now().isoformat() if status == "done" else None

            _write_tasks(tasks)

            return task



    return None





def get_progress_stats(subject: Optional[str] = None) -> dict:

    """
    Return progress statistics.
    If subject given, filter to that subject only.
    """

    tasks = get_all_tasks(subject=subject)



    if not tasks:

        return {

            "total": 0, "done": 0, "pending": 0,

            "percentage": 0, "status": "no_tasks",

            "subject": subject or "all"

        }



    total   = len(tasks)

    done    = sum(1 for t in tasks if t["status"] == "done")

    pending = total - done

    pct     = round((done / total) * 100)



                               

    if pct == 0:

        status_msg = "not_started"

    elif pct < 30:

        status_msg = "just_started"

    elif pct < 60:

        status_msg = "in_progress"

    elif pct < 85:

        status_msg = "almost_there"

    elif pct < 100:

        status_msg = "nearly_done"

    else:

        status_msg = "completed"



                     

    total_hours = round(sum(t.get("duration_hours", 0) for t in tasks), 1)

    done_hours  = round(sum(t.get("duration_hours", 0) for t in tasks if t["status"] == "done"), 1)



    return {

        "total": total,

        "done": done,

        "pending": pending,

        "percentage": pct,

        "status": status_msg,

        "subject": subject or "all",

        "total_hours": total_hours,

        "done_hours": done_hours,

        "remaining_hours": round(total_hours - done_hours, 1)

    }





def get_next_task(subject: Optional[str] = None) -> Optional[dict]:

    """Return the next pending task (lowest day number first)."""

    tasks = get_all_tasks(subject=subject, status="pending")

    if not tasks:

        return None

                                     

    tasks.sort(key=lambda t: (t.get("day", 99), t.get("id", "")))

    return tasks[0]





def get_adaptive_suggestion(subject: Optional[str] = None) -> dict:

    """
    Generate an adaptive suggestion based on current progress.
    Returns a dict with suggestion type and message.
    """

    stats = get_progress_stats(subject)

    next_task = get_next_task(subject)



    if stats["total"] == 0:

        return {

            "type": "create_plan",

            "message": "No study plan found yet. Create a plan by saying: 'Create a study plan for [subject] in [N] days with [H] hours/day'."

        }



    pct = stats["percentage"]

    done_hours = stats["done_hours"]



                                                                          

    recent_done = get_all_tasks(subject=subject, status="done")

    recent_done.sort(key=lambda t: t.get("completed_at") or "", reverse=True)

    recent_hours = sum(t.get("duration_hours", 0) for t in recent_done[:6])



    if recent_hours >= 4.0:

        return {

            "type": "break",

            "message": f"🧠 You've studied {recent_hours:.1f} hours recently — great work! Take a 15-20 minute break. Rest improves long-term retention."

        }



    if pct == 100:

        return {

            "type": "completed",

            "message": "🎉 You've completed all tasks! Consider doing a full mock exam or teaching the concepts to someone else to solidify your knowledge."

        }



    if next_task:

        if pct >= 70:

            msg = f"📖 Almost there! Next up: **{next_task['topic']}** (Day {next_task['day']}, {next_task['duration_hours']}h). You're {pct}% done — keep going!"

        elif pct >= 40:

            msg = f"📚 Good momentum! Continue with: **{next_task['topic']}** ({next_task['duration_hours']}h). You're {pct}% through the plan."

        else:

            msg = f"🚀 Let's keep building! Next task: **{next_task['topic']}** (Day {next_task['day']}, {next_task['duration_hours']}h). You've completed {pct}% so far."



        if pct > 0 and pct % 25 == 0:

            msg += f"\n\n💡 Revision tip: You've hit {pct}% — great time to quickly review completed topics before moving forward."



        return {

            "type": "next_task",

            "task_id": next_task["id"],

            "task": next_task["topic"],

            "day": next_task["day"],

            "message": msg

        }



    return {

        "type": "revision",

        "message": f"✅ All study sessions done! Your progress: {pct}%. Focus on revising weak areas and solving past papers."

    }

