from enum import Enum
from .utils import Dictable


class ResolveActionType(Enum):
    API = "api"
    RESPONSE = "response"

    @classmethod
    def _missing_(cls, value):
        return cls.RESPONSE


class IssueStatus(Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    FORWARDED = "forwarded"


class SlotType(Enum):
    STRING = "string"
    BOOL = "bool"
    CLASS = "class"
    NUMERIC = "numeric"
    DATE = "date"
    API = "api"
    ANY = "any"


class CreatorType(Enum):
    BOT = "bot"
    HUMAN = "human"


class IssueType(Enum):
    COMPLAINT = "complaint"
    INFO = "info"
    PROBLEM = "problem"
    OTHER = "other"


class IntentType(Enum):
    ISSUE = "issue"
    DEFINITE = "definite"
    INDEFINITE = "indefinite"
    OPERATOR = "operator"


class ResponseType(Enum):
    STRING = "question"
    BOOL = "text"


class QuestionMode(Enum):
    ISSUE_CREATE = "issueCreate"
    ISSUE_CLOSE = "issueClose"
    SLOT = "slot"
    SLOT_FILL = "slotFill"
    VARIABLE = "variable"


class ContextOperationType(Enum):
    REMOVE_NOTIFICATION = "removeNotification"
    ADD_NOTIFICATION = "addNotification"
    REMOVE_QUESTION = "removeQuestion"
    ADD_QUESTION = "addQuestion"
    CREATE_ISSUE = "createIssue"
    CREATE_SLOT = "createSlot"
    REMOVE_SLOT = "removeSlot"
    REMOVE_EMAIL = "removeEmail"
    ADD_EMAIL = "addEmail"
    REMOVE_PHONE = "removePhone"
    ADD_PHONE = "addPhone"
    REGISTER_USER_ID = "registerUserId"
    CREATE_RESOLVE = "createResolve"
    UPDATE_ISSUE_STATUS = "updateIssueStatus"
    ADD_ASSIGNEE = "addAssignee"
    REMOVE_ASSIGNEE = "removeAssignee"
    UPDATE_SLOT_VALUE = "updateSlotValue"
    UPDATE_SLOT_DEFAULT_VALUE = "updateSlotDefaultValue"
    UPDATE_RESOLVE = "updateResolve"


class ContextOperation(Dictable):
    def __init__(self, type: ContextOperationType, **kwargs):
        self.type = type
        self.args = kwargs

    def get(self, name):
        return self.args[name]

    def has(self, name):
        return name in self.args

    def __repr__(self):
        return f"Context Operation: {self.type}\n\t" + str(self.args)

    @classmethod
    def list_diff(cls, list_a, list_b, not_in_b, not_in_a, elem, **kwargs):
        ops = []
        for elem_a in list_a:
            if elem_a not in list_b:
                kwargs[elem] = elem_a
                ops.append(cls(not_in_b, **kwargs))
        for elem_b in list_b:
            if elem_b not in list_a:
                kwargs[elem] = elem_b
                ops.append(cls(not_in_a, **kwargs))
        return ops

    @classmethod
    def dict_diff(cls, dict_a, dict_b, not_in_b, not_in_a, elem, **kwargs):
        ops = []
        for key_a, val_a in dict_a.items():
            if key_a not in dict_b:
                kwargs[elem] = val_a
                ops.append(cls(not_in_b, **kwargs))
            else:
                ops += val_a.diff(dict_b[key_a], **kwargs)
        for key_b, val_b in dict_b.items():
            if key_b not in dict_a:
                kwargs[elem] = val_b
                ops.append(cls(not_in_a, **kwargs))
        return ops
