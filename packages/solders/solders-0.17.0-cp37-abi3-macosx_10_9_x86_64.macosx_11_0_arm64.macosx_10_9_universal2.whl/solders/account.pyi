from solders.account_decoder import ParsedAccount
from solders.pubkey import Pubkey

class Account:
    def __init__(
        self,
        lamports: int,
        data: bytes,
        owner: Pubkey,
        executable: bool = False,
        rent_epoch: int = 0,
    ) -> None: ...
    @staticmethod
    def default() -> "Account": ...
    def __bytes__(self) -> bytes: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def __richcmp__(self, other: "Account", op: int) -> bool: ...
    @staticmethod
    def from_bytes(raw_bytes: bytes) -> "Account": ...
    def to_json(self) -> str: ...
    @staticmethod
    def from_json(raw: str) -> "Account": ...
    @property
    def lamports(self) -> int: ...
    @property
    def data(self) -> bytes: ...
    @property
    def owner(self) -> Pubkey: ...
    @property
    def executable(self) -> bool: ...
    @property
    def rent_epoch(self) -> int: ...

class AccountJSON:
    def __init__(
        self,
        lamports: int,
        data: ParsedAccount,
        owner: Pubkey,
        executable: bool = False,
        rent_epoch: int = 0,
    ) -> None: ...
    def __bytes__(self) -> bytes: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def __richcmp__(self, other: "AccountJSON", op: int) -> bool: ...
    @staticmethod
    def from_bytes(raw_bytes: bytes) -> "AccountJSON": ...
    def to_json(self) -> str: ...
    @staticmethod
    def from_json(raw: str) -> "Account": ...
    @property
    def lamports(self) -> int: ...
    @property
    def data(self) -> ParsedAccount: ...
    @property
    def owner(self) -> Pubkey: ...
    @property
    def executable(self) -> bool: ...
    @property
    def rent_epoch(self) -> int: ...
