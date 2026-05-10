"""
routes/planner.py
Direct endpoints for study plan generation.
Now uses A* algorithm for optimal topic ordering.
"""



from flask import Blueprint, request, jsonify

from modules.astar_planner import generate_astar_plan

from modules.planner import generate_plan                                     

from modules.tracker import create_tasks_from_plan



planner_bp = Blueprint("planner", __name__)





@planner_bp.route("/plan", methods=["POST"])

def create_plan():

    """
    Create a study plan using A* algorithm.
    Body: {
        "subject":       "Python",
        "days":          5,
        "hours_per_day": 3,
        "goal":          "Final exam",   (optional)
        "topics":        ["Topic 1", ...]  (optional)
        "use_astar":     true            (optional, default true)
    }
    """

    body = request.get_json(silent=True) or {}



    subject       = body.get("subject")

    days          = body.get("days")

    hours_per_day = body.get("hours_per_day")

    use_astar     = body.get("use_astar", True)                     



    errors = []

    if not subject:       errors.append("'subject' is required")

    if not days:          errors.append("'days' is required")

    if not hours_per_day: errors.append("'hours_per_day' is required")

    if errors:

        return jsonify({"error": "; ".join(errors)}), 400



    try:

        days          = int(days)

        hours_per_day = float(hours_per_day)

    except (ValueError, TypeError):

        return jsonify({"error": "'days' must be integer, 'hours_per_day' must be number"}), 400



    goal          = body.get("goal", "Exam Preparation")

    custom_topics = body.get("topics")



                                                                 

    if use_astar:

        plan = generate_astar_plan(

            subject=subject,

            days=days,

            hours_per_day=hours_per_day,

            goal=goal,

            custom_topics=custom_topics

        )

    else:

        plan = generate_plan(

            subject=subject,

            days=days,

            hours_per_day=hours_per_day,

            goal=goal,

            custom_topics=custom_topics

        )



    tasks, plan_id = create_tasks_from_plan(plan)



    return jsonify({

        "success":       True,

        "plan_id":       plan_id,

        "plan":          plan,

        "tasks_created": len(tasks),

        "algorithm":     plan.get("algorithm", "linear")

    })





@planner_bp.route("/plan/preview", methods=["POST"])

def preview_plan():

    """Preview plan without saving. Uses A* by default."""

    body          = request.get_json(silent=True) or {}

    subject       = body.get("subject", "General")

    days          = int(body.get("days", 5))

    hours_per_day = float(body.get("hours_per_day", 2))

    goal          = body.get("goal", "Exam Preparation")

    use_astar     = body.get("use_astar", True)



    if use_astar:

        plan = generate_astar_plan(subject, days, hours_per_day, goal)

    else:

        plan = generate_plan(subject, days, hours_per_day, goal)



    return jsonify({"success": True, "plan": plan, "algorithm": plan.get("algorithm", "linear")})
