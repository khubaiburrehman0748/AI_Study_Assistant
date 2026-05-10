"""
routes/chat.py
Main chat endpoint — receives user messages, detects intent,
dispatches to appropriate handler, returns response.

AI features:
  - Intent detection: Naive Bayes classifier (with keyword fallback)
  - Suggestions:      Forgetting Curve checked before adaptive suggestion
  - Planning:         A* algorithm for optimal topic ordering
  - Q&A:              LLM (OpenRouter / Groq)
"""



import re

from flask import Blueprint, request, jsonify



from modules.naive_bayes_classifier import classify_intent

from modules.forgetting_curve import get_forgetting_curve_suggestion

from modules.astar_planner import generate_astar_plan

from modules.llm_handler import ask_llm

from modules.tracker import (

    create_tasks_from_plan, get_progress_stats,

    get_adaptive_suggestion, get_next_task, mark_task, get_all_tasks

)



chat_bp = Blueprint("chat", __name__)





@chat_bp.route("/chat", methods=["POST"])

def chat():

    """
    Main chat endpoint.
    Body: { "message": "user input here" }
    Returns: { "reply": "...", "intent": "...", "data": {...} }
    """

    body = request.get_json(silent=True)

    if not body or "message" not in body:

        return jsonify({"error": "Missing 'message' field"}), 400



    user_message = body["message"].strip()

    if not user_message:

        return jsonify({"error": "Empty message"}), 400



                                                                             

    intent_result = classify_intent(user_message)

    intent        = intent_result["intent"]

    method        = intent_result.get("method", "naive_bayes")



                                                                             

    reply, extra_data = _dispatch(intent, user_message, body)



    return jsonify({

        "reply":      reply,

        "intent":     intent,

        "confidence": intent_result["confidence"],

        "method":     method,

        "data":       extra_data

    })





def _dispatch(intent: str, message: str, body: dict) -> tuple:

    if intent == "question":

        return _handle_question(message, body)

    elif intent == "planning":

        return _handle_planning(message, body)

    elif intent == "progress":

        return _handle_progress(message, body)

    elif intent == "suggestion":

        return _handle_suggestion(message, body)

    else:

        return _handle_general(message)





                                                                                



def _extract_planning_params(text: str) -> dict:

    """
    Simple regex extraction of subject, days, and hours from a planning message.
    """

    text_lower = text.lower()

    params = {}



    day_match = re.search(r'(\d+)\s*day', text_lower)

    if day_match:

        params["days"] = int(day_match.group(1))



    hour_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|h)(?=[^a-zA-Z]|$)', text_lower)

    if hour_match:

        params["hours_per_day"] = float(hour_match.group(1))



                                                            

    _BLOCKLIST = {"plan", "a", "my", "the", "for", "me", "exam"}

    subject_patterns = [

        r'study\s+plan\s+for\s+([a-zA-Z][a-zA-Z\s]*?)(?:\s*,|\s+\d|\s+for|\s+in|\s*$)',

        r'plan\s+for\s+([a-zA-Z\s]+?)(?:\s+exam|\s+in|\s*,|\s+\d)',

        r'for\s+(?:my\s+)?([a-zA-Z\s]+?)\s+exam',

        r'study\s+([a-zA-Z\s]+?)(?:\s+for|\s+in|\s*,|\s*\.)',

        r'for\s+([a-zA-Z][a-zA-Z\s]*?)(?:\s*,|\s+\d)',

    ]

    for pattern in subject_patterns:

        match = re.search(pattern, text_lower)

        if match:

            subject = match.group(1).strip().title()

            if len(subject) > 1 and not subject.isdigit() and subject.lower() not in _BLOCKLIST:

                params["subject"] = subject

                break



    return params





def _progress_bar(pct: int, length: int = 10) -> str:

    filled = round(pct / 100 * length)

    return f"[{'█' * filled}{'░' * (length - filled)}]"





                                                                                



def _handle_question(message: str, body: dict) -> tuple:

    """Forward academic question to LLM."""

    context = body.get("context", "")

    answer  = ask_llm(message, context=context)

    return answer, {"type": "answer"}





