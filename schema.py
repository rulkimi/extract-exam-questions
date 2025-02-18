from pydantic import BaseModel
from typing import List, Optional, Union

# content flow types
class TextContent(BaseModel):
    malay: str
    english: str

class Text(BaseModel):
    type: str = "text"
    text: TextContent

class Diagram(BaseModel):
    type: str = "diagram"
    name: str
    page: int

class Row(BaseModel):
    type: str = "row"
    layout: str
    items: List[Union[Text, Diagram]]

class Table(BaseModel):
    type: str = "table"
    name: str
    page: int

class AnswerSpace(BaseModel):
    type: str = "answer_space"
    format: str
    lines: Optional[int] = None

class TypeSubQuestion(BaseModel):
    type: str = "sub_question"
    number: str

class TypeQuestion(BaseModel):
    type: str = "question"
    number: str


#  question paper structure data models
class SubQuestion(BaseModel):
    number: str
    marks: Optional[int] = None
    content_flow: List[Union[Text, AnswerSpace]]

class Question(BaseModel):
    number: str
    marks: Optional[int] = None
    content_flow: List[Union[Text, AnswerSpace, TypeQuestion, TypeSubQuestion, Diagram, Row, Table]]
    sub_questions: Optional[SubQuestion]

class MainQuestion(BaseModel):
    number: int
    content_flow: List[Union[Text, AnswerSpace, TypeQuestion, TypeSubQuestion, Diagram, Row, Table]]
    questions: List[Question]

class Section(BaseModel):
    section_title: TextContent
    instructions: TextContent
    section_marks: int
    main_questions: List[MainQuestion]

class ExamFormat(BaseModel):
    sections: List[Section]
