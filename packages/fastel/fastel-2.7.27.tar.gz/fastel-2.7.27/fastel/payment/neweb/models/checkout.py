import time
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


def timestamp_generate() -> str:
    return str(int(time.time()))


class CheckoutModel(BaseModel):
    MerchantOrderNo: str
    Amt: int
    ItemDesc: str = "Online Payment To Neweb pay"
    Email: EmailStr
    CREDIT: Optional[Literal[0, 1]]
    ANDROIDPAY: Optional[Literal[0, 1]]
    SAMSUNGPAY: Optional[Literal[0, 1]]
    LINEPAY: Optional[Literal[0, 1]]
    ImageUrl: Optional[str]
    CreditRed: Optional[Literal[0, 1]]
    CREDITAE: Optional[Literal[0, 1]]
    UNIONPAY: Optional[Literal[0, 1]]
    WEBATM: Optional[Literal[0, 1]]
    VACC: Optional[Literal[0, 1]]
    CVS: Optional[Literal[0, 1]]
    BARCODE: Optional[Literal[0, 1]]
    ALIPAY: Optional[Literal[0, 1]]
    P2G: Optional[Literal[0, 1]]
    CVSCOM: Literal[0, 1, 2, 3] = 0

    NotifyURL: Optional[str]
    ReturnURL: Optional[str]
    CustomerURL: Optional[str]

    MerchantID: Optional[str]
    Version: Optional[str] = "2.0"
    RespondType: Optional[str] = "JSON"
    TimeStamp: str = Field(default_factory=timestamp_generate)

    LgsType: Literal["B2C", "B2B"] = "B2C"
