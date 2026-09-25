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


# -------------------------------------------------------------
# Determine ticket priority using simple business rules.
# Priority is handled by Python instead of the AI model so that
# the result is consistent.
# -------------------------------------------------------------

def determine_priority(subject: str, description: str) -> tuple[str, str]:

    text = f"{subject} {description}".lower()

    # High-priority situations
    high_keywords = [
        "security breach",
        "hacked",
        "account compromised",
        "fraud",
        "unauthorized access",
        "critical",
        "emergency",
        "major outage",
        "serious financial loss"
    ]

    for keyword in high_keywords:
        if keyword in text:
            return (
                "High",
                f"High priority because the ticket mentions {keyword}."
            )

    # Medium-priority situations
    medium_keywords = [
        "refund",
        "payment",
        "order not received",
        "order hasn't arrived",
        "order has not arrived",
        "not received",
        "delayed",
        "delay",
        "missing order",
        "delivery"
    ]

    for keyword in medium_keywords:
        if keyword in text:
            return (
                "Medium",
                "The ticket concerns an unresolved customer issue."
            )

    # General / informational tickets
    return (
        "Low",
        "The ticket appears to be a general or low-urgency request."
    )


# -------------------------------------------------------------
# Generate a safe customer reply based on ticket status.
# Python controls this so the AI cannot invent actions,
# investigations, resolutions, or future promises.
# -------------------------------------------------------------

def generate_safe_reply(
    customer_name: str,
    subject: str,
    status: str
) -> str:

    subject_text = subject.strip().rstrip(".")

    if status == "Open":

        return (
            f"Thank you for contacting us, {customer_name}. "
            f"We understand your concern regarding {subject_text.lower()}. "
            f"Your ticket is currently open."
        )

    if status == "In Progress":

        return (
            f"Thank you for contacting us, {customer_name}. "
            f"We understand your concern regarding {subject_text.lower()}. "
            f"Your ticket is currently in progress."
        )

    # Closed
    return (
        f"Thank you for contacting us, {customer_name}. "
        f"We understand your concern regarding {subject_text.lower()}. "
        f"Your ticket is currently closed."
    )


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
    # 2. Determine priority using Python rules
    # ---------------------------------------------------------

    priority, priority_reason = determine_priority(
        ticket.subject,
        ticket.description
    )

    # ---------------------------------------------------------
    # 3. Generate safe customer reply
    # ---------------------------------------------------------

    safe_reply = generate_safe_reply(
        ticket.customer_name,
        ticket.subject,
        ticket.status
    )

    # ---------------------------------------------------------
    # 4. AI prompt
    #
    # Gemma is responsible ONLY for generating the summary.
    # Priority and customer reply are controlled by Python.
    # ---------------------------------------------------------

    prompt = f"""
You are an AI assistant inside a customer support CRM.

Analyze the support ticket below and write ONLY one summary.

Customer Name: {ticket.customer_name}
Subject: {ticket.subject}
Description: {ticket.description}
Current Status: {ticket.status}
Existing Notes: {ticket.notes if ticket.notes else "No notes available"}

IMPORTANT RULES:

1. Use only information explicitly provided in the ticket.

2. Do not invent:
- refund processing
- refund completion
- payment completion
- compensation
- investigation
- approval
- delivery
- dates
- actions
- resolution
- future promises

3. The Current Status is authoritative.

Open means the ticket is open.

In Progress means the ticket is currently in progress.

Closed means the ticket is closed.

4. Do not assume that a ticket status means that a specific action was performed.

For example:

In Progress does NOT automatically mean:
- the refund is being processed
- the order is being investigated
- the support team contacted the customer

Closed does NOT automatically mean:
- the issue was resolved
- the refund was received
- the payment was completed

5. Write one clear sentence describing the customer's actual issue.

IMPORTANT SUMMARY RULE:

Preserve the meaning of the original Subject and Description exactly.

Do NOT replace one state with another.

For example:

"not received" must NOT become:
- not processed
- processing
- pending
- delayed
- under review

unless those words or their meaning are explicitly present in the ticket.

"applied but not received" means exactly that:
the ticket says it was applied, but the customer has not received it.

Do not infer why something was not received.

Do not infer that a refund is pending, processing, delayed, or under review unless the ticket explicitly says so.

6. Do not write a customer reply.

7. Do not choose a priority.

8. Do not explain your reasoning.

Return ONLY:

SUMMARY:
One clear sentence describing the customer's issue.
"""

    # ---------------------------------------------------------
    # 5. Ollama request
    # ---------------------------------------------------------

    payload = {
        "model": "gemma3:1b",
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 100
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
        # 6. Make sure AI returned something
        # -----------------------------------------------------

        if not ai_result:

            raise HTTPException(
                status_code=500,
                detail="AI assistant returned an empty response."
            )

        # -----------------------------------------------------
        # 7. Remove accidental sections if Gemma adds them
        # -----------------------------------------------------

        if "PRIORITY:" in ai_result:

            ai_result = ai_result.split(
                "PRIORITY:"
            )[0].strip()

        if "SUGGESTED REPLY:" in ai_result:

            ai_result = ai_result.split(
                "SUGGESTED REPLY:"
            )[0].strip()

        # -----------------------------------------------------
        # 8. Build final response
        #
        # Summary = AI
        # Priority = Python
        # Suggested Reply = Python
        # -----------------------------------------------------

        final_result = f"""
{ai_result}

PRIORITY:
{priority} - {priority_reason}

SUGGESTED REPLY:
{safe_reply}
""".strip()

        return {
            "success": True,
            "result": final_result
        }

    # ---------------------------------------------------------
    # 9. Ollama connection error
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
    # 10. Timeout
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
    # 11. Preserve HTTP exceptions
    # ---------------------------------------------------------

    except HTTPException:
        raise

    # ---------------------------------------------------------
    # 12. Unexpected error
    # ---------------------------------------------------------

    except Exception as e:

        print(f"AI Error: {e}")

        raise HTTPException(
            status_code=500,
            detail=(
                "AI assistant could not process the ticket."
            )
        )