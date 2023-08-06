from typing import Optional

from pydantic import BaseModel


class MiniPayInfo(BaseModel):
    package: str
    paySign: str
    nonceStr: str
    signType: str = "RSA"
    prepay_id: Optional[str]
    timeStamp: str


class JSAPIPayInfo(BaseModel):
    pass


class TransactionAmount(BaseModel):
    total: int
    currency: str = "CNY"


class GoodsDetail(BaseModel):
    merchant_goods_id: str
    wechatpay_goods_id: Optional[str]
    goods_name: Optional[str]
    quantity: int
    unit_price: int


class TransactionDetail(BaseModel):
    cost_price: Optional[int]
    invoice_id: Optional[str]
    goods_detail: Optional[list[GoodsDetail]]


class StoreInfo(BaseModel):
    id: str
    name: Optional[str]
    area_code: Optional[str]
    address: Optional[str]


class TransactionSceneInfo(BaseModel):
    payer_client_ip: str
    device_id: Optional[str]
    store_info: Optional[StoreInfo]


class TransactionSettleInfo(BaseModel):
    profit_sharing: Optional[bool]


class PayInfo(BaseModel):
    appid: str
    mchid: str
    description: str
    out_trade_no: str
    time_expire: Optional[str]
    attach: Optional[str]
    notify_url: str
    goods_tag: Optional[str]
    support_fapiao: Optional[bool]
    amount: TransactionAmount
    detail: Optional[TransactionDetail]
    scene_info: Optional[TransactionSceneInfo]
    settle_info: Optional[TransactionSettleInfo]


class NativePayInfo(PayInfo):
    pass


class TransactionPayer(BaseModel):
    openid: str


class JsAPIPayInfo(PayInfo):
    payer: TransactionPayer


class TransactionInfoPayer(BaseModel):
    openid: Optional[str]


class TransactionInfoAmount(BaseModel):
    total: Optional[int]
    payer_total: Optional[int]
    currency: Optional[str]
    payer_currency: Optional[str]


class TransactionInfoSceneInfo(BaseModel):
    device_id: Optional[str]


class TransactionInfoPromotionDetailGoodsDetail(BaseModel):
    goods_id: str
    quantity: int
    unit_price: int
    discount_amount: int
    goods_remark: Optional[str]


class TransactionInfoPromotionDetail(BaseModel):
    coupon_id: str
    name: Optional[str]
    scope: Optional[str]
    type: Optional[str]
    amount: int
    stock_id: Optional[str]
    wechatpay_contribute: Optional[int]
    merchant_contribute: Optional[int]
    other_contribute: Optional[int]
    currency: Optional[str]
    goods_detail: Optional[list[TransactionInfoPromotionDetailGoodsDetail]]


class TransactionInfo(BaseModel):
    appid: str
    mchid: str
    out_trade_no: str
    transaction_id: Optional[str]
    trade_type: Optional[str]
    trade_state: str
    trade_state_desc: str
    bank_type: Optional[str]
    attach: Optional[str]
    success_time: Optional[str]
    payer: Optional[TransactionInfoPayer]
    amount: Optional[TransactionInfoAmount]
    scene_info: Optional[TransactionInfoSceneInfo]
    promotion_detail: Optional[list[TransactionInfoPromotionDetail]]
