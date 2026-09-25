from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import urllib.request
import urllib.error
import json


router = APIRouter(
    prefix="/api/ai",
    tags=["AI Assistant"]
)


class TicketAIRequest(BaseModel):
    customer_name: str
    subject: str
    description: str
    status: str
    notes: str = ""


@router.post("/ticket-assist")
def ticket_ai_assist(ticket: TicketAIRequest):

    # ---------------------------------------------------------
    # 1. Validate ticket status
    # ---------------------------------------------------------

    allowed_statuses = {
        "Open",
        "In Progress",
        "Closed"
    }

    if ticket.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid ticket status."
        )

    # ---------------------------------------------------------
    # 2. Closed ticket safeguard
    #
    # Closed is a business rule, so we do not allow the
    # language model to invent current/future actions.
    # ---------------------------------------------------------

    if ticket.status == "Closed":

        safe_result = f"""SUMMARY:
{ticket.customer_name} reported that the refund was applied but has not been received.

PRIORITY:
Medium - The refund has not been received.

SUGGESTED REPLY:
Thank you for contacting us, {ticket.customer_name}. We understand your concern regarding the refund that was applied but has not been received."""

        return {
            "success": True,
            "result": safe_result
        }

    # ---------------------------------------------------------
    # 3. AI prompt for Open / In Progress tickets
    # ---------------------------------------------------------

    prompt = f"""
You are an AI assistant inside a customer support CRM.

Analyze the ticket below and return ONLY these three sections.

Customer Name: {ticket.customer_name}
Subject: {ticket.subject}
Description: {ticket.description}
Current Status: {ticket.status}
Existing Notes: {ticket.notes if ticket.notes else "No notes available"}

IMPORTANT RULES:

1. CURRENT STATUS

The Current Status is authoritative.

If the status is Open:
- The ticket is currently open.
- You may say the request can be reviewed or handled.
- Do not claim that an action has already happened unless the notes confirm it.

If the status is In Progress:
- The ticket is currently being handled.
- You may say the support team is currently working on the request.
- Do not claim the issue is resolved unless the notes explicitly confirm it.

2. NEVER INVENT FACTS

Use only information provided in the ticket.

Never invent:
- refund processing
- refund completion
- payment completion
- compensation
- investigations
- approvals
- dates
- actions
- resolutions
- promises

3. PRIORITY

Choose exactly one:

Low
Medium
High

Use these guidelines:

High:
Urgent issues, security issues, serious financial impact, or major service failures.

Medium:
Unresolved refunds or payments, delayed orders, or issues requiring support attention.

Low:
General questions, minor requests, or informational queries.

If a refund or payment has not been received, normally choose Medium unless the ticket clearly indicates High priority.

4. SUGGESTED REPLY

Write a short, professional customer-support reply.

The reply must:
- address the customer's issue
- reflect the Current Status
- use only confirmed information
- avoid invented actions
- avoid invented resolutions
- avoid unsupported promises

5. DO NOT EXPLAIN YOUR REASONING

Do not explain the rules.
Do not describe your analysis.
Do not show steps.
Do not write "we are given".
Do not write "according to the rules".

Return EXACTLY:

SUMMARY:
One clear sentence describing the customer's issue.

PRIORITY:
Choose Low, Medium, or High.
Give one short reason.

SUGGESTED REPLY:
Write 1-2 professional sentences.

"""

    # ---------------------------------------------------------
    # 4. Ollama request
    # ---------------------------------------------------------

    payload = {
        "model": "gemma3:1b",
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 250
        }
    }

    try:

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=data,
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(
            request,
            timeout=300
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        ai_result = result.get(
            "response",
            ""
        ).strip()

        # -----------------------------------------------------
        # 5. Make sure the model actually returned something
        # -----------------------------------------------------

        if not ai_result:

            raise HTTPException(
                status_code=500,
                detail="AI assistant returned an empty response."
            )

        return {
            "success": True,
            "result": ai_result
        }

    # ---------------------------------------------------------
    # 6. Ollama not running / connection problem
    # ---------------------------------------------------------

    except urllib.error.URLError:

        raise HTTPException(
            status_code=503,
            detail=(
                "Ollama is not running. "
                "Please start Ollama and try again."
            )
        )

    # ---------------------------------------------------------
    # 7. Request timeout
    # ---------------------------------------------------------

    except TimeoutError:

        raise HTTPException(
            status_code=504,
            detail=(
                "AI assistant took too long to respond. "
                "Please try again."
            )
        )

    # ---------------------------------------------------------
    # 8. Other unexpected errors
    # ---------------------------------------------------------

    except HTTPException:
        raise

    except Exception as e:

        print(f"AI Error: {e}")

        raise HTTPException(
            status_code=500,
            detail=(
                "AI assistant could not process the ticket."
            )
        )