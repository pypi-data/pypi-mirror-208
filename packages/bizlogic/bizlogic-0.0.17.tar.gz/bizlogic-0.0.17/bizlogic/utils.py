import datetime

from ipfskvs.store import Store

import pandas as pd


class ParserType:
    """The type of protobuf object."""

    LOAN_APPLICATION = 1
    LOAN = 2
    VOUCH = 3


class TestingOnly:
    """A class to indicate that a function is for testing purposes only."""

    testing_mode: bool = False

    @classmethod
    def decorator(cls, func):  # noqa: ANN102, ANN001, ANN206
        """Indicate a function is for testing purposes only."""
        def wrapper(*args, **kwargs):  # noqa: ANN206, ANN201, ANN003, ANN002
            if not cls.testing_mode:
                raise RuntimeError(f"{func.__name__} is for testing purposes only and should not be called in production.")  # noqa: E501
            return func(*args, **kwargs)
        return wrapper


class Utils:
    """A class of utility functions."""

    @staticmethod
    def nanosecond_epoch_to_datetime(timestamp: int) -> datetime.date:
        """Convert nano seconds since epoch to date.

        Args:
            timestamp (int): Count of nanoseconds since 1970 Jan 1

        Returns:
            datetime.date: The date corresponding to the timestamp
        """
        timestamp = int(timestamp)
        seconds = timestamp // 1000000000
        nanoseconds = timestamp % 1000000000
        return datetime.datetime.fromtimestamp(
            seconds
        ) + datetime.timedelta(
            microseconds=nanoseconds // 1000
        )

    @staticmethod
    def get_most_recent(df: pd.DataFrame, group_by: str) -> pd.DataFrame:
        """Filter a CDC dataframe to get only the most recent of each object.

        Args:
            df (pd.DataFrame): The dataframe to filter
            group_by (str): The object id to group by

        Returns:
            pd.DataFrame: The filtered dataframe
        """
        # convert the "created" field to datetime format
        df['created'] = df['created'].apply(
            Utils.nanosecond_epoch_to_datetime
        )

        # group by application|loan|vouch
        # and get the row with the maximum "created" timestamp per group
        df = df.sort_values('created').groupby(
            group_by, as_index=False
        ).last()

        return df

    @staticmethod
    def parse_offer_expiry(store: Store) -> datetime.date:
        """Get the offer expiry timestamp as a datetime.

        Args:
            store (Store): The store object to parse

        Returns:
            datetime.date: The offer expiry
        """
        return datetime.datetime.fromtimestamp(
            store.reader.offer_expiry.seconds + store.reader.offer_expiry.nanos / 1e9  # noqa: E501
        )


PARSERS = {
    ParserType.LOAN_APPLICATION: {
        "amount_asking": lambda store: store.reader.amount_asking,
        "closed": lambda store: store.reader.closed,
    },
    ParserType.LOAN: {
        "principal": lambda store: store.reader.principal_amount,
        "offer_expiry": Utils.parse_offer_expiry,
        "transaction": lambda store: store.reader.transaction,
        "accepted": lambda store: store.reader.accepted,
        "payments": lambda store: len(store.reader.repayment_schedule)
    },
    ParserType.VOUCH: {}  # no content needed to parse for vouchers
}

GROUP_BY = {
    ParserType.LOAN_APPLICATION: 'application',
    ParserType.LOAN: 'loan',
    ParserType.VOUCH: 'vouch'
}
