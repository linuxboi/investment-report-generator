"""Conversational interface powered by stored reports and Gemini."""

from __future__ import annotations

from typing import Dict, List, Optional

from agno.agent import Agent
from agno.models.google import Gemini

from config import get_google_api_key
from embeddings import embed_text
from report_store import search_report_chunks

GOOGLE_API_KEY = get_google_api_key(required=True)

chat_agent = Agent(
    name="Investment Insight Chatbot",
    role="Answer investor questions using stored research reports",
    model=Gemini(
        id="gemini-2.0-flash-001",
        api_key=GOOGLE_API_KEY,
    ),
    instructions=[
        "You are a financial research assistant.",
        "Answer questions using ONLY the provided report excerpts.",
        "Cite the excerpt numbers you rely on (e.g., [Excerpt 2]).",
        "If the context lacks the answer, say you do not have enough information.",
        "Keep responses concise, professional, and data-driven.",
    ],
    markdown=True,
)


def build_prompt(question: str, excerpts: List[Dict[str, str]]) -> str:
    sections = []
    for idx, item in enumerate(excerpts, start=1):
        sections.append(f"[Excerpt {idx}]\n{item['content']}")

    joined_context = "\n\n".join(sections)
    return (
        "You are assisting an investor by answering questions grounded in the following investment reports.\n\n"
        f"Context:\n{joined_context}\n\n"
        "Follow the instructions carefully:\n"
        "- Only use information found in the excerpts.\n"
        "- Mention the excerpt references you draw from.\n"
        "- If the excerpts lack the answer, acknowledge the gap.\n\n"
        f"Investor question: {question}\n"
    )


def answer_question(
    question: str,
    *,
    report_id: Optional[str] = None,
    top_k: int = 5,
) -> Dict[str, object]:
    """Return a chatbot response and supporting excerpts."""

    query_embedding = embed_text(question)
    matches = search_report_chunks(query_embedding, report_id=report_id, top_k=top_k)

    if not matches:
        return {
            "reply": "I couldn’t locate relevant information in the stored reports for that question.",
            "sourceChunks": [],
        }

    prompt_excerpts: List[Dict[str, str]] = []
    for match in matches:
        prompt_excerpts.append(
            {
                "content": match["content"],
                "score": match["score"],
                "reportId": match["report_id"],
                "chunkIndex": match["chunk_index"],
            }
        )

    prompt = build_prompt(question, prompt_excerpts)
    result = chat_agent.run(prompt)
    reply = getattr(result, "content", str(result)).strip()

    return {
        "reply": reply,
        "sourceChunks": prompt_excerpts,
    }
