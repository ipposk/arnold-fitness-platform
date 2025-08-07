from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class PentestFinding(BaseModel):
    type: str
    host: str
    port: int
    service: str
    status: str


class PentestChecklistItem(BaseModel):
    step: str
    status: str


class PentestContext(BaseModel):
    test_id: str
    phase: str
    pt_type: str
    domain: str
    targets: List[str]
    credentials: List[str]
    entities: List[str]
    goal: str
    evidence: List[str]
    next_action: str
    checklist: List[PentestChecklistItem]
    findings: List[PentestFinding]
    meta: Dict[str, str]
