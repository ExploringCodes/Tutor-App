from pydantic import BaseModel
from typing import List, Optional


class MCQBase(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    explanation: str  # Add this line for explanation
    hardness_level: Optional[str] = None  # Hardness level (optional) # Add this line for hardness level (or Integer if it's a numeric value)

class MCQCreate(MCQBase):
    subtopic_id: int

class SubtopicBase(BaseModel):
    name: str

class SubtopicCreate(SubtopicBase):
    topic_id: int

class TopicBase(BaseModel):
    name: str

class TopicCreate(TopicBase):
    subject_id: int

class SubjectBase(BaseModel):
    name: str

class SubjectCreate(SubjectBase):
    pass



# For the "Engaging" MCQs (Math or English) without hardness_level
class EngagingMCQBase(MCQBase):
    category: str  # "Math" or "English" category for the fun question

    # Override: Exclude hardness_level from EngagingMCQBase
    class Config:
        orm_mode = True
        # Exclude 'hardness_level' field from EngagingMCQBase
        fields = {'hardness_level': {'exclude': True}}

# # Schema for creating new engaging fun MCQs (Math or English)
# class EngagingMCQCreate(EngagingMCQBase):
#     pass

# Schema for returning existing Engaging MCQs (with an ID)
class EngagingMCQ(EngagingMCQBase):
    id: int

    class Config:
        orm_mode = True
        
        
# Models
class UserModel(BaseModel):
    id: Optional[int] = None
    email: str
    name: str
    picture: Optional[str] = None

class UserInteractionCreate(BaseModel):
    user_id: int
    interaction_type: str
    details: str