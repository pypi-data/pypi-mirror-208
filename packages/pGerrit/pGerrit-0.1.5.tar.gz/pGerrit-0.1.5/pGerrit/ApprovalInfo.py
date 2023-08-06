import json
from typing import Optional
from VotingRangeInfo import VotingRangeInfo

class ApprovalInfo:
    value: Optional[int] = None
    permitted_voting_range: Optional[str] = None
    date: Optional[str] = None
    tag: Optional[str] = None
    post_submit: Optional[bool] = None

    def __init__(self, value: Optional[int] = None, permitted_voting_range: Optional[str] = None, 
                 date: Optional[str] = None, tag: Optional[str] = None, post_submit: Optional[bool] = None) -> None:
        self.value = value
        self.permitted_voting_range = permitted_voting_range
        self.date = date
        self.tag = tag
        self.post_submit = post_submit

    @classmethod
    def from_json(cls, data: str) -> ApprovalInfo:
        json_data = json.loads(data)

        return cls(
            value=json_data.get('value'),
            date=json_data.get('date'),
            tag=json_data.get('tag'),
            post_submit=json_data.get('post_submit')
        )