from dataclasses import dataclass
from typing import Optional, List

@dataclass
class IsUserType:
   isuser: Optional[bool]
   token: Optional[str]
   id_user: Optional[int]
   email: Optional[str]

@dataclass
class OrderType:
   total: float
   opciones_entrega: str

@dataclass
class OrderIdentificationType:
   email: str
   name: str
   last_name: str
   document_number: int
   phone: int
   ruc: Optional[str]

@dataclass 
class OrderStoreType:
   store_name: Optional[str]

@dataclass
class OrderDeliveryType:
   department: str
   province: str
   district: str
   address: str
   street: str
   street_number: str
   reference: Optional[str]

@dataclass
class OrderPaymentType:
   amount: float
   payment_method: str

@dataclass
class OrderDetailType:
   quantity: int
   price: float
   subtotal: float
   product_id: int

@dataclass
class RegisterOrderData:
   isuser: Optional[IsUserType]
   order: OrderType
   order_identification: OrderIdentificationType
   order_store: Optional[OrderStoreType]
   order_delivery: Optional[OrderDeliveryType]
   order_payment: OrderPaymentType
   order_delivery: list[OrderDetailType]