"""
routes/tracker.py
Endpoints for task tracking and progress management.

AI-powered endpoints:
  GET /api/retention  — forgetting curve scores per completed topic
  GET /api/suggest    — checks forgetting curve first, then adaptive rules
"""



from flask import Blueprint, request, jsonify

from modules.tracker import (

    get_all_tasks, mark_task, get_progress_stats,

    get_next_task, get_adaptive_suggestion

)

from modules.forgetting_curve import (

    get_retention_scores,

    get_forgetting_curve_suggestion

)



tracker_bp = Blueprint("tracker", __name__)





@tracker_bp.route("/tasks", methods=["GET"])

def list_tasks():

    subject = request.args.get("subject")

    status  = request.args.get("status")

    tasks   = get_all_tasks(subject=subject, status=status)

    return jsonify({"success": True, "count": len(tasks), "tasks": tasks})





@tracker_bp.route("/tasks/<task_id>/status", methods=["PATCH"])

def update_task_status(task_id: str):

    body   = request.get_json(silent=True) or {}

    status = body.get("status")



    if status not in ("done", "pending"):

        return jsonify({"error": "status must be 'done' or 'pending'"}), 400



    task = mark_task(task_id, status)

    if not task:

        return jsonify({"error": f"Task '{task_id}' not found"}), 404



    return jsonify({"success": True, "task": task})





@tracker_bp.route("/progress", methods=["GET"])

def progress():

    subject = request.args.get("subject")

    stats   = get_progress_stats(subject)

    return jsonify({"success": True, "stats": stats})





@tracker_bp.route("/suggest", methods=["GET"])

def suggest():

    """
    Smart suggestion endpoint.
    Checks forgetting curve first — if a topic is fading fast,
    that takes priority over the regular next-task suggestion.
    """

    subject = request.args.get("subject")



    fc = get_forgetting_curve_suggestion(subject)

    if fc["type"] == "forgetting_curve" and fc.get("urgency") in ("high", "medium"):

        return jsonify({

            "success":    True,

            "suggestion": fc,

            "source":     "forgetting_curve"

        })



    suggestion = get_adaptive_suggestion(subject)

    return jsonify({

        "success":    True,

        "suggestion": suggestion,

        "source":     "adaptive_rules"

    })





@tracker_bp.route("/next", methods=["GET"])

def next_task():

    subject = request.args.get("subject")

    task    = get_next_task(subject)

    if not task:

        return jsonify({"success": True, "task": None, "message": "All tasks completed!"})

    return jsonify({"success": True, "task": task})





@tracker_bp.route("/retention", methods=["GET"])

def retention():

    """
    GET /api/retention?subject=Python (optional)

    Returns forgetting curve retention scores for all completed tasks,
    sorted by retention ascending (most forgotten first).

    Response:
    {
      "success": true,
      "count": 5,
      "retention_scores": [
        {
          "task_id": "abc",
          "topic": "Graphs (BFS/DFS)",
          "retention_pct": 42.1,
          "needs_revision": true,
          "urgency": "high"
        },
        ...
      ]
    }
    """

    subject = request.args.get("subject")

    scores  = get_retention_scores(subject)

    return jsonify({

        "success":          True,

        "count":            len(scores),

        "retention_scores": scores

    })
