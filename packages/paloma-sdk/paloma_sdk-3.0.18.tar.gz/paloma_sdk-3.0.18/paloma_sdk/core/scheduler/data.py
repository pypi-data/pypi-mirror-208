from dataclasses import dataclass
from typing import List

import betterproto


@dataclass(eq=False, repr=False)
class ScheduleTrigger(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class EventTrigger(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class Trigger(betterproto.Message):
    schedule: "ScheduleTrigger" = betterproto.message_field(1, group="trigger")
    event: "EventTrigger" = betterproto.message_field(2, group="trigger")


@dataclass(eq=False, repr=False)
class Runner(betterproto.Message):
    chain_type: str = betterproto.string_field(1)
    chain_reference_id: str = betterproto.string_field(2)
    address: bytes = betterproto.bytes_field(3)


@dataclass(eq=False, repr=False)
class Permissions(betterproto.Message):
    whitelist: List["Runner"] = betterproto.message_field(1)
    blacklist: List["Runner"] = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class Routing(betterproto.Message):
    chain_type: str = betterproto.string_field(1)
    chain_reference_id: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class Job(betterproto.Message):
    id: str = betterproto.string_field(1)
    owner: bytes = betterproto.bytes_field(2)
    routing: "Routing" = betterproto.message_field(3)
    definition: bytes = betterproto.bytes_field(5)
    payload: bytes = betterproto.bytes_field(6)
    is_payload_modifiable: bool = betterproto.bool_field(7)
    permissions: "Permissions" = betterproto.message_field(8)
    triggers: List["Trigger"] = betterproto.message_field(9)
    address: bytes = betterproto.bytes_field(10)


@dataclass(eq=False, repr=False)
class MsgCreateJob(betterproto.Message):
    creator: str = betterproto.string_field(1)
    job: "Job" = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class MsgExecuteJob(betterproto.Message):
    creator: str = betterproto.string_field(1)
    job_id: str = betterproto.string_field(2)
    payload: bytes = betterproto.bytes_field(3)
