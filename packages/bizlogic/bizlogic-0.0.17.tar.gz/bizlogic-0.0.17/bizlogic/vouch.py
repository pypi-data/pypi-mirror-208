import time
import uuid
from typing import Self

from bizlogic.protoc.vouch_pb2 import Vouch
from bizlogic.utils import GROUP_BY, PARSERS, ParserType, TestingOnly, Utils

from ipfsclient.ipfs import Ipfs

from ipfskvs.index import Index
from ipfskvs.store import Store

import pandas as pd


PREFIX = "vouch"


class VouchWriter:
    """Class for writing Vouches.

    "voucher": person giving the vouch
    "vouchee": person receiving the vouch

    ipfs filename:
        vouch/vouchee_<id>.voucher_<id>/created_<timestamp>
    """

    vouch_id: str
    vouchee: str
    voucher: str
    ipfsclient: Ipfs
    data: Vouch

    def __init__(
            self: Self,
            ipfsclient: Ipfs,
            voucher: str,
            vouchee: str) -> None:
        """Initialize VouchWriter.

        Args:
            ipfsclient (Ipfs): IPFS client.
            voucher (str): voucher string.
            vouchee (str): vouchee string.
        """
        self.vouch_id = str(uuid.uuid4())
        self.vouchee = vouchee
        self.voucher = voucher
        self.ipfsclient = ipfsclient
        self.data = Vouch(active=True)

    def write(self: Self) -> None:
        """Write the Vouch."""
        self._generate_index()

        store = Store(
            index=self.index,
            ipfs=self.ipfsclient,
            writer=self.data
        )

        store.add()

    @TestingOnly.decorator
    def delete(self: Self) -> None:
        """Delete the vouch from IPFS."""
        store = Store(
            index=self.index,
            ipfs=self.ipfsclient,
            writer=self.data
        )

        store.delete()

    def _generate_index(self: Self) -> None:
        """Generate the index for the vouch."""
        self.index = Index(
            prefix=PREFIX,
            index={
                "vouchee": self.vouchee,
                "voucher": self.voucher,
                "vouch": self.vouch_id
            },
            subindex=Index(
                index={
                    "created": str(time.time_ns())
                }
            )
        )


class VouchReader():
    """Read and query vouches from IPFS."""

    ipfsclient: Ipfs

    def __init__(self: Self, ipfsclient: Ipfs) -> None:
        """Create a new vouch reader.

        Args:
            ipfsclient (Ipfs): The ipfs client
        """
        self.ipfsclient = ipfsclient

    def get_all_vouches(self: Self) -> pd.DataFrame:
        """Get all vouches.

        Returns:
            pd.DataFrame: A dataframe of all vouches
        """
        query_results = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={}
            ),
            ipfs=self.ipfsclient,
            reader=Vouch()
        )

        # parse applications into a dataframe
        df = Store.to_dataframe(query_results, PARSERS[ParserType.VOUCH])

        # filter for most recent applications per loan_id
        return Utils.get_most_recent(df, GROUP_BY[ParserType.VOUCH])

    def query_vouches(
        self: Self,
        voucher: str = None,
        vouchee: str = None
    ) -> pd.DataFrame:
        """Search vouches for a vouchee or voucher.

        Args:
            voucher (str, optional): The voucher to search for.
                Defaults to None.
            vouchee (str, optional): The vouchee to search for.
                Defaults to None.

        Returns:
            pd.DataFrame: A dataframe of all vouches matching the query
        """
        assert voucher or vouchee, "Must provide voucher or vouchee"

        index = {
            "voucher": voucher
        } if voucher else {
            "vouchee": vouchee
        }

        query_results = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index=index,
                size=2
            ),
            ipfs=self.ipfsclient,
            reader=Vouch()
        )

        # parse applications into a dataframe
        df = Store.to_dataframe(query_results, PARSERS[ParserType.VOUCH])

        # filter for most recent applications per loan_id
        return Utils.get_most_recent(df, GROUP_BY[ParserType.VOUCH])
