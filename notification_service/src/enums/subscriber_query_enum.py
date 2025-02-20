# stdlib
from enum import Enum

# project
from services.subscriber_resolver import SubscriberResolver

# Динамический Enum, обновляемый на основе зарегистрированных fetcher-ов.
SubscriberQueryEnum = Enum(  # type: ignore
    "SubscriberQueryEnum",
    {key: key for key in SubscriberResolver._fetchers.keys()},
)
