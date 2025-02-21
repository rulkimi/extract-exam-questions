from pydantic import BaseModel
from typing import List, Optional, Literal
from enum import Enum

class ContentType(str, Enum):
    TEXT = "text"
    DIAGRAM = "diagram"
    ROW = "row"
    TABLE = "table"
    ANSWER_SPACE = "answer_space"
    SUB_QUESTION = "sub_question"
    QUESTION = "question"

class ContentFlowItem(BaseModel):
    type: ContentType 

    class Config:
        use_enum_values = True

class TextContent(BaseModel):
    malay: str
    english: Optional[str] = None

class Text(ContentFlowItem):
    type: Literal[ContentType.TEXT]
    text: TextContent

class Diagram(ContentFlowItem):
    type: Literal[ContentType.DIAGRAM]
    name: str
    page: int

class Row(ContentFlowItem):
    type: Literal[ContentType.ROW]
    layout: str
    items: List["ContentFlowItem"] 

class Table(ContentFlowItem):
    type: Literal[ContentType.TABLE]
    name: str
    page: int

class AnswerSpace(ContentFlowItem):
    type: Literal[ContentType.ANSWER_SPACE]
    format: str
    lines: Optional[int] = None

class TypeSubQuestion(ContentFlowItem):
    type: Literal[ContentType.SUB_QUESTION]
    number: str

class TypeQuestion(ContentFlowItem):
    type: Literal[ContentType.QUESTION]
    number: str

# enable automatic resolution of forward references
ContentFlowItem.model_rebuild()

class SubQuestion(BaseModel):
    number: str
    marks: Optional[int] = None
    content_flow: List[ContentFlowItem]

class Question(BaseModel):
    number: str
    marks: Optional[int] = None
    content_flow: List[ContentFlowItem]
    sub_questions: Optional[List[SubQuestion]] = None

class MainQuestion(BaseModel):
    number: int
    content_flow: List[ContentFlowItem]
    questions: List[Question]

class Section(BaseModel):
    section_title: TextContent
    instructions: TextContent
    section_marks: int
    main_questions: List[MainQuestion]

class ExamFormat(BaseModel):
    sections: List[Section]
