from pydantic import BaseModel
from typing import List, Literal
from enum import Enum


class SkillType(int, Enum):
    with_skills = 0
    no_skills = 1


class SkillSetting(BaseModel):
    skill_id: str
    skill_desc: str = ''


class BaseRoleSetting(BaseModel):
    role_id: str
    role: Literal['user', 'assistant']
    type: SkillType | None = None
    name: str
    description: str
    skills: List[SkillSetting] | None = None


class UserRoleSetting(BaseRoleSetting):
    role_id: str = 'user'
    role: str = 'user'


class AgentRoleSetting(BaseRoleSetting):
    role: str = 'assistant'


class ScheduleItem(BaseModel):
    id: str
    role: UserRoleSetting | AgentRoleSetting
    skill: SkillSetting | None = None


class MutilAssistantChatRoomSetting(BaseModel):
    room_description: str
    roles: List[UserRoleSetting | AgentRoleSetting]


class Message(BaseModel):
    role: str
    content: str
    name: str


class NextRoundSignal(str, Enum):
    CONTINUE = '助理间还需要继续自动对话'
    BREAK = '需要用户参与对话'
