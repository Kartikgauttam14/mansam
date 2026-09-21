# Mansam LLM-first conversation

The active `/api/chat` route now uses `rag_answer()` in `server.py`.

1. Typed text, button selections and speech transcripts enter the same browser handler.
2. The browser sends the message, recent conversation, profile and previous product IDs.
3. The configured Hugging Face model produces a structured search plan.
4. Python retrieves matching local catalog products and workbook records. Previous products are included for follow-ups.
5. A second model call receives these facts and the conversation, then writes the answer.
6. Python validates returned product IDs against the retrieved records and builds product links itself.
7. The browser displays the answer and optionally speaks it. It does not enforce the old questionnaire.

## Configuration

- `HF_TOKEN`: set privately in the backend environment; required.
- `HF_MODEL`: defaults to `meta-llama/Llama-3.1-8B-Instruct:novita`.
- `HF_API_URL`: defaults to `https://router.huggingface.co/v1/chat/completions`.
- `HF_TIMEOUT_SECONDS`: timeout per model call (default 20 seconds; maximum 60).

The new path uses the chat-completions API directly; the legacy Gradio configuration is not used by this route. The browser allows 125 seconds for the two sequential model calls and does not fall back to hardcoded product suggestions.

Without a token, on provider failure, invalid JSON, or an unverified product ID, the customer gets a temporary-unavailability response. No token or provider error body is displayed or logged.

## Accuracy and limits

Facts come from local JSON catalog snapshots and workbook exports; the existing background catalog refresh remains enabled. Retrieval is lexical, not an embedding/vector search. The model is instructed to use only supplied facts, honor preferences, answer interruptions, and ask at most one relevant clarification. Product IDs and links are validated in code; factual correctness of all generated prose is not independently guaranteed. Tests mock provider calls; a successful live inference still requires credentials and provider access.

The old `make_answer()` remains available for regression tests and reference but is not the active chat API handler. Stored history is bounded, so older preferences can fall out of conversation context.

## Checks

```text
python -m unittest discover -s tests
node tests/test_chat_flow.js
node --check js/chatbot.js
```
