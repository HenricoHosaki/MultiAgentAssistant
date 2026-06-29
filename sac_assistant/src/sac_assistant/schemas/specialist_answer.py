from pydantic import BaseModel


class SpecialistAnswer(BaseModel):
    answer: str
    found_answer: bool