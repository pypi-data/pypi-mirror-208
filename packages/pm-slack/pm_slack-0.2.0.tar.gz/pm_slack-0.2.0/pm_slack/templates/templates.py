from dataclasses import dataclass
from typing import Any, TypedDict


@dataclass
class Template:
    params: Any  # Python TypedDict ile dict'i eşleştiremiyor
    channel: str
    _header: str
    _text: str

    @property
    def message(self) -> str:
        _message = self._text.format(**self.params)
        return _message

    @property
    def header(self) -> str:
        return self._header

    @property
    def blocks(self) -> Any:
        ...


class FutureOrderParams(TypedDict):
    building_name: str
    brand_name: str
    adisyon_no: str
    platform: str


@dataclass
class FutureOrderTemplate(Template):
    params: FutureOrderParams
    channel: str
    _header: str = ":information_source: İleri Tarihli Sipariş Geldi."
    _text: str = "*{building_name}* binasında bulunan *{brand_name}* markasına *{adisyon_no}* adisyon nolu *{platform}* üzerinden ileri \
tarihli bir sipariş geldi ancak teslimat saati bilinmiyor. Lütfen *{platform}* ile iletişime geçiniz ve aldığınız uyarı \
mesajının kodunu yazılım-destek kanalına iletiniz. (ERR-0002)"

    @property
    def blocks(self) -> Any:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/DawwNigKJ2ckPeDeDM7jAg/o.jpg",
                    "alt_text": "brand logo",
                },
            },
            {"type": "divider"},
        ]


class NoOrdersFromBrandParams(TypedDict):
    log_id: str
    function_name: str


@dataclass
class NoOrdersFromBrandTemplate(Template):
    params: NoOrdersFromBrandParams
    channel: str
    _header: str = ":skull: Hiçbir markadan sipariş alınamayacak"
    _text: str = "Acil işlem yapınız ! log_id: {log_id}, function_name: {function_name}"

    @property
    def blocks(self) -> Any:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
            },
        ]


class CantSaveOrderParams(TypedDict):
    brand_name: str
    platform_code: str
    platform: str


@dataclass
class CantSaveOrderTemplate(Template):
    params: CantSaveOrderParams
    channel: str
    _header: str = ":exclamation: Sipariş Sisteme Kaydedilemedi"
    _text: str = """
Eksik sipariş içeriği nedeniyle  *{brand_name}* markasına gelen *{platform_code}* platform kodlu sipariş sisteme
kaydedilemedi. Bu sipariş ile ilgili aldığınız uyarı mesajı kodunu
yazılım-destek kanalına iletiniz ve *{platform}* ile iletişime geçiniz.
"""

    @property
    def blocks(self) -> Any:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/DawwNigKJ2ckPeDeDM7jAg/o.jpg",
                    "alt_text": "alt text for image",
                },
            },
        ]


class OrderCantConfirmedParams(TypedDict):
    building_name: str
    brand_name: str
    adisyon_no: str
    platform: str


@dataclass
class OrderCantConfirmedTemplate(Template):
    params: OrderCantConfirmedParams
    channel: str
    _header: str = ":exclamation: Platforma Siparişin Onaylandığı Bilgisi Gönderilemedi"
    _text: str = """
*{building_name}* binasında bulunan *{brand_name}* markasındaki *{adisyon_no}* adisyon numaralı siparişin
onaylandığı bilgisi *{platform}* platformuna iletilemedi.
Bu sipariş ile ilgili aldığınız uyarı mesajı kodunu
yazılım-destek kanalına iletiniz ve {platform} ile iletişime geçiniz.
"""

    @property
    def blocks(self) -> Any:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/DawwNigKJ2ckPeDeDM7jAg/o.jpg",
                    "alt_text": "alt text for image",
                },
            },
        ]


class PlatformConnectionFailedParams(TypedDict):
    log_id: str
    function_name: str


@dataclass
class PlatformConnectionsFailedTemplate(Template):
    params: PlatformConnectionFailedParams
    channel: str
    _header: str = ":skull: Bazı Markaların Platform Bağlantısı Sağlanamadı"
    _text: str = """
    Acil işlem yapınız ! log_id: {log_id}, function_name: {function_name}
    """

    @property
    def blocks(self) -> Any:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
            },
        ]
