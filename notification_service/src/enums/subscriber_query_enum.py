# stdlib
from enum import Enum

# project
from services.subscriber_resolver import SubscriberResolver

SubscriberQueryEnum = Enum(  # type: ignore
    "SubscriberQueryEnum",
    {fetcher: fetcher for fetcher in SubscriberResolver._fetchers},
    type=str,
)
