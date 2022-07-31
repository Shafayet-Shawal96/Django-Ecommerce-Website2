from sslcommerz_sdk.contrib.django_app.models import SslcommerzSession
from sslcommerz_sdk.handlers import PaymentHandler
from sslcommerz_sdk.orm_adapters.django import DjangoORMAdapter
from sslcommerz_sdk.store import SslcommerzStore
from sslcommerz_sdk.store_providers import SingleStoreProvider

store = SslcommerzStore(
    store_id="abclt62de890925cf2",
    store_passwd="abclt62de890925cf2@ssl",
    base_url="https://sandbox.sslcommerz.com",
)
payment_handler = PaymentHandler(
    model=SslcommerzSession,
    orm_adapter=DjangoORMAdapter(),
    store_provider=SingleStoreProvider(store=store),
)