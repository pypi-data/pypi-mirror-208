from pydantic import BaseModel
from typing import List


class Form(BaseModel):
    id: int
    ra_number: str
    survey_number: int


class Group(BaseModel):
    id: int
    group_name: str


class Role(BaseModel):
    id: int
    role_name: str


class GetFormWithGroupsResponse(BaseModel):
    form: Form
    readers: List[Group]
    writers: List[Group]


class GetGroupWithRolesAndFormsResponse(BaseModel):
    group: Group
    direct_roles: List[Role]
    inherited_roles: List[Role]
    forms_read: List[Form]
    forms_write: List[Form]


class GetRoleWithGroupsResponse(BaseModel):
    role: Role
    direct_members: List[Group]
    inherited_members: List[Group]
