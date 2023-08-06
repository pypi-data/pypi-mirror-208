from typing import List, Optional
from enum import Enum, auto
from dataclasses import asdict, dataclass, field

@dataclass
class Actor:
    # id: int = field(init=False)  # pk
    key: str  # phone number
    type: str
    name: str
    # created: int = field(init=False)
    # updated: int = field(init=False)


@dataclass(order=True)
class Company:
    domain: str  # unique
    name: Optional[str] = None
    description: Optional[str] = None
    meta: dict = field(default_factory=dict)
    id: int = field(default=None)  # primary key
    uid: Optional[int] = field(default=None)  # foreign key


class EventType(str, Enum):
    CREATE = auto()
    ADVANCE = auto()
    VALIDATE = auto()
    SEND = auto()
    CLIENT_ACCEPT = auto()
    CONFLICT = auto()
    REJECT = auto()
    CRITERIA = auto()


@dataclass
class Event:
    
    search_uid: int  # fk # add index 
    domain: Optional[str]  # fk
    actor_key: str  # fk
    type: str  # build, advance, qualify, reject, conflict, rate
    data: dict = field(default_factory=dict)
    id: int = field(default=None)  # pk
    # created: int = field(init=False)


@dataclass
class Comment(Event):
    def __post_init__(self):
        assert isinstance(self.data["comment"], str)


@dataclass
class Rating(Event):
    def __post_init__(self):
        assert isinstance(self.data["rating"], int)

@dataclass
class Checkpoint:
    # actor_key: str  # foreign key
    event_id: int  # foreign key
    id: int  = field(default=None) # primary key
    # created: int  # timestamp

@dataclass(order=True)
class Target:
    domain: str  # enforce unique
    name: str
    search_id: int  # fk
    description: str
    event: List
    last_event_type: str  # enum EventType
    last_rating: int  # enum EventType
    meta: dict


@dataclass
class Criteria:
    search_id: int
    type: str  # include, exclude
    prompt: str
    rating: list
    employees_range: list
    country: list
    state: list
    ownership: list
    product: list
    services: list
    updated: int
    actor_id: int  # fk


@dataclass
class Search:
    
    uid: int  # foreign key, dealcloud id
    client_domain: str  # 
    label: str
    meta: dict = field(default_factory=dict)
    inclusion: dict = field(default_factory=dict)
    exclusion: dict = field(default_factory=dict)
    sort: dict = field(default_factory=dict)
    id: int  = field(default=None) # primary key
    # created: int = field(init=False)
    # updated: int = field(init=False)


@dataclass
class Sort:
    FIELDS = ["employee_count", "rating", "state", "country", "year_founded", "name"]
    ORDERS = ["asc", "desc"]

    field: str
    order: str
