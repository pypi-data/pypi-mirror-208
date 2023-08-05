"""
Type annotations for ivs-realtime service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivs_realtime/type_defs/)

Usage::

    ```python
    from mypy_boto3_ivs_realtime.type_defs import CreateParticipantTokenRequestRequestTypeDef

    data: CreateParticipantTokenRequestRequestTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import EventNameType, ParticipantStateType, ParticipantTokenCapabilityType

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "CreateParticipantTokenRequestRequestTypeDef",
    "ParticipantTokenTypeDef",
    "ParticipantTokenConfigurationTypeDef",
    "StageTypeDef",
    "DeleteStageRequestRequestTypeDef",
    "DisconnectParticipantRequestRequestTypeDef",
    "EventTypeDef",
    "GetParticipantRequestRequestTypeDef",
    "ParticipantTypeDef",
    "GetStageRequestRequestTypeDef",
    "GetStageSessionRequestRequestTypeDef",
    "StageSessionTypeDef",
    "ListParticipantEventsRequestRequestTypeDef",
    "ListParticipantsRequestRequestTypeDef",
    "ParticipantSummaryTypeDef",
    "ListStageSessionsRequestRequestTypeDef",
    "StageSessionSummaryTypeDef",
    "ListStagesRequestRequestTypeDef",
    "StageSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "ResponseMetadataTypeDef",
    "TagResourceRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateStageRequestRequestTypeDef",
    "CreateParticipantTokenResponseTypeDef",
    "CreateStageRequestRequestTypeDef",
    "CreateStageResponseTypeDef",
    "GetStageResponseTypeDef",
    "UpdateStageResponseTypeDef",
    "ListParticipantEventsResponseTypeDef",
    "GetParticipantResponseTypeDef",
    "GetStageSessionResponseTypeDef",
    "ListParticipantsResponseTypeDef",
    "ListStageSessionsResponseTypeDef",
    "ListStagesResponseTypeDef",
)

_RequiredCreateParticipantTokenRequestRequestTypeDef = TypedDict(
    "_RequiredCreateParticipantTokenRequestRequestTypeDef",
    {
        "stageArn": str,
    },
)
_OptionalCreateParticipantTokenRequestRequestTypeDef = TypedDict(
    "_OptionalCreateParticipantTokenRequestRequestTypeDef",
    {
        "attributes": Mapping[str, str],
        "capabilities": Sequence[ParticipantTokenCapabilityType],
        "duration": int,
        "userId": str,
    },
    total=False,
)


class CreateParticipantTokenRequestRequestTypeDef(
    _RequiredCreateParticipantTokenRequestRequestTypeDef,
    _OptionalCreateParticipantTokenRequestRequestTypeDef,
):
    pass


ParticipantTokenTypeDef = TypedDict(
    "ParticipantTokenTypeDef",
    {
        "attributes": Dict[str, str],
        "capabilities": List[ParticipantTokenCapabilityType],
        "duration": int,
        "expirationTime": datetime,
        "participantId": str,
        "token": str,
        "userId": str,
    },
    total=False,
)

ParticipantTokenConfigurationTypeDef = TypedDict(
    "ParticipantTokenConfigurationTypeDef",
    {
        "attributes": Mapping[str, str],
        "capabilities": Sequence[ParticipantTokenCapabilityType],
        "duration": int,
        "userId": str,
    },
    total=False,
)

_RequiredStageTypeDef = TypedDict(
    "_RequiredStageTypeDef",
    {
        "arn": str,
    },
)
_OptionalStageTypeDef = TypedDict(
    "_OptionalStageTypeDef",
    {
        "activeSessionId": str,
        "name": str,
        "tags": Dict[str, str],
    },
    total=False,
)


class StageTypeDef(_RequiredStageTypeDef, _OptionalStageTypeDef):
    pass


DeleteStageRequestRequestTypeDef = TypedDict(
    "DeleteStageRequestRequestTypeDef",
    {
        "arn": str,
    },
)

_RequiredDisconnectParticipantRequestRequestTypeDef = TypedDict(
    "_RequiredDisconnectParticipantRequestRequestTypeDef",
    {
        "participantId": str,
        "stageArn": str,
    },
)
_OptionalDisconnectParticipantRequestRequestTypeDef = TypedDict(
    "_OptionalDisconnectParticipantRequestRequestTypeDef",
    {
        "reason": str,
    },
    total=False,
)


class DisconnectParticipantRequestRequestTypeDef(
    _RequiredDisconnectParticipantRequestRequestTypeDef,
    _OptionalDisconnectParticipantRequestRequestTypeDef,
):
    pass


EventTypeDef = TypedDict(
    "EventTypeDef",
    {
        "errorCode": Literal["INSUFFICIENT_CAPABILITIES"],
        "eventTime": datetime,
        "name": EventNameType,
        "participantId": str,
        "remoteParticipantId": str,
    },
    total=False,
)

GetParticipantRequestRequestTypeDef = TypedDict(
    "GetParticipantRequestRequestTypeDef",
    {
        "participantId": str,
        "sessionId": str,
        "stageArn": str,
    },
)

ParticipantTypeDef = TypedDict(
    "ParticipantTypeDef",
    {
        "attributes": Dict[str, str],
        "firstJoinTime": datetime,
        "participantId": str,
        "published": bool,
        "state": ParticipantStateType,
        "userId": str,
    },
    total=False,
)

GetStageRequestRequestTypeDef = TypedDict(
    "GetStageRequestRequestTypeDef",
    {
        "arn": str,
    },
)

GetStageSessionRequestRequestTypeDef = TypedDict(
    "GetStageSessionRequestRequestTypeDef",
    {
        "sessionId": str,
        "stageArn": str,
    },
)

StageSessionTypeDef = TypedDict(
    "StageSessionTypeDef",
    {
        "endTime": datetime,
        "sessionId": str,
        "startTime": datetime,
    },
    total=False,
)

_RequiredListParticipantEventsRequestRequestTypeDef = TypedDict(
    "_RequiredListParticipantEventsRequestRequestTypeDef",
    {
        "participantId": str,
        "sessionId": str,
        "stageArn": str,
    },
)
_OptionalListParticipantEventsRequestRequestTypeDef = TypedDict(
    "_OptionalListParticipantEventsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)


class ListParticipantEventsRequestRequestTypeDef(
    _RequiredListParticipantEventsRequestRequestTypeDef,
    _OptionalListParticipantEventsRequestRequestTypeDef,
):
    pass


_RequiredListParticipantsRequestRequestTypeDef = TypedDict(
    "_RequiredListParticipantsRequestRequestTypeDef",
    {
        "sessionId": str,
        "stageArn": str,
    },
)
_OptionalListParticipantsRequestRequestTypeDef = TypedDict(
    "_OptionalListParticipantsRequestRequestTypeDef",
    {
        "filterByPublished": bool,
        "filterByState": ParticipantStateType,
        "filterByUserId": str,
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)


class ListParticipantsRequestRequestTypeDef(
    _RequiredListParticipantsRequestRequestTypeDef, _OptionalListParticipantsRequestRequestTypeDef
):
    pass


ParticipantSummaryTypeDef = TypedDict(
    "ParticipantSummaryTypeDef",
    {
        "firstJoinTime": datetime,
        "participantId": str,
        "published": bool,
        "state": ParticipantStateType,
        "userId": str,
    },
    total=False,
)

_RequiredListStageSessionsRequestRequestTypeDef = TypedDict(
    "_RequiredListStageSessionsRequestRequestTypeDef",
    {
        "stageArn": str,
    },
)
_OptionalListStageSessionsRequestRequestTypeDef = TypedDict(
    "_OptionalListStageSessionsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)


class ListStageSessionsRequestRequestTypeDef(
    _RequiredListStageSessionsRequestRequestTypeDef, _OptionalListStageSessionsRequestRequestTypeDef
):
    pass


StageSessionSummaryTypeDef = TypedDict(
    "StageSessionSummaryTypeDef",
    {
        "endTime": datetime,
        "sessionId": str,
        "startTime": datetime,
    },
    total=False,
)

ListStagesRequestRequestTypeDef = TypedDict(
    "ListStagesRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)

_RequiredStageSummaryTypeDef = TypedDict(
    "_RequiredStageSummaryTypeDef",
    {
        "arn": str,
    },
)
_OptionalStageSummaryTypeDef = TypedDict(
    "_OptionalStageSummaryTypeDef",
    {
        "activeSessionId": str,
        "name": str,
        "tags": Dict[str, str],
    },
    total=False,
)


class StageSummaryTypeDef(_RequiredStageSummaryTypeDef, _OptionalStageSummaryTypeDef):
    pass


ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)

_RequiredUpdateStageRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateStageRequestRequestTypeDef",
    {
        "arn": str,
    },
)
_OptionalUpdateStageRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateStageRequestRequestTypeDef",
    {
        "name": str,
    },
    total=False,
)


class UpdateStageRequestRequestTypeDef(
    _RequiredUpdateStageRequestRequestTypeDef, _OptionalUpdateStageRequestRequestTypeDef
):
    pass


CreateParticipantTokenResponseTypeDef = TypedDict(
    "CreateParticipantTokenResponseTypeDef",
    {
        "participantToken": ParticipantTokenTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

CreateStageRequestRequestTypeDef = TypedDict(
    "CreateStageRequestRequestTypeDef",
    {
        "name": str,
        "participantTokenConfigurations": Sequence[ParticipantTokenConfigurationTypeDef],
        "tags": Mapping[str, str],
    },
    total=False,
)

CreateStageResponseTypeDef = TypedDict(
    "CreateStageResponseTypeDef",
    {
        "participantTokens": List[ParticipantTokenTypeDef],
        "stage": StageTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetStageResponseTypeDef = TypedDict(
    "GetStageResponseTypeDef",
    {
        "stage": StageTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

UpdateStageResponseTypeDef = TypedDict(
    "UpdateStageResponseTypeDef",
    {
        "stage": StageTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListParticipantEventsResponseTypeDef = TypedDict(
    "ListParticipantEventsResponseTypeDef",
    {
        "events": List[EventTypeDef],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetParticipantResponseTypeDef = TypedDict(
    "GetParticipantResponseTypeDef",
    {
        "participant": ParticipantTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetStageSessionResponseTypeDef = TypedDict(
    "GetStageSessionResponseTypeDef",
    {
        "stageSession": StageSessionTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListParticipantsResponseTypeDef = TypedDict(
    "ListParticipantsResponseTypeDef",
    {
        "nextToken": str,
        "participants": List[ParticipantSummaryTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListStageSessionsResponseTypeDef = TypedDict(
    "ListStageSessionsResponseTypeDef",
    {
        "nextToken": str,
        "stageSessions": List[StageSessionSummaryTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListStagesResponseTypeDef = TypedDict(
    "ListStagesResponseTypeDef",
    {
        "nextToken": str,
        "stages": List[StageSummaryTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)
