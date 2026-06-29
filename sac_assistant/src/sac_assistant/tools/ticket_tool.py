import uuid


def open_ticket(question: str, reason: str) -> str:
    ticket_id = str(uuid.uuid4())[:8]
    print(f"[Escalation] Ticket {ticket_id} opened for question: '{question}' (reason: {reason})")
    return ticket_id
