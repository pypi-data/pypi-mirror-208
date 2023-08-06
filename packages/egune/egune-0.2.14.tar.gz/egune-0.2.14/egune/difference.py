from typing import List, Union
from copy import deepcopy

from .utils import Dictable
from .enumerators import ContextOperationType, IssueStatus
from .dataclasses import (
    ResolveAttempt, SlotVal, Issue, UserSignature, Context, UserMessage
)


class Operation(Dictable):
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
                _kwargs = deepcopy(kwargs)
                _kwargs[elem] = val_a
                ops.append(cls(not_in_b, **_kwargs))
            else:
                ops += diff(val_a, dict_b[key_a], **kwargs)
        for key_b, val_b in dict_b.items():
            if key_b not in dict_a:
                _kwargs = deepcopy(kwargs)
                _kwargs[elem] = val_b
                ops.append(cls(not_in_a, **_kwargs))
        return ops


def diff(a, b, **kwargs) -> List[Operation]:
    def get_issue_id(issue):
        if kwargs.get("test", False):
            return issue.name
        else:
            return issue.id
    if isinstance(a, ResolveAttempt):
        ops = []
        if a.accepted != b.accepted:
            ops.append(
                Operation(
                    ContextOperationType.UPDATE_RESOLVE,
                    issueId=kwargs["issueId"],
                    resolveId=a.id,
                    accepted=b.accepted,
                )
            )
        return ops
    elif isinstance(a, SlotVal):
        ops = []
        if a.value != b.value:
            ops.append(
                Operation(
                    ContextOperationType.UPDATE_SLOT_VALUE,
                    slot=a.name,
                    value=b.value,
                    issueId=kwargs["issueId"],
                )
            )
        if a.default != b.default:
            ops.append(
                Operation(
                    ContextOperationType.UPDATE_SLOT_DEFAULT_VALUE,
                    slot=a.name,
                    value=b.default,
                    issueId=kwargs["issueId"],
                )
            )
        return ops
    if isinstance(a, Issue):
        ops = []
        ops += Operation.list_diff(
            a.assignees,
            b.assignees,
            ContextOperationType.ADD_ASSIGNEE,
            ContextOperationType.REMOVE_ASSIGNEE,
            "assignee",
        )
        if a.status != b.status:
            ops.append(
                Operation(
                    ContextOperationType.UPDATE_ISSUE_STATUS,
                    issueId=a.id,
                    status=b.status,
                )
            )

        for other_resolve in b.resolveAttempts:
            for my_resolve in a.resolveAttempts:
                if my_resolve.is_equal(other_resolve):
                    break
            else:
                ops.append(
                    Operation(
                        ContextOperationType.CREATE_RESOLVE,
                        resolve=other_resolve,
                        issueId=a.id,
                    )
                )
        for resolve in a.resolveAttempts:
            for other_resolve in b.resolveAttempts:
                if resolve.id == other_resolve.id:
                    ops += diff(resolve, other_resolve, issueId=a.id)
                    break
            else:
                if not kwargs["silent"]:
                    raise ValueError(
                        "Resolve not found in new context",
                        {
                            "resolve": resolve.to_dict(),
                            "current": a.to_dict(),
                            "next": b.to_dict(),
                        },
                    )

        ops += Operation.dict_diff(
            a.slotValues,
            b.slotValues,
            ContextOperationType.REMOVE_SLOT,
            ContextOperationType.CREATE_SLOT,
            "slot",
            issueId=a.id,
        )
        ops.extend(
            Operation.list_diff(
                a.expectingAnswers,
                b.expectingAnswers,
                ContextOperationType.REMOVE_QUESTION,
                ContextOperationType.ADD_QUESTION,
                "question",
                issueId=a.id,
            )
        )
        return ops
    if isinstance(b, UserSignature):
        ops = []
        if a.userId is None and b.userId is not None:
            ops.append(
                Operation(
                    ContextOperationType.REGISTER_USER_ID, userId=b.userId
                )
            )
        elif a.userId != b.userId:
            raise ValueError(
                "User ids does not match",
                {"current user id": a.userId, "new user id": b.userId},
            )
        ops.extend(
            Operation.list_diff(
                a.email,
                b.email,
                ContextOperationType.REMOVE_EMAIL,
                ContextOperationType.ADD_EMAIL,
                "email",
            )
        )
        ops.extend(
            Operation.list_diff(
                a.phone,
                b.phone,
                ContextOperationType.REMOVE_PHONE,
                ContextOperationType.ADD_PHONE,
                "phone",
            )
        )
        return ops
    if isinstance(b, Context):
        ops = []
        ops += diff(a.userSignature, b.userSignature)

        ops += Operation.dict_diff(
            a.variables,
            b.variables,
            ContextOperationType.REMOVE_SLOT,
            ContextOperationType.CREATE_SLOT,
            "slot",
            issueId=None,
        )

        active_issue_ids = [get_issue_id(i) for i in a.activeIssues]
        for other_issue in b.activeIssues:
            if get_issue_id(other_issue) not in active_issue_ids:
                ops.append(
                    Operation(
                        ContextOperationType.CREATE_ISSUE, issue=other_issue
                    )
                )
                ops += diff(Issue.from_dict({
                    "name": other_issue.name,
                    "id": other_issue.id,
                    "type": other_issue.type.value,
                    "status": other_issue.status.value
                }), other_issue)
        for issue in a.activeIssues:
            for other_issue in b.activeIssues:
                if get_issue_id(issue) == get_issue_id(other_issue):
                    ops += diff(issue, other_issue)
                    break
            else:
                for other_issue in b.inactiveIssues:
                    if get_issue_id(issue) == get_issue_id(other_issue):
                        ops += diff(issue, other_issue)
                        break
                else:
                    raise ValueError(
                        "Issue not found in new context",
                        {
                            "issue": issue.id,
                            "current": a.to_dict(),
                            "next": b.to_dict(),
                        },
                    )
        ops.extend(
            Operation.list_diff(
                a.impendingQuestions,
                b.impendingQuestions,
                ContextOperationType.REMOVE_QUESTION,
                ContextOperationType.ADD_QUESTION,
                "question",
                issueId=None,
            )
        )
        ops.extend(
            Operation.list_diff(
                a.impendingNotifications,
                b.impendingNotifications,
                ContextOperationType.REMOVE_NOTIFICATION,
                ContextOperationType.ADD_NOTIFICATION,
                "notification",
            )
        )
        return ops
    else:
        raise TypeError("Invalid Type For Difference Calculation", a, b)


