from decimal import Decimal
from dydx3 import Client
from dydx3.constants import (
    API_HOST_GOERLI,
    API_HOST_MAINNET,
    NETWORK_ID_GOERLI,
    NETWORK_ID_MAINNET,
    TIME_IN_FORCE_GTT,
    TIME_IN_FORCE_IOC,
)
from tarvis.common import secrets, time
import tarvis.common.environ
from tarvis.common.environ import DeploymentType
from tarvis.common.time import datetime
from tarvis.common.trading import Exchange, Order, OrderSide, OrderType, TradingPolicy


class DYDXExchange(Exchange):
    EXCHANGE_NAME = "dYdX"

    _ORDER_TYPE_TO_DYDX = {
        OrderType.MARKET: "MARKET",
        OrderType.LIMIT: "LIMIT",
        OrderType.STOP_LOSS: "STOP_MARKET",
    }
    _ORDER_TYPE_TO_TARVIS = dict(
        (value, key) for key, value in _ORDER_TYPE_TO_DYDX.items()
    )

    def __init__(
        self,
        credentials_secret: str,
        limit_fee: Decimal,
        market_limit: Decimal,
        order_expiration: float = time.span(days=27, hours=23),
    ):
        super().__init__()
        self.short_selling_supported = True
        self.stop_loss_orders_supported = True

        self._limit_fee = Decimal(limit_fee)
        self._market_limit = Decimal(market_limit)
        self._order_expiration = order_expiration

        credentials = secrets.get_secret(credentials_secret, decode_json=True)
        ethereum_address = credentials["ethereum_address"]
        stark_private_key = credentials["stark_private_key"]
        api_key = credentials["api_key"]
        api_secret = credentials["api_secret"]
        api_passphrase = credentials["api_passphrase"]

        if tarvis.common.environ.deployment == DeploymentType.PRODUCTION:
            host = API_HOST_MAINNET
            network_id = NETWORK_ID_MAINNET
        else:
            host = API_HOST_GOERLI
            network_id = NETWORK_ID_GOERLI

        self._client = Client(
            host=host,
            network_id=network_id,
            default_ethereum_address=ethereum_address,
            api_key_credentials={
                "key": api_key,
                "secret": api_secret,
                "passphrase": api_passphrase,
            },
            stark_private_key=stark_private_key,
        )

        self._position_id = self._get_position_id()

    def _get_position_id(self):
        response = self._client.private.get_account()
        return response.data["account"]["positionId"]

    @staticmethod
    def _convert_market_to_assets(market: str) -> (str, str):
        base_asset, quote_asset = market.split("-")
        return base_asset, quote_asset

    @staticmethod
    def _convert_assets_to_market(base_asset: str, quote_asset: str) -> str:
        return "-".join((base_asset, quote_asset))

    def get_policy(self, base_asset: str, quote_asset: str) -> TradingPolicy:
        market = self._convert_assets_to_market(base_asset, quote_asset)
        response = self._client.public.get_markets(market)
        market_data = response.data["markets"][market]

        minimum_order_quantity = Decimal(market_data["minOrderSize"])
        maximum_order_quantity = Decimal(market_data["maxPositionSize"])
        quantity_precision = Decimal(market_data["stepSize"])
        price_precision = Decimal(market_data["tickSize"])

        return TradingPolicy(
            minimum_order_quantity=minimum_order_quantity,
            maximum_order_quantity=maximum_order_quantity,
            quantity_precision=quantity_precision,
            price_precision=price_precision,
        )

    def get_quote(self, base_asset: str, quote_asset: str) -> Decimal:
        market = self._convert_assets_to_market(base_asset, quote_asset)
        response = self._client.public.get_markets(market)
        market_data = response.data["markets"][market]
        price = market_data["indexPrice"]
        return Decimal(price)

    def get_positions(self) -> dict[str, Decimal]:
        results = {}
        response = self._client.private.get_account()
        positions = response.data["account"]["openPositions"]

        # Only one open position possible for each market in dYdX
        for key, position in positions.items():
            market = position["market"]
            size = position["size"]

            base_asset, quote_asset = self._convert_market_to_assets(market)
            size = Decimal(size)

            results[base_asset] = size

        results["USD"] = Decimal(response.data["account"]["quoteBalance"])

        return results

    def get_open_orders(self, base_asset: str, quote_asset: str) -> list[Order]:
        _PAGE_SIZE = 100

        results = {}
        market = self._convert_assets_to_market(base_asset, quote_asset)
        page_order_count = _PAGE_SIZE
        start_datetime = None
        while page_order_count == _PAGE_SIZE:
            response = self._client.private.get_orders(
                market=market,
                status="PENDING,OPEN,UNTRIGGERED",
                limit=_PAGE_SIZE,
                created_before_or_at=start_datetime,
            )

            dydx_orders = response.data["orders"]
            page_order_count = len(dydx_orders)

            for dydx_order in dydx_orders:
                order_id = dydx_order["id"]
                market = dydx_order["market"]
                quantity = dydx_order["size"]
                side = dydx_order["side"]
                order_type = dydx_order["type"]
                if order_type == "STOP_MARKET":
                    price = dydx_order["triggerPrice"]
                else:
                    price = dydx_order["price"]
                created_at = dydx_order["createdAt"]
                remaining_quantity = dydx_order["remainingSize"]

                quote_asset, base_asset = self._convert_market_to_assets(market)
                quantity = Decimal(quantity)
                side = OrderSide[side]
                # noinspection PyBroadException
                try:
                    order_type = self._ORDER_TYPE_TO_TARVIS[order_type]
                except:
                    order_type = OrderType.UNSUPPORTED
                creation_date = datetime.parse(created_at)
                creation_time = creation_date.timestamp()
                filled_quantity = quantity - Decimal(remaining_quantity)
                meta_data = {"order_id": order_id}

                start_datetime = created_at

                order = Order(
                    quote_asset,
                    base_asset,
                    side,
                    order_type,
                    creation_time,
                    quantity=quantity,
                    price=price,
                    filled_quantity=filled_quantity,
                    meta_data=meta_data,
                )

                results[order_id] = order

        return list(results.values())

    def place_order(
        self,
        policy: TradingPolicy,
        base_asset: str,
        quote_asset: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: Decimal,
        price: Decimal = None,
        stop_loss_price: Decimal = None,
        increasing_position: bool = None,
    ):
        market = self._convert_assets_to_market(base_asset, quote_asset)
        dydx_order_type = self._ORDER_TYPE_TO_DYDX[order_type]
        expiration = int(time.time() + self._order_expiration)

        if order_type == OrderType.STOP_LOSS:
            if stop_loss_price is None:
                raise ValueError("stop_loss_price is None.")
            if price is None:
                price = stop_loss_price
            trigger_price = str(stop_loss_price)
        else:
            trigger_price = None

        # dYdX requires all orders, even market orders, to have a price
        if price is None:
            raise ValueError("price is None.")
        if order_type in [OrderType.MARKET, OrderType.STOP_LOSS]:
            if side == OrderSide.BUY:
                price *= 1 + self._market_limit
            else:
                price *= 1 - self._market_limit
            price = policy.align_price(price)

        if increasing_position is not None:
            reduce_only = not increasing_position
        else:
            reduce_only = None

        # GTT (Good 'Til Date/Time) is not allowed for reduce and market orders
        if reduce_only or (order_type != OrderType.LIMIT):
            time_in_force = TIME_IN_FORCE_IOC
        else:
            time_in_force = TIME_IN_FORCE_GTT

        self._client.private.create_order(
            position_id=self._position_id,
            market=market,
            side=side.name,
            order_type=dydx_order_type,
            post_only=False,
            size=str(quantity),
            price=str(price),
            limit_fee=str(self._limit_fee),
            trigger_price=trigger_price,
            time_in_force=time_in_force,
            expiration_epoch_seconds=expiration,
            reduce_only=reduce_only,
        )

    def cancel_order(self, order: Order):
        self._client.private.cancel_order(order.meta_data["order_id"])
