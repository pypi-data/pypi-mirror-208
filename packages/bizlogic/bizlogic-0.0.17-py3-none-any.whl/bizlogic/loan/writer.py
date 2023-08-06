
import datetime
import time
import uuid
from typing import List, Self

from bizlogic.loan import PREFIX
from bizlogic.protoc.loan_pb2 import Loan, LoanPayment

from google.protobuf.timestamp_pb2 import Timestamp

from ipfsclient.ipfs import Ipfs

from ipfskvs.index import Index
from ipfskvs.store import Store


class LoanWriter():
    """Loan Writer.

    ipfs filename:
        loan/borrower_<id>.lender_<id>.loan_<id>/created_<timestamp>
    """

    loan_id: str
    borrower: str
    lender: str
    index: Index
    data: Loan
    ipfsclient: Ipfs

    def __init__(
            self: Self,
            ipfs: Ipfs,
            borrower: str,
            lender: str,
            principal_amount: int,
            repayment_schedule: List[LoanPayment],
            offer_expiry: datetime.date) -> None:
        """Construct a new unaccepted loan and write it.

        The loan is not accepted until the borrower signs it.

        Args:
            ipfs: the ipfs client
            borrower: the borrower id
            lender: the lender id
            principal_amount: the principal amount of the loan
            repayment_schedule: the repayment schedule of the loan
            offer_expiry: the expiry date of the loan offer
        """
        self.loan_id = str(uuid.uuid4())
        self.borrower = borrower
        self.lender = lender
        self.ipfsclient = ipfs
        timestamp = Timestamp()
        timestamp.FromDatetime(offer_expiry)
        self.data = Loan(
            principal_amount=principal_amount,
            repayment_schedule=repayment_schedule,
            offer_expiry=timestamp,
            accepted=False
        )

    @staticmethod
    def from_data(ipfs: Ipfs, data: Store) -> Self:
        """Construct a loan from data.

        Args:
            ipfs: the ipfs client
            data: the data to construct the loan from

        Returns:
            LoanWriter: the constructed loan
        """
        return LoanWriter(
            ipfs=ipfs,
            borrower=data.index["borrower"],
            lender=data.index["lender"],
            principal_amount=data.reader.principal_amount,
            repayment_schedule=data.reader.repayment_schedule,
            offer_expiry=data.reader.offer_expiry
        )

    def write(self: Self) -> None:
        """Write the loan to IPFS."""
        self._generate_index()

        store = Store(
            index=self.index,
            ipfs=self.ipfsclient,
            writer=self.data
        )

        store.add()

    def _generate_index(self: Self) -> None:
        """Generate the index for the loan."""
        self.index = Index(
            prefix=PREFIX,
            index={
                "borrower": self.borrower,
                "lender": self.lender,
                "loan": self.loan_id
            },
            subindex=Index(
                index={
                    "created": str(time.time_ns())
                }
            )
        )

    def accept_terms(self: Self) -> None:
        """Accept the loan terms."""
        self.data = Loan(
            principal_amount=self.data.principal_amount,
            repayment_schedule=self.data.repayment_schedule,
            offer_expiry=self.data.offer_expiry,
            accepted=True
        )

    def register_payment(
            self: Self,
            payment_id: str,
            transaction: str) -> None:
        """Register a payment.

        Args:
            payment_id: the payment id
            transaction: the transaction id
        """
        new_repayment_schedule = []
        for payment in self.data.repayment_schedule:
            if payment.payment_id == payment_id:
                new_repayment_schedule.append(LoanPayment(
                    payment_id=payment_id,
                    amount_due=payment.amount_due_each_payment,
                    due_date=payment.timestamp,
                    transaction=transaction
                ))
            else:
                new_repayment_schedule.append(payment)

        self.data = Loan(
            principal_amount=self.data.principal_amount,
            repayment_schedule=self.data.repayment_schedule,
            offer_expiry=self.data.offer_expiry,
            accepted=self.data.accepted
        )
