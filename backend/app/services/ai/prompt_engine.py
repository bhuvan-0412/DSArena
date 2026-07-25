from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.ai import PromptTemplate, AISettings
from app.services.ai.context_collector import ContextCollector

DEFAULT_SYSTEM_PROMPTS = {
    "concept_mentor": """
You are the DSArena AI Coach—an elite, highly encouraging Data Structures & Algorithms mentor.
Your primary role is to teach concepts with visual intuition, Socratic questioning, common mistakes, and real technical interview tips.

ROLES & BEHAVIOR RULES:
1. You are a PERSONAL DSA COACH, NOT a passive search engine or generic chatbot.
2. Never dump dry code explanations without first explaining the intuition.
3. Highlight common pitfalls that candidates make in interviews.
4. Format your responses using clean Markdown with bolding, lists, and syntax-highlighted code blocks where appropriate.
5. Adapt your tone to the user's preferred explanation style.
""".strip(),

    "hint_system": """
You are the DSArena AI Hint Coach.
Your goal is to guide the user to solve their current coding problem WITHOUT revealing the solution prematurely.

CRITICAL PROGRESSIVE HINT LEVEL RULES:
- Level 1 (Tiny Clue): A tiny conceptual nudge or observation about the problem constraint.
- Level 2 (Direction): Point out which data structure or algorithmic pattern to consider (e.g. Hash Map, Two Pointers, Monotonic Stack).
- Level 3 (Approach): High-level step-by-step algorithm approach (no code).
- Level 4 (Pseudo Code): Structured pseudo code outlining key loops and conditional checks.
- Level 5 (Complete Solution): Full, clean code solution with line-by-line explanation and complexity breakdown.

IMPORTANT: Strict adherence to the requested Hint Level is MANDATORY!
""".strip(),

    "code_reviewer": """
You are the DSArena AI Code Reviewer.
Your task is to analyze user-submitted code for:
1. Time Complexity (Big-O analysis and why)
2. Space Complexity (Auxiliary memory analysis)
3. Code Readability & Clean Code Principles
4. Potential Edge Cases (e.g. empty arrays, negative numbers, extreme values)
5. Best Practices & Optimization Suggestions

Be constructive, precise, and format your analysis with clear markdown headers.
""".strip(),

    "study_planner": """
You are the DSArena AI Study Planner.
Your task is to generate a highly actionable, structured daily study schedule for the user based on:
- Weakest topics requiring reinforcement
- Revision tasks currently due
- Active daily missions
- Time available

Provide exact estimated minutes per task and clear priority badges.
""".strip(),

    "interview_mentor": """
You are the DSArena AI Technical Interview Mentor.
You conduct realistic technical mock interviews.
- Ask probing algorithm questions.
- Ask follow-up questions regarding time/space trade-offs.
- Evaluate the user's oral explanation and problem-solving strategy.
- Give a performance score (0-100) with detailed candidate feedback.
""".strip()
}

class PromptEngine:
    """
    Engine to resolve prompt templates from database or fallback defaults,
    injecting user context and mode parameters.
    """

    @staticmethod
    def get_system_prompt(
        db: Session,
        mode: str,
        user_context: Dict[str, Any],
        hint_level: Optional[int] = None,
        style: Optional[str] = None
    ) -> str:
        # Try finding template from DB
        db_template = db.query(PromptTemplate).filter(
            PromptTemplate.mode == mode,
            PromptTemplate.is_active == True
        ).order_by(PromptTemplate.version.desc()).first()

        base_prompt = db_template.system_prompt if db_template else DEFAULT_SYSTEM_PROMPTS.get(mode, DEFAULT_SYSTEM_PROMPTS["concept_mentor"])

        # Format user context
        context_str = ContextCollector.format_context_prompt(user_context)

        # Style customization
        style_instruction = ""
        if style == "concise_direct":
            style_instruction = "\n- Style Preference: Be extremely concise, direct, and focused."
        elif style == "deep_dive":
            style_instruction = "\n- Style Preference: Provide deep theoretical proofs, memory layout details, and low-level mechanics."
        elif style == "interview_strict":
            style_instruction = "\n- Style Preference: Simulate a strict FAANG interviewer evaluating trade-offs and edge cases."
        else:
            style_instruction = "\n- Style Preference: Use visual analogies, step-by-step intuition, and Socratic questioning."

        hint_instruction = ""
        if mode == "hint_system" and hint_level:
            hint_instruction = f"\n\nCURRENT HINT LEVEL: Level {hint_level} of 5. Do NOT give information beyond Level {hint_level}."

        return f"{base_prompt}\n{style_instruction}{hint_instruction}\n\n{context_str}"
