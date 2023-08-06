
from typing import Self

from bizlogic.loan import PREFIX
from bizlogic.loan.status import LoanStatus, LoanStatusType
from bizlogic.protoc.loan_pb2 import Loan
from bizlogic.utils import GROUP_BY, PARSERS, ParserType, Utils

from ipfsclient.ipfs import Ipfs

from ipfskvs.index import Index
from ipfskvs.store import Store

import pandas as pd


class LoanReader():
    """Loan Reader."""

    ipfsclient: Ipfs

    def __init__(self: Self, ipfsclient: Ipfs) -> None:
        """Create a Loan Reader."""
        self.ipfsclient = ipfsclient

    def get_open_loan_offers(
            self: Self,
            borrower: str,
            recent_only: bool = True) -> pd.DataFrame:
        """Get all open loan offers for a borrower.

        Args:
            borrower (str): The borrower to get open loan offers for.
            recent_only (bool, optional): Include previous updates or
                only get the most recent. Defaults to True.

        Returns:
            pd.DataFrame: The open loan offers for the borrower.
        """
        return self.query_for_status(
            status=LoanStatus.PENDING_ACCEPTANCE,
            index=Index(
                prefix=PREFIX,
                index={
                    "borrower": borrower
                },
                size=3
            ),
            recent_only=recent_only
        )

    def query_for_status(
            self: Self,
            status: LoanStatusType,
            index: dict = {},
            recent_only: bool = True) -> pd.DataFrame:
        """Query for loans with a specific status.  # noqa: D411, D415

        Args:
            status (LoanStatusType): The status to query for.
            index (dict, optional): Additional search/filter options,
                ex {"borrower": 123}. Defaults to {}.
            recent_only (bool, optional): Include previous updates or
                only get the most recent. Defaults to True.
        Returns:
            pd.DataFrame: The loans with the specified status.
        """
        # get all applications from ipfs
        loans = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index=index
            ),
            ipfs=self.ipfsclient,
            reader=Loan()
        )

        # parse results into a dataframe
        df = Store.to_dataframe(loans, PARSERS[ParserType.LOAN])

        # filter for unexpired and unaccepted loans
        df = df[df['loan_status'] == status]

        # filter for most recent applications per loan_id
        if recent_only:
            df = Utils.get_most_recent(df, GROUP_BY[ParserType.LOAN])

        return df

    def query_for_borrower(
            self: Self,
            borrower: str,
            recent_only: bool = True) -> pd.DataFrame:
        """Query for loans with a specific borrower.

        Args:
            borrower (str): The borrower to query for.
            recent_only (bool, optional): Include previous updates or
                only get the most recent. Defaults to True.

        Returns:
            pd.DataFrame: The loans with the specified borrower.
        """
        # fetch the loan data from ipfs
        loans = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={
                    "borrower": borrower
                },
                size=3
            ),
            ipfs=self.ipfsclient,
            reader=Loan()
        )

        # parse results into a dataframe
        df = Store.to_dataframe(loans, PARSERS[ParserType.LOAN])

        # filter for most recent applications per loan_id
        if recent_only:
            df = Utils.get_most_recent(df, GROUP_BY[ParserType.LOAN])

        return df

    def query_for_lender(
            self: Self,
            lender: str,
            recent_only: bool = True) -> pd.DataFrame:
        """Query for loans with a specific lender.

        Args:
            lender (str): The lender to query for.
            recent_only (bool, optional): Include previous updates or
                only get the most recent. Defaults to True.

        Returns:
            pd.DataFrame: The loans with the specified lender.
        """
        loans = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={
                    "lender": lender
                },
                size=3
            ),
            ipfs=self.ipfsclient,
            reader=Loan()
        )

        # parse results into a dataframe
        df = Store.to_dataframe(loans, PARSERS[ParserType.LOAN])

        # filter for most recent applications per loan_id
        if recent_only:
            df = Utils.get_most_recent(df, GROUP_BY[ParserType.LOAN])

        return df

    def query_for_loan(
            self: Self,
            loan_id: str,
            recent_only: bool = True) -> pd.DataFrame:
        """Query for a specific loan.

        Args:
            loan_id (str): The loan to query for.
            recent_only (bool, optional): Include previous updates or
                only get the most recent. Defaults to True.

        Returns:
            pd.DataFrame: The loan with the specified id.
        """
        loans = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={
                    "loan": loan_id
                },
                size=3
            ),
            ipfs=self.ipfsclient,
            reader=Loan()
        )

        # parse results into a dataframe
        df = Store.to_dataframe(loans, PARSERS[ParserType.LOAN])

        # filter for most recent applications per loan_id
        if recent_only:
            df = Utils.get_most_recent(df, GROUP_BY[ParserType.LOAN])

        return df