def _handle_planning(message: str, body: dict) -> tuple:

    """Parse planning params, then generate a study plan using the A* algorithm."""

    params        = _extract_planning_params(message)

    subject       = body.get("subject")       or params.get("subject")

    days          = body.get("days")           or params.get("days")

    hours_per_day = body.get("hours_per_day")  or params.get("hours_per_day")

    goal          = body.get("goal", "Exam Preparation")

    custom_topics = body.get("topics")



    missing = []

    if not subject:       missing.append("subject")

    if not days:          missing.append("number of days")

    if not hours_per_day: missing.append("hours per day")



    if missing:

        prompt = "I'd love to build your study plan! I just need a few more details:\n"

        for m in missing:

            prompt += f"• {m.replace('_', ' ').title()}\n"

        prompt += "\nFor example: *'Study plan for Python, 5 days, 3 hours/day'*"

        return prompt, {"type": "planning_prompt", "missing": missing}



    plan = generate_astar_plan(

        subject=subject,

        days=int(days),

        hours_per_day=float(hours_per_day),

        goal=goal,

        custom_topics=custom_topics

    )



    tasks, plan_id = create_tasks_from_plan(plan)



    reply = (

        f"✅ **Study Plan Created for {plan['subject']}**\n"

        f"*(A\\* algorithm used to order topics by difficulty & prerequisites)*\n\n"

        f"📅 Duration: {plan['days']} days | ⏰ {plan['hours_per_day']}h/day | "

        f"📚 {plan['total_topics']} topics\n\n"

        f"{plan['summary']}\n\n"

        f"Your tasks have been saved. Say **'show my tasks'** to see them, "

        f"or **'what should I do next?'** to get started!"

    )



    return reply, {

        "type":       "plan",

        "plan":       plan,

        "plan_id":    plan_id,

        "task_count": len(tasks),

        "algorithm":  "A*"

    }





def _handle_progress(message: str, body: dict) -> tuple:

    """Handle progress updates and status queries."""

    msg_lower = message.lower()



    task_id = body.get("task_id")

    if task_id:

        new_status = "done" if any(w in msg_lower for w in ["done", "complete", "finish"]) else "pending"

        updated = mark_task(task_id, new_status)

        if updated:

            emoji = "✅" if new_status == "done" else "↩️"

            return (

                f"{emoji} Task **'{updated['topic']}'** marked as {new_status}.",

                {"type": "task_update", "task": updated}

            )

        return "❌ Task not found. Please check the task ID.", {"type": "error"}



    subject = body.get("subject")

    stats   = get_progress_stats(subject)



    if stats["total"] == 0:

        reply = "No tasks found. Create a study plan first by saying: *'Create a study plan for [subject]'*"

    else:

        bar   = _progress_bar(stats["percentage"])

        reply = (

            f"📊 **Your Progress" + (f" — {subject}" if subject else "") + "**\n\n"

            f"{bar} **{stats['percentage']}%**\n\n"

            f"✅ Completed: {stats['done']}/{stats['total']} tasks\n"

            f"⏳ Remaining: {stats['pending']} tasks ({stats['remaining_hours']}h)\n"

            f"🕐 Study time logged: {stats['done_hours']}h"

        )



    return reply, {"type": "progress", "stats": stats}





def _handle_suggestion(message: str, body: dict) -> tuple:

    """
    Return smart suggestion:
    1. First check forgetting curve — if a topic urgently needs revision, say so
    2. Otherwise fall back to the adaptive suggestion logic
    """

    subject = body.get("subject")



    fc_suggestion = get_forgetting_curve_suggestion(subject)

    if fc_suggestion["type"] == "forgetting_curve" and
       fc_suggestion.get("urgency") in ("high", "medium"):

        return fc_suggestion["message"], {

            "type":       "suggestion",

            "suggestion": fc_suggestion,

            "source":     "forgetting_curve"

        }



    suggestion = get_adaptive_suggestion(subject)

    return suggestion["message"], {

        "type":       "suggestion",

        "suggestion": suggestion,

        "source":     "adaptive_rules"

    }





def _handle_general(message: str) -> tuple:

    """Handle greetings and general chat."""

    msg_lower = message.lower()



    if any(w in msg_lower for w in ["hello", "hi", "hey", "good morning", "good evening"]):

        return (

            "👋 Hello! I'm your **AI Study Assistant**. Here's what I can do:\n\n"

            "• 📚 **Answer questions** — Ask me anything academic\n"

            "• 📅 **Create study plans** — Tell me your subject, days, and hours\n"

            "• ✅ **Track progress** — Mark tasks done, view completion stats\n"

            "• 💡 **Suggest next steps** — Ask 'What should I do next?'\n\n"

            "What would you like to start with?",

            {"type": "greeting"}

        )



    if any(w in msg_lower for w in ["thanks", "thank you", "great", "awesome"]):

        return (

            "You're welcome! Keep up the great work. 💪 Ask me anything whenever you need help.",

            {"type": "general"}

        )



    if any(w in msg_lower for w in ["help", "what can you do", "commands"]):

        return (

            "Here's how to use me:\n\n"

            "**Ask a question:**\n> What is recursion?\n\n"

            "**Create a study plan:**\n> Study plan for Database, 5 days, 2 hours/day\n\n"

            "**Check progress:**\n> Show my progress\n\n"

            "**Get a suggestion:**\n> What should I study next?",

            {"type": "help"}

        )



    answer = ask_llm(message)

    return answer, {"type": "answer_fallback"}
