from typing import Any, Dict, List, Optional

from app.services.llm_service import llm_service


class MockInterviewService:
    """LLM-powered mock interview generation and evaluation."""

    DEFAULT_CATEGORIES = ["DSA", "OS", "DBMS", "HR"]

    async def generate_questions(
        self,
        focus_areas: Optional[List[str]] = None,
        difficulty: str = "medium",
        num_questions: int = 5,
    ) -> List[Dict[str, Any]]:
        categories = focus_areas or self.DEFAULT_CATEGORIES

        system = (
            "You are a technical interviewer at a top tech company. "
            "Generate realistic interview questions for placement preparation."
        )

        prompt = f"""Generate {num_questions} mock interview questions for a software engineering placement interview.

Categories to cover: {', '.join(categories)}
Difficulty: {difficulty}

Return JSON with key "questions" containing a list of objects, each with:
- index: number (0-based)
- category: string (DSA, OS, DBMS, CN, HR, etc.)
- question: string
- expected_topics: list of strings (key concepts the answer should cover)
- difficulty: string
"""

        result = await llm_service.generate_json(prompt, system=system, temperature=0.7)

        questions = result.get("questions", [])
        if not questions or result.get("parse_error"):
            questions = await self._fallback_questions(num_questions, categories, difficulty)

        for i, q in enumerate(questions):
            q["index"] = i
            q.setdefault("category", categories[i % len(categories)])
            q.setdefault("difficulty", difficulty)

        return questions[:num_questions]

    async def _fallback_questions(
        self,
        num: int,
        categories: List[str],
        difficulty: str,
    ) -> List[Dict[str, Any]]:
        """Generate questions one at a time if batch JSON fails."""
        questions = []
        for i in range(num):
            cat = categories[i % len(categories)]
            q_text = await llm_service.generate(
                f"Generate one {difficulty} difficulty {cat} interview question for software engineering placement. "
                "Return only the question text, no numbering.",
                system="You are a technical interviewer.",
                temperature=0.8,
            )
            questions.append({
                "index": i,
                "category": cat,
                "question": q_text,
                "expected_topics": [],
                "difficulty": difficulty,
            })
        return questions

    async def evaluate_answer(
        self,
        question: Dict[str, Any],
        answer: str,
    ) -> Dict[str, Any]:
        system = (
            "You are an experienced technical interviewer evaluating a candidate's answer. "
            "Be fair, constructive, and specific in feedback."
        )

        prompt = f"""Evaluate this interview answer.

Question ({question.get('category', 'General')}): {question.get('question', '')}
Expected topics: {question.get('expected_topics', [])}
Difficulty: {question.get('difficulty', 'medium')}

Candidate's answer:
{answer}

Return JSON with:
- score: number 0-10
- feedback: string (detailed constructive feedback, 2-4 sentences)
- strengths: list of strings
- improvements: list of strings
- key_points_missed: list of strings
"""

        result = await llm_service.generate_json(prompt, system=system, temperature=0.4)

        if result.get("parse_error"):
            feedback = await llm_service.generate(
                f"Evaluate this interview answer briefly:\nQ: {question.get('question')}\nA: {answer}",
                system=system,
            )
            result = {
                "score": 5.0,
                "feedback": feedback,
                "strengths": [],
                "improvements": ["Provide more structured answers"],
                "key_points_missed": [],
            }

        score = float(result.get("score", 5))
        result["score"] = max(0, min(10, score))
        return result


mock_interview_service = MockInterviewService()