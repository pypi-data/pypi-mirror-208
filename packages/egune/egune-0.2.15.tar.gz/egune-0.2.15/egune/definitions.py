from dataclasses import dataclass, field
from .utils import Dictable
from .enumerators import SlotType, IntentType, IssueType, IssueStatus, ResponseType, QuestionMode
from .dataclasses import SlotVal, Issue, ResolveAction
from typing import Any, List, Tuple, Union, Dict
from copy import deepcopy
from datetime import datetime


@Dictable.decorator
@dataclass
class SlotDef(Dictable):
    name: str
    type: SlotType
    entities: List[str]
    intent: List[Tuple[str, Any]]
    options: Union[None, List[Any]]
    default: Union[None, List[Tuple[str, Any]]]
    defaultQuestionCode: str
    canUsePrev: bool


@Dictable.decorator
@dataclass
class IntentDefinition(Dictable):
    type: IntentType
    name: str
    responseCodes: List[str]


@Dictable.decorator
@dataclass
class ResolveDefinition(Dictable):
    group: Union[None, str]
    slotValues: List[SlotVal]
    availableActions: List[ResolveAction]
    prohibitedActions: List[ResolveAction]


@Dictable.decorator
@dataclass
class ResponseDefinition(Dictable):
    type: ResponseType
    code: str
    appId: str
    slots: List[str]
    slotVariations: Dict[List[str], str]
    slotType: SlotType
    questionMode: QuestionMode
    relatedSlot: Union[None, str]
    slotFillValue: Union[None, Any]
    relatedIssues: Union[None, str]


def find_slot(slotDef: SlotDef, context=None, userMessage=None):
    slotName = slotDef.name
    if userMessage is not None:
        for entity_name in slotDef.entities:
            entity_val = userMessage.get_entity_val(entity_name)
            if entity_val is not None:
                return SlotVal(slotName, entity_name, entity_val, None)
        for intent, value in slotDef.intent:
            if intent in userMessage.intent.positives:
                return SlotVal(slotName, None, value, None)
    if slotDef.canUsePrev and context is not None:
        for prev_issue in (context.activeIssues + context.inactiveIssues)[::-1]:
            if slotName in prev_issue.slotValues:
                return deepcopy(prev_issue.slotValues[slotName])
        else:
            for entity_name in slotDef.entities:
                for entity in context.pastEntities[::-1]:
                    if entity.name == entity_name:
                        return SlotVal(slotName, entity_name, entity.val, None)
    return None


@Dictable.decorator
@dataclass
class IssueDefinition(Dictable):
    type: IssueType
    name: str
    slotNames: List[str]
    possibleResolves: List[ResolveDefinition]
    relatedQuestion: Union[None, str]

    def build_issue(self, slotDefs: List[SlotDef], id=None, context=None, userMessage=None):
        filled_slots = {}
        for slotDef in slotDefs:
            slot = find_slot(slotDef, context, userMessage)
            if slot is not None:
                filled_slots[slotDef.name] = slot

        return Issue(
            id=Issue.new_id() if id is None else id,
            type=self.type,
            name=self.name,
            created=datetime.now(),
            assignees=[],
            status=IssueStatus.ACTIVE,
            resolveAttempts=[],
            slotValues=filled_slots,
            expectingAnswers=[],
            activeGroup=None
        )


@Dictable.decorator
@dataclass
class EventDefinition(Dictable):
    name: str
    issue: Union[None, str]
    codes: List[str]
    onFail: str
