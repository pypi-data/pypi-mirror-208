from typing import Union

from paloma_sdk.core.distribution.proposals import CommunityPoolSpendProposal
from paloma_sdk.core.gov.proposals import TextProposal
from paloma_sdk.core.ibc.proposals import ClientUpdateProposal
from paloma_sdk.core.params.proposals import ParameterChangeProposal
from paloma_sdk.core.upgrade import (CancelSoftwareUpgradeProposal,
                                     SoftwareUpgradeProposal)

from .base import create_demux, create_demux_proto, create_demux_unpack_any

Content = Union[
    TextProposal,
    CommunityPoolSpendProposal,
    ParameterChangeProposal,
    SoftwareUpgradeProposal,
    CancelSoftwareUpgradeProposal,
    ClientUpdateProposal,
]

parse_content = create_demux(
    [
        CommunityPoolSpendProposal,
        TextProposal,
        ParameterChangeProposal,
        SoftwareUpgradeProposal,
        CancelSoftwareUpgradeProposal,
        ClientUpdateProposal,
    ]
)

parse_content_proto = create_demux_proto(
    [
        CommunityPoolSpendProposal,
        TextProposal,
        ParameterChangeProposal,
        SoftwareUpgradeProposal,
        CancelSoftwareUpgradeProposal,
        ClientUpdateProposal,
    ]
)

parse_content_unpack_any = create_demux_unpack_any(
    [
        CommunityPoolSpendProposal,
        TextProposal,
        ParameterChangeProposal,
        SoftwareUpgradeProposal,
        CancelSoftwareUpgradeProposal,
        ClientUpdateProposal,
    ]
)

"""
parse_content_proto = create_demux_proto(
    [
        [CommunityPoolSpendProposal.type_url, CommunityPoolSpendProposal_pb],
        [TextProposal.type_url, TextProposal_pb],
        [ParameterChangeProposal.type_url, ParameterChangeProposal_pb],
        [SoftwareUpgradeProposal.type_url, SoftwareUpgradeProposal_pb],
        [CancelSoftwareUpgradeProposal.type_url, CancelSoftwareUpgradeProposal_pb],
        [ClientUpdateProposal.type_url, ClientUpdateProposal_pb]
    ]
)
"""
