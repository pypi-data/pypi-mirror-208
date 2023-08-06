import common  # noqa
from decimal import Decimal
from tarvis.common import time
from tarvis.common.trading import OrderSide, OrderType
from tarvis.exchange.woo import WooExchange, WooVersion
import pytest  # noqa

_TEST_CREDENTIALS = "woo_margin_test_credentials"

_BASE_ASSET = "BTC"
_QUOTE_ASSET = "USDT"

_PRICE_RANGE_MIN = 1000
_PRICE_RANGE_MAX = 1000000000

_UNREALISTIC_BUY = Decimal("0.9")
_UNREALISTIC_SELL = Decimal("1.1")
_STOP_LOSS_LONG = Decimal("0.8")
_STOP_LOSS_SHORT = Decimal("1.2")

_SETTLEMENT_DELAY = 5
_ALLOWED_TIME_DIFFERENCE = 5

exchange = WooExchange(_TEST_CREDENTIALS, WooVersion.MARGIN)
price = exchange.get_quote(_BASE_ASSET, _QUOTE_ASSET)
trading_policy = exchange.get_policy(_BASE_ASSET, _QUOTE_ASSET)
minimum_order_quantity = trading_policy.get_minimum_order_quantity(price)


def test_get_quote():
    assert price > _PRICE_RANGE_MIN
    assert price < _PRICE_RANGE_MAX


def test_get_policy():
    assert minimum_order_quantity < (1.0 / _PRICE_RANGE_MIN)
    assert minimum_order_quantity > (1.0 / _PRICE_RANGE_MAX)
    # noinspection PyProtectedMember
    assert trading_policy._quantity_decimals == 8
    # noinspection PyProtectedMember
    assert trading_policy._price_decimals == 2


def test_get_positions():
    positions = exchange.get_positions()
    assert positions is not None
    quote_position = positions.get(_QUOTE_ASSET, 0)
    assert quote_position > 0


def test_get_open_orders():
    orders = exchange.get_open_orders(_BASE_ASSET, _QUOTE_ASSET)
    assert orders is not None


def test_long_market_order_completed():
    exchange.cancel_open_orders(_BASE_ASSET, _QUOTE_ASSET)

    orders = exchange.get_open_orders(_BASE_ASSET, _QUOTE_ASSET)
    assert len(orders) == 0

    positions = exchange.get_positions()
    base_position_start = positions.get(_BASE_ASSET, 0)
    quote_position_start = positions.get(_QUOTE_ASSET, 0)

    # Order twice as much as necessary to ensure success
    order_quantity = trading_policy.align_quantity(minimum_order_quantity * 2)
    order_price = trading_policy.align_price(price)
    exchange.place_order(
        trading_policy,
        _BASE_ASSET,
        _QUOTE_ASSET,
        OrderSide.BUY,
        OrderType.MARKET,
        order_quantity,
        price=order_price,
    )

    time.sleep(_SETTLEMENT_DELAY)

    orders = exchange.get_open_orders(_BASE_ASSET, _QUOTE_ASSET)
    assert len(orders) == 0

    positions = exchange.get_positions()
    base_position_end = positions.get(_BASE_ASSET, 0)
    quote_position_end = positions.get(_QUOTE_ASSET, 0)
    assert float(base_position_end - base_position_start) == pytest.approx(
        float(order_quantity), 0.01
    )
    assert float(quote_position_start - quote_position_end) == pytest.approx(
        float(order_quantity * order_price), 0.01
    )


def test_long_stop_loss_order():
    positions = exchange.get_positions()
    base_position = positions.get(_BASE_ASSET, 0)
    # Assumes a previous test purchased minimum quantity
    assert base_position > minimum_order_quantity

    start_time = time.time()

    order_quantity = trading_policy.align_quantity(base_position)
    stop_loss_price = trading_policy.align_price(price * _STOP_LOSS_LONG)
    exchange.place_order(
        trading_policy,
        _BASE_ASSET,
        _QUOTE_ASSET,
        OrderSide.SELL,
        OrderType.STOP_LOSS,
        order_quantity,
        stop_loss_price=stop_loss_price,
    )

    end_time = time.time()

    orders = exchange.get_open_orders(_BASE_ASSET, _QUOTE_ASSET)
    assert len(orders) == 1

    order = orders[0]
    assert order.base_asset == _BASE_ASSET
    assert order.quote_asset == _QUOTE_ASSET
    # noinspection PyProtectedMember
    assert float(order._quantity) == pytest.approx(float(order_quantity))
    assert float(order.price) == pytest.approx(float(stop_loss_price))
    assert order.side == OrderSide.SELL
    assert order.order_type == OrderType.STOP_LOSS
    # Allow 1 second time inaccuracy
    assert order.creation_time > (start_time - _ALLOWED_TIME_DIFFERENCE)
    assert order.creation_time < (end_time + _ALLOWED_TIME_DIFFERENCE)
    assert order.filled_quantity == 0

    exchange.cancel_order(order)

    orders = exchange.get_open_orders(_BASE_ASSET, _QUOTE_ASSET)
    assert len(orders) == 0


