from datetime import datetime, timedelta
from enum import Enum

from bizlogic.protoc.loan_pb2 import Loan

from google.protobuf.timestamp_pb2 import Timestamp


class LoanStatusType(Enum):
    """Loan Status Type."""

    PENDING_ACCEPTANCE = 1
    EXPIRED_UNACCEPTED = 2
    ACCEPTED = 3


class LoanStatus():
    """Loan Status."""

    @staticmethod
    def _timestamp_to_datetime(timestamp: Timestamp) -> datetime:
        """Convert a protobuf timestamp to a datetime.

        Args:
            timestamp: the timestamp

        Returns:
            datetime: the datetime
        """
        seconds = datetime.fromtimestamp(timestamp.seconds)
        micros = timedelta(microseconds=timestamp.nanos / 1000)
        return seconds + micros

    @staticmethod
    def loan_status(loan: Loan) -> LoanStatusType:
        """Get the status of a loan.

        Args:
            loan: the loan

        Returns:
            LoanStatusType: the status of the loan
        """
        now = datetime.now()
        expiry = LoanStatus._timestamp_to_datetime(loan.offer_expiry)

        if expiry <= now and not loan.accepted:
            return LoanStatusType.PENDING_ACCEPTANCE

        elif expiry > now and not loan.accepted:
            return LoanStatusType.EXPIRED_UNACCEPTED

        elif expiry <= now and loan.accepted:
            return LoanStatusType.ACCEPTED

        elif expiry > now and loan.accepted:
            return LoanStatusType.ACCEPTED

        raise
