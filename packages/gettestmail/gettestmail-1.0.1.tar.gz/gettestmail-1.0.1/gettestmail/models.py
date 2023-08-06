from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Attachment:
    filename: str
    mimeType: str
    content: str


@dataclass
class Message:
    id: str
    from_: str
    to: str
    subject: str
    text: str
    html: str
    attachments: List[Attachment]


@dataclass
class GetTestMail:
    id: str
    emailAddress: str
    expiresAt: str
    message: Optional[Message] = None


@dataclass
class Problem:
    type: str
    title: str
    detail: str
    status: int