def test_long_limit_order():
    exchange.cancel_open_orders(_BASE_ASSET, _QUOTE_ASSET)

    start_time = time.time()

    # Create an unrealistic limit order that will not be filled
    order_price = trading_policy.align_price(price * _UNREALISTIC_BUY)
    order_quantity = trading_policy.get_minimum_order_quantity(order_price)
    exchange.place_order(
        trading_policy,
        _BASE_ASSET,
        _QUOTE_ASSET,
        OrderSide.BUY,
        OrderType.LIMIT,
        order_quantity,
        price=order_price,
    )

    end_time = time.time()

    orders = exchange.get_open_orders(_BASE_ASSET, _QUOTE_ASSET)
    assert len(orders) == 1

    order = orders[0]
    assert order.base_asset == _BASE_ASSET
    assert order.quote_asset == _QUOTE_ASSET
    # noinspection PyProtectedMember
    assert float(order._quantity) == pytest.approx(float(order_quantity))
    assert float(order.price) == pytest.approx(float(order_price))
    assert order.side == OrderSide.BUY
    assert order.order_type == OrderType.LIMIT
    # Allow 1 second time inaccuracy
    assert order.creation_time > (start_time - _ALLOWED_TIME_DIFFERENCE)
    assert order.creation_time < (end_time + _ALLOWED_TIME_DIFFERENCE)
    assert order.filled_quantity == 0

    exchange.cancel_order(order)

    orders = exchange.get_open_orders(_BASE_ASSET, _QUOTE_ASSET)
    assert len(orders) == 0


def test_close_long_position():
    positions = exchange.get_positions()
    base_position_start = positions.get(_BASE_ASSET, 0)
    quote_position_start = positions.get(_QUOTE_ASSET, 0)
    # Assumes a previous test purchased
    assert base_position_start >= 0

    order_price = trading_policy.align_price(price)
    order_quantity = trading_policy.align_quantity(base_position_start)
    assert order_quantity >= minimum_order_quantity

    exchange.place_order(
        trading_policy,
        _BASE_ASSET,
        _QUOTE_ASSET,
        OrderSide.SELL,
        OrderType.MARKET,
        order_quantity,
        price=order_price,
    )

    time.sleep(_SETTLEMENT_DELAY)

    positions = exchange.get_positions()
    base_position_end = positions.get(_BASE_ASSET, 0)
    quote_position_end = positions.get(_QUOTE_ASSET, 0)
    assert quote_position_end > quote_position_start
    assert base_position_end <= minimum_order_quantity
    assert float(base_position_start - base_position_end) == pytest.approx(
        float(order_quantity), 0.01
    )
    assert float(quote_position_end - quote_position_start) == pytest.approx(
        float(order_quantity * order_price), 0.01
    )


def test_short_market_order_completed():
    positions = exchange.get_positions()
    base_position_start = positions.get(_BASE_ASSET, 0)
    quote_position_start = positions.get(_QUOTE_ASSET, 0)
    assert base_position_start >= 0

    order_price = trading_policy.align_price(price)
    # Leave enough base asset for at least another order
    order_quantity = (quote_position_start / order_price) - (minimum_order_quantity * 2)
    order_quantity = trading_policy.align_quantity(order_quantity)
    assert order_quantity >= trading_policy.get_minimum_order_quantity(order_price)

    exchange.place_order(
        trading_policy,
        _BASE_ASSET,
        _QUOTE_ASSET,
        OrderSide.SELL,
        OrderType.MARKET,
        order_quantity,
        price=order_price,
    )

    time.sleep(_SETTLEMENT_DELAY)

    orders = exchange.get_open_orders(_BASE_ASSET, _QUOTE_ASSET)
    assert len(orders) == 0

    positions = exchange.get_positions()
    base_position_end = positions.get(_BASE_ASSET, 0)
    quote_position_end = positions.get(_QUOTE_ASSET, 0)
    assert quote_position_end > quote_position_start
    assert base_position_end < 0
    assert float(base_position_start - base_position_end) == pytest.approx(
        float(order_quantity), 0.01
    )
    assert float(quote_position_end - quote_position_start) == pytest.approx(
        float(order_quantity * order_price), 0.01
    )


