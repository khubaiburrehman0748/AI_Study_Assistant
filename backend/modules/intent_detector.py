"""
intent_detector.py
Keyword-based intent detection — no ML required.
Classifies user input into one of 5 intents.

Used as a fallback by naive_bayes_classifier.py when confidence is low.
"""



import re



                                                                                



QUESTION_KEYWORDS = [

    "what", "why", "how", "when", "who", "where", "which",

    "explain", "define", "describe", "tell me", "meaning of",

    "difference between", "what is", "what are", "how does",

    "give me", "example of", "concept of", "theory of",

    "understand", "clarify", "elaborate"

]



PLANNING_KEYWORDS = [

    "study plan", "schedule", "plan", "timetable", "prepare",

    "exam in", "days left", "need to study", "help me study",

    "organize", "revision plan", "study schedule", "topics to cover",

    "make a plan", "create a plan", "generate plan", "learning path",

    "add plan", "add task", "new plan", "create task", "add a plan",

    "add a task", "add study", "new task"

]



PROGRESS_KEYWORDS = [

    "done", "completed", "finished", "mark as done", "i did",

    "i completed", "update progress", "check off", "i studied",

    "progress", "status", "how am i doing", "what's left",

    "remaining", "pending", "my tasks", "task done"

]



SUGGESTION_KEYWORDS = [

    "what should i", "suggest", "recommend", "next topic",

    "what next", "what should i study", "i'm stuck", "struggling",

    "need help with", "advice", "tip", "should i take a break",

    "what do i study", "study next"

]





def detect_intent(text: str) -> dict:

    """
    Detect user intent from input text.

    Returns:
        {
          "intent":     one of ["question", "planning", "progress", "suggestion", "general"],
          "confidence": "high" | "medium" | "low",
          "raw":        original text
        }
    """

    text_lower = text.lower().strip()



    scores = {

        "question":   0,

        "planning":   0,

        "progress":   0,

        "suggestion": 0,

    }



    for kw in QUESTION_KEYWORDS:

        if kw in text_lower:

            scores["question"] += 2 if text_lower.startswith(kw) else 1



    for kw in PLANNING_KEYWORDS:

        if kw in text_lower:

            scores["planning"] += 2



    for kw in PROGRESS_KEYWORDS:

        if kw in text_lower:

            scores["progress"] += 2



    for kw in SUGGESTION_KEYWORDS:

        if kw in text_lower:

            scores["suggestion"] += 2



                                              

    if text.strip().endswith("?"):

        scores["question"] += 3



                                                                  

    if re.search(r'what should i\s+(study|do|cover|review|focus)', text_lower):

        scores["suggestion"] += 5

        scores["question"]   -= 2



                                                 

    if re.search(r'\d+\s*day', text_lower):

        scores["planning"] += 3



    if any(p in text_lower for p in ["plan for", "study plan", "exam in", "add plan", "new plan"]):

        scores["planning"] += 4



    if any(p in text_lower for p in ["mark done", "i finished", "task complete"]):

        scores["progress"] += 4



    max_score = max(scores.values())



    if max_score == 0:

        return {"intent": "general", "confidence": "low", "raw": text}



    intent     = max(scores, key=scores.get)

    confidence = "high" if max_score >= 4 else "medium" if max_score >= 2 else "low"



    return {"intent": intent, "confidence": confidence, "raw": text}