def apply(a: Context, ops: List[Operation], msg: Union[None, UserMessage] = None):
    def _is(type):
        return op.type == type

    for op in ops:
        if _is(ContextOperationType.REMOVE_NOTIFICATION):
            a.impendingNotifications.remove(op.get("notification"))
        elif _is(ContextOperationType.ADD_NOTIFICATION):
            a.impendingNotifications.append(op.get("notification"))
        elif _is(ContextOperationType.REMOVE_QUESTION):
            if op.get("issueId") is None:
                for q in a.impendingQuestions:
                    if q.code == op.get("question").code:
                        a.impendingQuestions.remove(q)
            else:
                issue = a.get_issue(op.get("issueId"))
                if issue is not None:
                    issue.expectingAnswers.remove(op.get("question"))
        elif _is(ContextOperationType.ADD_QUESTION):
            if op.get("issueId") is None:
                a.impendingQuestions.append(op.get("question"))
            else:
                issue = a.get_issue(op.get("issueId"))
                if issue is not None:
                    issue.expectingAnswers.append(op.get("question"))
        elif _is(ContextOperationType.CREATE_ISSUE):
            a.activeIssues.append(op.get("issue"))
        elif _is(ContextOperationType.CREATE_SLOT):
            slot: SlotVal = op.get("slot")
            if msg is not None:
                slot.update_value(msg)
            if op.get("issueId") is None:
                a.variables[op.get("slot").name] = op.get("slot")
            else:
                issue = a.get_issue(op.get("issueId"))
                if issue is not None:
                    issue.slotValues[op.get("slot").name] = op.get("slot")
        elif _is(ContextOperationType.REMOVE_SLOT):
            if op.get("issueId") is None:
                del a.variables[op.get("slot").name]
            else:
                issue = a.get_issue(op.get("issueId"))
                if issue is not None:
                    del issue.slotValues[op.get("slot").name]
        elif _is(ContextOperationType.REMOVE_EMAIL):
            a.userSignature.email.remove(op.get("email"))
        elif _is(ContextOperationType.ADD_EMAIL):
            a.userSignature.email.append(op.get("email"))
        elif _is(ContextOperationType.REMOVE_PHONE):
            a.userSignature.phone.remove(op.get("phone"))
        elif _is(ContextOperationType.ADD_PHONE):
            a.userSignature.phone.append(op.get("phone"))
        elif _is(ContextOperationType.REGISTER_USER_ID):
            a.userSignature.userId = op.get("userId")
        elif _is(ContextOperationType.CREATE_RESOLVE):
            issue = a.get_issue(op.get("issueId"))
            if issue is not None:
                issue.resolveAttempts.append(op.get("resolve"))
        elif _is(ContextOperationType.UPDATE_ISSUE_STATUS):
            issue = a.get_issue(op.get("issueId"))
            if issue is not None:
                prev = issue.status
                new = op.get("status")
                issue.status = new
                if prev == IssueStatus.ACTIVE and new != IssueStatus.ACTIVE:
                    a.activeIssues.remove(issue)
                    a.inactiveIssues.append(issue)
                elif prev != IssueStatus.ACTIVE and new == IssueStatus.ACTIVE:
                    a.activeIssues.append(issue)
                    a.inactiveIssues.remove(issue)
        elif _is(ContextOperationType.ADD_ASSIGNEE):
            issue = a.get_issue(op.get("issueId"))
            if issue is not None:
                issue.assignees.append(op.get("assignee"))
        elif _is(ContextOperationType.ADD_ASSIGNEE):
            issue = a.get_issue(op.get("issueId"))
            if issue is not None:
                issue.assignees.remove(op.get("assignee"))
        elif _is(ContextOperationType.UPDATE_RESOLVE):
            resolve = a.get_resolve(op.get("resolveId"))
            if resolve is not None:
                resolve.accepted = op.get("accepted")
        elif _is(ContextOperationType.UPDATE_SLOT_VALUE):
            slotName = op.get("slot")
            issueId = op.get("issueId")
            if issueId is None:
                a.variables[slotName].value = op.get("value")
                if msg is not None:
                    a.variables[slotName].update_value(msg)
                a.variables[slotName].value = op.get("value")
            else:
                for issue in a.activeIssues + a.inactiveIssues:
                    if issue.id == issueId:
                        issue.slotValues[slotName].value = op.get("value")
                        if msg is not None:
                            issue.slotValues[slotName].update_value(msg)
        elif _is(ContextOperationType.UPDATE_SLOT_DEFAULT_VALUE):
            slotName = op.get("slot")
            issueId = op.get("issueId")
            if issueId is None:
                a.variables[slotName].default = op.get("value")
            else:
                for issue in a.activeIssues + a.inactiveIssues:
                    if issue.id == issueId:
                        issue.slotValues[slotName].default = op.get(
                            "value")
                        break
        else:
            print(op.type)
            raise TypeError
    return a
