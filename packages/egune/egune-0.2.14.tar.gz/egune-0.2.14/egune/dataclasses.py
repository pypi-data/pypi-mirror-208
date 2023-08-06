from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Union
from datetime import datetime
from .enumerators import (
    CreatorType, SlotType, QuestionMode,
    IssueType, IssueStatus, ResolveActionType
)
from .utils import Dictable


@Dictable.decorator
@dataclass
class Text(Dictable):
    mutations: Dict[str, str]

    def __init__(self, mutations: Union[str, Dict[str, str]]):
        if isinstance(mutations, str):
            self.mutations = {"original": mutations}
        else:
            self.mutations = mutations

    def add_mutation(self, key, mutation):
        self.mutations[key] = mutation

    def get(self, key="original") -> str:
        return self.mutations[key] if key in self.mutations else ""


@Dictable.decorator
@dataclass
class Entity(Dictable):
    name: str
    input_type: str
    val: str
    sidx: int
    eidx: int
    confidence: float


@Dictable.decorator
@dataclass
class Intent(Dictable):
    chosen: str
    scores: Dict[str, float]
    positives: List[str]
    negatives: List[str]


@Dictable.decorator
@dataclass
class ResolveAction(Dictable):
    endpoint: Union[None, str]
    response: Dict[str, "ResolveAction"]
    responseCodes: List[str] 
    removeSlots: List[str]
    setSlots: Dict[str, Any]
    next_group: Union[None, str]
    type: ResolveActionType 

    @classmethod
    def from_dict(cls, dictionary):
        if isinstance(dictionary, str):
            dictionary = {
                "type": "response",
                "responseCodes": [dictionary]
            }
        return super().from_dict(dictionary)


@Dictable.decorator
@dataclass
class ResolveAttempt(Dictable):
    id: str
    created: datetime
    accepted: Union[None, bool]
    creator: CreatorType
    resolveAction: ResolveAction

    def is_equal(self, other):
        return self.resolveAction == other.resolveAction


@Dictable.decorator
@dataclass
class Question(Dictable):
    code: str
    type: SlotType
    mode: QuestionMode
    relatedSlotName: Union[None, str]
    slotFillValue: Union[None, List[Tuple[str, Any]]]
    relatedIssueName: Union[None, str]
    resolveId: Union[None, str]


@Dictable.decorator
@dataclass
class SlotVal(Dictable):
    name: str
    takenFromEntity: Union[None, str]
    value: Union[None, Any]  # TODO what if user dont want to give info
    default: Union[None, Any]

    def update_value(self, msg):
        if self.takenFromEntity is not None:
            self.value = msg.get_entity_val(self.takenFromEntity)


@Dictable.decorator
@dataclass
class Issue(Dictable):
    id: str
    type: IssueType
    name: str
    created: datetime
    assignees: List[str]
    status: IssueStatus
    resolveAttempts: List[ResolveAttempt]
    slotValues: Dict[str, SlotVal]
    expectingAnswers: List[Question]
    activeGroup: Union[None, str]


@Dictable.decorator
@dataclass
class UserSignature(Dictable):
    userId: Union[None, str]
    email: List[str]
    phone: List[str]


@Dictable.decorator
@dataclass
class Response(Dictable):
    code: str
    appId: str
    relatedSlot: Union[None, str]
    relatedIssueId: Union[None, str]


@Dictable.decorator
@dataclass
class Context(Dictable):
    userSignature: UserSignature
    variables: Dict[str, SlotVal]
    activeIssues: List[Issue]
    inactiveIssues: List[Issue]
    impendingQuestions: List[Question]
    impendingNotifications: List[str]
    lastResponseCodes: List[str]
    pastEntities: List[Entity]
    pastIntents: List[Intent]
    appId: str

    def apply_last_responses(self, responses: List[Response]):
        self.lastResponseCodes = [resp.code for resp in responses]

    def get_issue(self, issueId) -> Union[None, Issue]:
        for issue in self.activeIssues + self.inactiveIssues:
            if issue.id == issueId:
                return issue
        return None

    def get_resolve(self, resolveId) -> Union[None, ResolveAttempt]:
        for issue in self.activeIssues + self.inactiveIssues:
            for resolve in issue.resolveAttempts:
                if resolve.id == resolveId:
                    return resolve
        return None


@Dictable.decorator
@dataclass
class UserMessage(Dictable):
    user_id: str
    app_id: str
    channel_id: str
    text: Union[None, Text]
    intent: Union[None, Intent]
    entities: List[Entity]
    context: Union[None, Context]

    def select(self, key):
        args = key.split(":")
        if args[0] == "text":
            return self.text.get(args[1])  # type:ignore
        elif args[0] == "intent":
            return self.intent.chosen  # type:ignore
        elif args[0] == "entity":
            for e in self.entities:  # type:ignore
                if e.name == args[1]:
                    return e.val
        return ""

    def get_entity_val(self, name, default=None):
        if self.entities is not None:
            for e in self.entities:
                if e.name == name:
                    return e.val
        return default


@Dictable.decorator
@dataclass
class BotMessage(Dictable):
    user_id: str
    app_id: str
    channel_id: str
    code: Union[None, str]
    text: Union[None, str]
    buttons: List[str]
    misc: Any


@Dictable.decorator
@dataclass
class Event(Dictable):
    name: str
    responseCode: Union[None, str]
    issueQuestions: List[Question]
    responseVars: Any
    isFailed: bool
