"""
llm_handler.py
Handles all LLM API calls (OpenRouter or Groq).
Used ONLY for: answering academic questions, generating explanations.
NOT used for system logic, planning structure, or task tracking.
"""



import os

import requests

import json



                                                                               

LLM_PROVIDER  = os.getenv("LLM_PROVIDER", "openrouter")                          

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

GROQ_API_KEY       = os.getenv("GROQ_API_KEY", "")



OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

GROQ_URL       = "https://api.groq.com/openai/v1/chat/completions"



               

OPENROUTER_MODEL = "meta-llama/llama-3-8b-instruct"

GROQ_MODEL       = "llama3-8b-8192"



                                                             

ACADEMIC_SYSTEM_PROMPT = """You are an expert academic tutor. Your job is to answer student questions clearly, accurately and concisely.

Rules:
- Give structured, easy-to-understand explanations
- Use examples where helpful
- Keep answers focused and relevant
- Use bullet points or numbered lists when explaining multi-step concepts
- Avoid unnecessary filler or vague statements
- If a concept has multiple layers, explain step by step
- Be encouraging but professional"""





def _call_openrouter(messages: list[dict]) -> str:

    """Send messages to OpenRouter API and return assistant reply."""

    if not OPENROUTER_API_KEY:

        return "⚠️ OpenRouter API key not configured. Set OPENROUTER_API_KEY in your .env file."



    headers = {

        "Authorization": f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type": "application/json",

        "HTTP-Referer": "http://localhost:5000",

        "X-Title": "AI Study Assistant"

    }

    payload = {

        "model": OPENROUTER_MODEL,

        "messages": messages,

        "max_tokens": 800,

        "temperature": 0.4

    }

    try:

        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"].strip()

    except requests.exceptions.Timeout:

        return "⚠️ Request timed out. Please try again."

    except requests.exceptions.HTTPError as e:

        return f"⚠️ API error ({e.response.status_code}): {e.response.text}"

    except Exception as e:

        return f"⚠️ Unexpected error: {str(e)}"





def _call_groq(messages: list[dict]) -> str:

    """Send messages to Groq API and return assistant reply."""

    if not GROQ_API_KEY:

        return "⚠️ Groq API key not configured. Set GROQ_API_KEY in your .env file."



    headers = {

        "Authorization": f"Bearer {GROQ_API_KEY}",

        "Content-Type": "application/json"

    }

    payload = {

        "model": GROQ_MODEL,

        "messages": messages,

        "max_tokens": 800,

        "temperature": 0.4

    }

    try:

        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"].strip()

    except requests.exceptions.Timeout:

        return "⚠️ Request timed out. Please try again."

    except requests.exceptions.HTTPError as e:

        return f"⚠️ API error ({e.response.status_code}): {e.response.text}"

    except Exception as e:

        return f"⚠️ Unexpected error: {str(e)}"





def ask_llm(user_question: str, context: str = "") -> str:

    """
    Public function: send an academic question to the LLM.
    context: optional extra info (e.g., subject being studied)
    Returns: string answer from the LLM.
    """

    messages = [{"role": "system", "content": ACADEMIC_SYSTEM_PROMPT}]



    if context:

        messages.append({

            "role": "user",

            "content": f"Context: {context}"

        })



    messages.append({"role": "user", "content": user_question})



    if LLM_PROVIDER == "groq":

        return _call_groq(messages)

    else:

        return _call_openrouter(messages)





def generate_topic_explanation(topic: str, subject: str, depth: str = "medium") -> str:

    """
    Generate a focused explanation of a study topic.
    depth: "brief" | "medium" | "detailed"
    """

    depth_map = {

        "brief":    "Give a short 2-3 sentence overview.",

        "medium":   "Give a clear explanation with one example. Aim for 150-200 words.",

        "detailed": "Give a thorough explanation with examples and sub-concepts. Aim for 300-400 words."

    }

    instruction = depth_map.get(depth, depth_map["medium"])



    prompt = f"""Subject: {subject}
Topic: {topic}
Task: {instruction}

Explain this topic clearly for a student preparing for an exam."""



    return ask_llm(prompt)