def test_short_stop_loss_order():
    positions = exchange.get_positions()
    base_position = positions.get(_BASE_ASSET, 0)
    assert base_position < 0
    base_position = -base_position
    # Assumes a previous test purchased minimum quantity
    assert base_position > minimum_order_quantity

    start_time = time.time()

    order_quantity = trading_policy.align_quantity(base_position)
    stop_loss_price = trading_policy.align_price(price * _STOP_LOSS_SHORT)
    exchange.place_order(
        trading_policy,
        _BASE_ASSET,
        _QUOTE_ASSET,
        OrderSide.BUY,
        OrderType.STOP_LOSS,
        order_quantity,
        stop_loss_price=stop_loss_price,
    )

    end_time = time.time()

    orders = exchange.get_open_orders(_BASE_ASSET, _QUOTE_ASSET)
    assert len(orders) == 1

    order = orders[0]
    assert order.base_asset == _BASE_ASSET
    assert order.quote_asset == _QUOTE_ASSET
    # noinspection PyProtectedMember
    assert float(order._quantity) == pytest.approx(float(order_quantity))
    assert float(order.price) == pytest.approx(float(stop_loss_price))
    assert order.side == OrderSide.BUY
    assert order.order_type == OrderType.STOP_LOSS
    # Allow 1 second time inaccuracy
    assert order.creation_time > (start_time - _ALLOWED_TIME_DIFFERENCE)
    assert order.creation_time < (end_time + _ALLOWED_TIME_DIFFERENCE)
    assert order.filled_quantity == 0

    exchange.cancel_order(order)

    orders = exchange.get_open_orders(_BASE_ASSET, _QUOTE_ASSET)
    assert len(orders) == 0


def test_short_limit_order():
    exchange.cancel_open_orders(_BASE_ASSET, _QUOTE_ASSET)

    start_time = time.time()

    # Create an unrealistic limit order that will not be filled
    order_price = trading_policy.align_price(price * _UNREALISTIC_SELL)
    order_quantity = trading_policy.get_minimum_order_quantity(order_price)
    exchange.place_order(
        trading_policy,
        _BASE_ASSET,
        _QUOTE_ASSET,
        OrderSide.SELL,
        OrderType.LIMIT,
        order_quantity,
        price=order_price,
    )

    end_time = time.time()

    orders = exchange.get_open_orders(_BASE_ASSET, _QUOTE_ASSET)
    assert len(orders) == 1

    order = orders[0]
    assert order.base_asset == _BASE_ASSET
    assert order.quote_asset == _QUOTE_ASSET
    # noinspection PyProtectedMember
    assert float(order._quantity) == pytest.approx(float(order_quantity))
    assert float(order.price) == pytest.approx(float(order_price))
    assert order.side == OrderSide.SELL
    assert order.order_type == OrderType.LIMIT
    # Allow 1 second time inaccuracy
    assert order.creation_time > (start_time - _ALLOWED_TIME_DIFFERENCE)
    assert order.creation_time < (end_time + _ALLOWED_TIME_DIFFERENCE)
    assert order.filled_quantity == 0

    exchange.cancel_order(order)

    orders = exchange.get_open_orders(_BASE_ASSET, _QUOTE_ASSET)
    assert len(orders) == 0


def test_close_short_position():
    positions = exchange.get_positions()
    base_position_start = positions.get(_BASE_ASSET, 0)
    quote_position_start = positions.get(_QUOTE_ASSET, 0)
    assert base_position_start < 0

    order_price = trading_policy.align_price(price)
    order_quantity = trading_policy.align_quantity(-base_position_start)
    assert order_quantity >= trading_policy.get_minimum_order_quantity(order_price)

    exchange.place_order(
        trading_policy,
        _BASE_ASSET,
        _QUOTE_ASSET,
        OrderSide.BUY,
        OrderType.MARKET,
        order_quantity,
        price=order_price,
    )

    time.sleep(_SETTLEMENT_DELAY)

    positions = exchange.get_positions()
    base_position_end = positions.get(_BASE_ASSET, 0)
    quote_position_end = positions.get(_QUOTE_ASSET, 0)
    assert quote_position_end < quote_position_start
    assert base_position_end > base_position_start
    assert float(base_position_end - base_position_start) == pytest.approx(
        float(order_quantity), 0.01
    )
    assert float(quote_position_start - quote_position_end) == pytest.approx(
        float(order_quantity * order_price), 0.01
    )
