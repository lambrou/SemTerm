from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, root_validator, ValidationError


class CaseData(BaseModel):
    case_metadata: Union[Dict, None] = None
    case_transcript: Union[List[Dict], None] = None
    case_id: str
    org_id: str
    source: str = "AI"
    summary: Optional[str] = None

    @root_validator
    def check_case_fields(cls, values):
        case_metadata = values.get('case_metadata')
        case_transcript = values.get('case_transcript')
        if not case_metadata and not case_transcript:
            raise ValidationError('At least one of case_metadata or case_transcript must be defined')
        return values


class Summary(BaseModel):
    summary: Optional[str] = None
    status: Optional[str] = 'PENDING'
    source: Optional[str] = None
    created_date: datetime = datetime.now()
    completed_date: Optional[datetime] = None


class CaseSummary(Summary):
    case_data: CaseData
