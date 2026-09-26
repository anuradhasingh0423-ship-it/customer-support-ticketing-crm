from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import urllib.request
import urllib.error
import json
import os


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
    # 2. Generate safe customer reply in Python
    #
    # This prevents the AI from inventing:
    # - investigations
    # - refunds
    # - resolutions
    # - future promises
    # ---------------------------------------------------------

    subject = ticket.subject.strip()

    if ticket.status == "Open":

        safe_reply = (
            f"Thank you for contacting us, {ticket.customer_name}. "
            f"We understand your concern regarding {subject.lower()}. "
            f"Your ticket is currently open."
        )

    elif ticket.status == "In Progress":

        safe_reply = (
            f"Thank you for contacting us, {ticket.customer_name}. "
            f"We understand your concern regarding {subject.lower()}. "
            f"Your ticket is currently in progress."
        )

    else:

        safe_reply = (
            f"Thank you for contacting us, {ticket.customer_name}. "
            f"We understand your concern regarding {subject.lower()}. "
            f"Your ticket is currently closed."
        )

    # ---------------------------------------------------------
    # 3. Determine priority in Python
    #
    # This makes priority predictable and prevents the small
    # local model from giving inconsistent results.
    # ---------------------------------------------------------

    text = (
        f"{ticket.subject} "
        f"{ticket.description} "
        f"{ticket.notes}"
    ).lower()

    high_keywords = [
        "fraud",
        "hacked",
        "security breach",
        "unauthorized",
        "account compromised",
        "critical",
        "urgent",
        "stolen",
        "major outage"
    ]

    medium_keywords = [
        "refund",
        "payment",
        "not received",
        "delayed",
        "delay",
        "order",
        "charged",
        "billing",
        "missing"
    ]

    if any(keyword in text for keyword in high_keywords):
        priority = "High"
        priority_reason = (
            "The ticket describes an urgent, security-related, "
            "or serious customer issue."
        )

    elif any(keyword in text for keyword in medium_keywords):
        priority = "Medium"
        priority_reason = (
            "The ticket concerns an unresolved customer issue "
            "requiring support attention."
        )

    else:
        priority = "Low"
        priority_reason = (
            "The ticket describes a general or lower-impact "
            "customer request."
        )

    # ---------------------------------------------------------
    # 4. AI prompt
    #
    # The AI is used only to create the ticket summary.
    # Priority and customer reply are controlled by Python.
    # ---------------------------------------------------------

    prompt = f"""
You are an AI assistant inside a customer support CRM.

Analyze the support ticket below.

Customer Name: {ticket.customer_name}
Subject: {ticket.subject}
Description: {ticket.description}
Current Status: {ticket.status}
Existing Notes: {ticket.notes if ticket.notes else "No notes available"}

IMPORTANT RULES:

1. Use ONLY information provided in the ticket.

2. Do NOT invent facts.

Never invent:
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

3. Current Status is authoritative.

Open means the ticket is currently open.

In Progress means the ticket is currently in progress.

Closed means the ticket is currently closed.

4. Do not assume that a status means a specific action happened.

For example:

In Progress does NOT automatically mean:
- the refund is being processed
- the order is being investigated
- the support team contacted the customer

Closed does NOT automatically mean:
- the issue was resolved
- the refund was received
- the payment was completed

5. SUMMARY

Write exactly ONE sentence describing the customer's actual issue.

Do not describe actions that are not explicitly confirmed.

6. Do NOT generate:
- priority
- suggested reply
- reasoning
- explanations
- recommendations

The application generates those separately.

Return ONLY:

SUMMARY:
One clear sentence describing the customer's issue.
"""

    # ---------------------------------------------------------
    # 5. Get OpenAI API key
    # ---------------------------------------------------------

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail=(
                "OPENAI_API_KEY is not configured. "
                "Add it to the Render environment variables."
            )
        )

    # ---------------------------------------------------------
    # 6. OpenAI model
    # ---------------------------------------------------------

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5.6-luna"
    )

    payload = {
        "model": model,
        "input": prompt,
        "max_output_tokens": 100
    }

    # ---------------------------------------------------------
    # 7. Send request to OpenAI
    # ---------------------------------------------------------

    try:

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST"
        )

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        # -----------------------------------------------------
        # 8. Extract generated text
        # -----------------------------------------------------

        text_parts = []

        for item in result.get("output", []):

            for content in item.get("content", []):

                if content.get("type") == "output_text":

                    generated_text = content.get(
                        "text",
                        ""
                    ).strip()

                    if generated_text:
                        text_parts.append(
                            generated_text
                        )

        ai_result = "\n".join(
            text_parts
        ).strip()

        # -----------------------------------------------------
        # 9. Check empty AI response
        # -----------------------------------------------------

        if not ai_result:

            raise HTTPException(
                status_code=500,
                detail="AI assistant returned an empty response."
            )

        # -----------------------------------------------------
        # 10. Clean accidental sections
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
        # 11. Make sure SUMMARY exists
        # -----------------------------------------------------

        if not ai_result.upper().startswith("SUMMARY:"):

            ai_result = (
                "SUMMARY:\n"
                + ai_result
            )

        # -----------------------------------------------------
        # 12. Build final CRM response
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
    # 13. OpenAI API error
    # ---------------------------------------------------------

    except urllib.error.HTTPError as e:

        try:

            error_body = e.read().decode(
                "utf-8"
            )

            error_data = json.loads(
                error_body
            )

            error_message = (
                error_data
                .get("error", {})
                .get(
                    "message",
                    "OpenAI API request failed."
                )
            )

        except Exception:

            error_message = (
                "OpenAI API request failed."
            )

        print(
            f"OpenAI API Error: {error_message}"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                f"AI service error: "
                f"{error_message}"
            )
        )

    # ---------------------------------------------------------
    # 14. Connection error
    # ---------------------------------------------------------

    except urllib.error.URLError as e:

        print(
            f"OpenAI connection error: {e}"
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Could not connect to the AI service. "
                "Please try again."
            )
        )

    # ---------------------------------------------------------
    # 15. Timeout
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
    # 16. Preserve FastAPI HTTP exceptions
    # ---------------------------------------------------------

    except HTTPException:

        raise

    # ---------------------------------------------------------
    # 17. Unexpected error
    # ---------------------------------------------------------

    except Exception as e:

        print(
            f"AI Error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "AI assistant could not process "
                "the ticket."
            )
        )