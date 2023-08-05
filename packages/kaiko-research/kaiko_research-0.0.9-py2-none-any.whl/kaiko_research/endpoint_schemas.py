from kaiko_research.utils import (
    validate_time,
    validate_bases,
    validate_bases_weights,
    validate_risk_level,
)

# REFERENCE DATA
# Instruments
instruments_schema = {
    "exchange_code": {"type": "string", "required": False, "part_of_query": True},
    "base_asset": {"type": "string", "required": False, "part_of_query": True},
    "quote_asset": {"type": "string", "required": False, "part_of_query": True},
    "code": {"type": "string", "required": False, "part_of_query": True},
    "kaiko_legacy_symbol": {"type": "string", "required": False, "part_of_query": True},
    "class": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "allowed": ["spot", "future", "perpetual-future"],
    },
    "base_asset_class": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "allowed": [
            "cryptocurrency",
            "fiat",
            "stablecoin",
            "commodity",
            "leveraged-token",
        ],
    },
    "quote_asset_class": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "allowed": [
            "cryptocurrency",
            "fiat",
            "stablecoin",
            "commodity",
            "leveraged-token",
        ],
    },
    "trade_start_timestamp": {
        "type": "string",
        "required": False,
        "part_of_query": True,
    },
    "trade_end_timestamp": {"type": "string", "required": False, "part_of_query": True},
    "trade_count_min": {"type": "string", "required": False, "part_of_query": True},
    "trade_count_max": {"type": "string", "required": False, "part_of_query": True},
    "with_list_pools": {"type": "boolean", "required": False, "part_of_query": True},
    "continuation_token": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "orderBy": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "allowed": [
            "exchange_code",
            "class",
            "kaiko_legacy_symbol",
            "trade_start_timestamp",
            "trade_end_timestamp",
            "trade_count",
            "base_asset",
            "quote_asset",
            "code",
            "trade_count_min",
            "trade_count_max",
        ],
    },
    "order": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "allowed": ["1", "-1"],
    },
}
# Pools
pools_schema = {
    "address": {"type": "string", "required": False, "part_of_query": True},
    "protocol": {"type": "string", "required": False, "part_of_query": True},
    "type": {"type": "string", "required": False, "part_of_query": True},
    "fee": {"type": "string", "required": False, "part_of_query": True},
    "tokens": {"type": "string", "required": False, "part_of_query": True},
    "underlying_tokens": {"type": "string", "required": False, "part_of_query": True},
}

# TRADE DATA
# Trade data
trade_data_schema = {
    "commodity": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["trades"],
        "default": "trades",
    },
    "continuation_token": {"type": "string", "required": False, "part_of_query": True},
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v1",
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
    "exchange": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "krkn",
    },
    "instrument_class": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["spot", "future", "perpetual-future"],
        "default": "spot",
    },
    "instrument": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "btc-usdt",
    },
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
}

# ORDER BOOK DATA
# Order Book Snapshots: Full
order_book_snapshots_full_schema = {
    "commodity": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["order_book_snapshots"],
        "default": "order_book_snapshots",
    },
    "continuation_token": {"type": "string", "required": False, "part_of_query": True},
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v1",
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
    "exchange": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "krkn",
    },
    "instrument_class": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["spot", "future", "perpetual-future"],
        "default": "spot",
    },
    "instrument": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "btc-usdt",
    },
    "limit_orders": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "sort": {"type": "string", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
    "slippage": {"type": "string", "required": False, "part_of_query": True},
    "slippage_ref": {"type": "string", "required": False, "part_of_query": True},
}
# Order Book Snapshots: Raw
order_book_snapshots_raw_schema = {
    "commodity": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["order_book_snapshots"],
        "default": "order_book_snapshots",
    },
    "continuation_token": {"type": "string", "required": False, "part_of_query": True},
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v1",
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
    "exchange": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "krkn",
    },
    "instrument_class": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["spot", "future", "perpetual-future"],
        "default": "spot",
    },
    "instrument": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "btc-usdt",
    },
    "limit_orders": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "sort": {"type": "string", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
}
# Order Book Snapshots: Depth
order_book_snapshots_depth_schema = {
    "commodity": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["order_book_snapshots"],
        "default": "order_book_snapshots",
    },
    "continuation_token": {"type": "string", "required": False, "part_of_query": True},
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v1",
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
    "exchange": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "krkn",
    },
    "instrument_class": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["spot", "future", "perpetual-future"],
        "default": "spot",
    },
    "instrument": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "btc-usdt",
    },
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "sort": {"type": "string", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
}
# Order Book Snapshots: Slippage
order_book_snapshots_slippage_schema = {
    "commodity": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["order_book_snapshots"],
        "default": "order_book_snapshots",
    },
    "continuation_token": {"type": "string", "required": False, "part_of_query": True},
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v1",
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
    "exchange": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "krkn",
    },
    "instrument_class": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["spot", "future", "perpetual-future"],
        "default": "spot",
    },
    "instrument": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "btc-usdt",
    },
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "sort": {"type": "string", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
    "slippage": {"type": "string", "required": False, "part_of_query": True},
    "slippage_ref": {"type": "string", "required": False, "part_of_query": True},
}
# Order Book Aggregations: Full
order_book_aggregations_full_schema = {
    "commodity": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["order_book_snapshots"],
        "default": "order_book_snapshots",
    },
    "continuation_token": {"type": "string", "required": False, "part_of_query": True},
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v1",
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
    "exchange": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "krkn",
    },
    "instrument_class": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["spot", "future", "perpetual-future"],
        "default": "spot",
    },
    "instrument": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "btc-usdt",
    },
    "interval": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "sort": {"type": "string", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
    "slippage": {"type": "string", "required": False, "part_of_query": True},
    "slippage_ref": {"type": "string", "required": False, "part_of_query": True},
}
# Order Book Aggregations: Depth
order_book_aggregations_depth_schema = {
    "commodity": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["order_book_snapshots"],
        "default": "order_book_snapshots",
    },
    "continuation_token": {"type": "string", "required": False, "part_of_query": True},
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v1",
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
    "exchange": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "krkn",
    },
    "instrument_class": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["spot", "future", "perpetual-future"],
        "default": "spot",
    },
    "instrument": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "btc-usdt",
    },
    "interval": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "sort": {"type": "string", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
}
# Order Book Aggregations: Slippage
order_book_aggregations_slippage_schema = {
    "commodity": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["order_book_snapshots"],
        "default": "order_book_snapshots",
    },
    "continuation_token": {"type": "string", "required": False, "part_of_query": True},
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v1",
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
    "exchange": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "krkn",
    },
    "instrument_class": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["spot", "future", "perpetual-future"],
        "default": "spot",
    },
    "instrument": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "btc-usdt",
    },
    "interval": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "sort": {"type": "string", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
    "slippage": {"type": "string", "required": False, "part_of_query": True},
    "slippage_ref": {"type": "string", "required": False, "part_of_query": True},
}

# AGGREGATES
# OHLCV (Candles)
ohlcv_candles_schema = {
    "commodity": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["trades"],
        "default": "trades",
    },
    "continuation_token": {"type": "string", "required": False, "part_of_query": True},
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v1",
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
    "exchange": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "krkn",
    },
    "instrument_class": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["spot", "future", "perpetual-future"],
        "default": "spot",
    },
    "instrument": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "btc-usdt",
    },
    "interval": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "sort": {"type": "string", "required": False, "part_of_query": True},
}
# VWAP (Prices)
vwap_prices_schema = {
    "commodity": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["trades"],
        "default": "trades",
    },
    "continuation_token": {"type": "string", "required": False, "part_of_query": True},
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v1",
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
    "exchange": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "krkn",
    },
    "instrument_class": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["spot", "future", "perpetual-future"],
        "default": "spot",
    },
    "instrument": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "btc-usdt",
    },
    "interval": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "sort": {"type": "string", "required": False, "part_of_query": True},
}
# Count-OHLCV-VWAP
count_ohlcv_vwap_schema = {
    "commodity": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["trades"],
        "default": "trades",
    },
    "continuation_token": {"type": "string", "required": False, "part_of_query": True},
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v1",
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
    "exchange": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "krkn",
    },
    "instrument_class": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["spot", "future", "perpetual-future"],
        "default": "spot",
    },
    "instrument": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "btc-usdt",
    },
    "interval": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "sort": {"type": "string", "required": False, "part_of_query": True},
}

# PRICING AND VALUATION SERVICES
# Asset Price
asset_price_schema = {
    "base_asset": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "btc",
    },
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v1",
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
    "exclude_exchanges": {"type": "string", "required": False, "part_of_query": True},
    "interval": {"type": "string", "required": False, "part_of_query": True},
    "include_exchanges": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "quote_asset": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "usd",
    },
    "start_time": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "sort": {"type": "string", "required": False, "part_of_query": True},
    "sources": {"type": "boolean", "required": False, "part_of_query": True},
}
# Cross Price
cross_price_schema = {
    "base_asset": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "btc",
    },
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v1",
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
    "exclude_exchanges": {"type": "string", "required": False, "part_of_query": True},
    "interval": {"type": "string", "required": False, "part_of_query": True},
    "include_exchanges": {"type": "string", "required": False, "part_of_query": True},
    "outliers_strategy": {"type": "string", "required": False, "part_of_query": True},
    "outliers_min_data": {"type": "string", "required": False, "part_of_query": True},
    "outliers_threshold": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "quote_asset": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "usd",
    },
    "start_time": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "sort": {"type": "string", "required": False, "part_of_query": True},
    "sources": {"type": "boolean", "required": False, "part_of_query": True},
    "extrapolate_missing_values": {
        "type": "string",
        "required": False,
        "part_of_query": True,
    },
}
# Valuation
valuation_schema = {
    "bases": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "btc,eth",
        "validator": validate_bases,
    },
    "continuation_token": {"type": "string", "required": False, "part_of_query": True},
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v1",
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
    "exchanges": {"type": "string", "required": False, "part_of_query": True},
    "interval": {"type": "string", "required": False, "part_of_query": True},
    "percentages": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "1",
    },
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "semi_length_window": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "30m",
    },
    "sources": {"type": "boolean", "required": False, "part_of_query": True},
    "quote": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "usd",
    },
    "weights": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "0.5,0.5",
        "validator": validate_bases_weights,
    },
}
# OANDA FX Rates
oanda_fx_rates_schema = {
    "base": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "usd",
    },
    "continuation_token": {"type": "string", "required": False, "part_of_query": True},
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v2",
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
    "interval": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "quote": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "eur",
    },
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "sort": {"type": "string", "required": False, "part_of_query": True},
}

# DEX LIQUIDITY
# Liquidity Events
liquidity_events_schema = {
    "protocol": {"type": "string", "required": False, "part_of_query": True},
    "pool_address": {"type": "string", "required": False, "part_of_query": True},
    "pool_contains": {"type": "string", "required": False, "part_of_query": True},
    "block_number": {"type": "string", "required": False, "part_of_query": True},
    "user_addresses": {"type": "string", "required": False, "part_of_query": True},
    "tx_hash": {"type": "string", "required": False, "part_of_query": True},
    "start_block": {"type": "string", "required": False, "part_of_query": True},
    "end_block": {"type": "string", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
    "sort": {"type": "string", "required": False, "part_of_query": True},
    "type": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
}
# Liquidity Snapshots
liquidity_snapshots_schema = {
    "pool_address": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7",
    },
    "start_block": {"type": "string", "required": False, "part_of_query": True},
    "end_block": {"type": "string", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
    "sort": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
}
# Uniswap v3 Liquidity Snapshots
uniswap_v3_liquidity_snapshot_schema = {
    "pool_address": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
    },
    "start_block": {"type": "string", "required": False, "part_of_query": True},
    "end_block": {"type": "string", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
    "price_range": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
}

# LENDING PROTOCOLS
# Lending and Borrowing Events
lending_and_borrowing_schema = {
    "blockchain": {"type": "string", "required": False, "part_of_query": True},
    "protocol": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "aav2",
    },
    "user_address": {"type": "string", "required": False, "part_of_query": True},
    "tx_hash": {"type": "string", "required": False, "part_of_query": True},
    "asset": {"type": "string", "required": False, "part_of_query": True},
    "type": {"type": "string", "required": False, "part_of_query": True},
    "block_number": {"type": "string", "required": False, "part_of_query": True},
    "start_block": {"type": "string", "required": False, "part_of_query": True},
    "end_block": {"type": "string", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
    "sort": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
}

# RISK MANAGEMENT
# Value at Risk
value_at_risk_schema = {
    "bases": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "eth,btc,ltc",
        "validator": validate_bases,
    },
    "quote": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "usd",
    },
    "quantities": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "3,2,5",
    },
    "risk_level": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "0.95",
        "validator": validate_risk_level,
    },
    "start_time": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "end_time": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
    "exchanges": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "krkn",
    },
    "sources": {"type": "boolean", "required": False, "part_of_query": True},
    "data_version": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "allowed": ["v1", "v2"],
        "default": "v2",
    },
}

# DERIVATIVES METRICS
# Reference
reference_schema = {
    "exchange": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "drbt",
    },
    "instrument_class": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "allowed": ["future", "perpetual-future", "option"],
        "default": "perpetual-future",
    },
    "instrument": {"type": "string", "required": False, "part_of_query": True},
    "base_assets": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "btc",
    },
    "quote_assets": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "usdt",
    },
    "option_type": {"type": "string", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
}
# Risk
risk_schema = {
    "exchange": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "krkn",
    },
    "instrument_class": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "allowed": ["spot", "future", "perpetual-future"],
        "default": "spot",
    },
    "instrument": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "btc-usdt",
    },
    "interval": {"type": "string", "required": False, "part_of_query": True},
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "sort": {"type": "string", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
}
# Price
price_schema = {
    "exchange": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "okex",
    },
    "instrument_class": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "allowed": ["future", "perpetual-future", "option"],
        "default": "perpetual-future",
    },
    "instrument": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "btc-usdt",
    },
    "interval": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "1m",
    },
    "page_size": {"type": "integer", "required": False, "part_of_query": True},
    "sort": {"type": "string", "required": False, "part_of_query": True},
    "start_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
    "end_time": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "validator": validate_time,
    },
}

# DERIVATIVES ANALYTICS
# Implied Volatility Smile
iv_smile_schema = {
    "base": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "btc",
    },
    "quote": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "usd",
    },
    "exchange": {"type": "string", "required": False, "part_of_query": True},
    "time": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "expiry": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "2022-11-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "strikes": {
        "type": "string",
        "required": False,
        "part_of_query": True,
        "default": "1",
    },
    "forward_log_moneynequantitiessses": {
        "type": "string",
        "required": False,
        "part_of_query": True,
    },
}

# MARKET & ASSET ANALYTICS
# Asset Metrics
asset_metrics_schema = {
    "asset": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "btc",
    },
    "start_time": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "2022-10-01T00:00:00.000Z",
        "validator": validate_time,
    },
    "end_time": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "2023-01-31T00:00:00.000Z",
        "validator": validate_time,
    },
    "interval": {
        "type": "string",
        "required": True,
        "part_of_query": True,
        "default": "1h",
    },
    "sources": {"type": "boolean", "required": False, "part_of_query": True},
    "page_size": {
        "type": "integer",
        "required": False,
        "part_of_query": True,
        "default": 100,
    },
}

# RESEARCH INTELLIGENCE
# Exchage volume USD
exchange_volume_usd = {
    "exchage": {
        "type": "string",
        "required": True,
        "part_of_query": False,
        "default": "krkn,cbse,stmp,bnus,binc,gmni,btrx,itbi,huob,okex",
    },
    "instrument": {"type": "string", "required": True, "part_of_query": False},
}


# ENDPOINTS MAPPING
endpoints_mapping = [
    {
        "data_type": "Reference Data",
        "data_endpoints": "Assets",
        "url": "https://reference-data-api.kaiko.io/v1/",
        "suffix": "assets",
        "schema_name": "",
    },
    {
        "data_type": "Reference Data",
        "data_endpoints": "Exchanges",
        "url": "https://reference-data-api.kaiko.io/v1/",
        "suffix": "exchanges",
        "schema_name": "",
    },
    {
        "data_type": "Reference Data",
        "data_endpoints": "Instruments",
        "url": "https://reference-data-api.kaiko.io/v1/",
        "suffix": "instruments",
        "schema_name": "instruments_schema",
    },
    {
        "data_type": "Reference Data",
        "data_endpoints": "Pools",
        "url": "https://reference-data-api.kaiko.io/v1/",
        "suffix": "pools",
        "schema_name": "pools_schema",
    },
    {
        "data_type": "Trade data",
        "data_endpoints": "Trade data",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "{}.{}/exchanges/{}/{}/{}/trades",
        "schema_name": "trade_data_schema",
    },
    {
        "data_type": "Order Book data",
        "data_endpoints": "Order Book Snapshots: Full",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "{}.{}/exchanges/{}/{}/{}/snapshots/full",
        "schema_name": "order_book_snapshots_full_schema",
    },
    {
        "data_type": "Order Book data",
        "data_endpoints": "Order Book Snapshots: Raw",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "{}.{}/exchanges/{}/{}/{}/snapshots/raw",
        "schema_name": "order_book_snapshots_raw_schema",
    },
    {
        "data_type": "Order Book data",
        "data_endpoints": "Order Book Snapshots: Depth",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "{}.{}/exchanges/{}/{}/{}/snapshots/depth",
        "schema_name": "order_book_snapshots_depth_schema",
    },
    {
        "data_type": "Order Book data",
        "data_endpoints": "Order Book Snapshots: Slippage",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "{}.{}/exchanges/{}/{}/{}/snapshots/slippage",
        "schema_name": "order_book_snapshots_slippage_schema",
    },
    {
        "data_type": "Order Book data",
        "data_endpoints": "Order Book Aggregations: Full",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "{}.{}/exchanges/{}/{}/{}/ob_aggregations/full",
        "schema_name": "order_book_aggregations_full_schema",
    },
    {
        "data_type": "Order Book data",
        "data_endpoints": "Order Book Aggregations: Depth",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "{}.{}/exchanges/{}/{}/{}/ob_aggregations/depth",
        "schema_name": "order_book_aggregations_depth_schema",
    },
    {
        "data_type": "Order Book data",
        "data_endpoints": "Order Book Aggregations: Slippage",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "{}.{}/exchanges/{}/{}/{}/ob_aggregations/slippage",
        "schema_name": "order_book_aggregations_slippage_schema",
    },
    {
        "data_type": "Aggregates",
        "data_endpoints": "OHLCV (Candles)",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "{}.{}/exchanges/{}/{}/{}/aggregations/ohlcv",
        "schema_name": "ohlcv_candles_schema",
    },
    {
        "data_type": "Aggregates",
        "data_endpoints": "VWAP (Prices)",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "{}.{}/exchanges/{}/{}/{}/aggregations/vwap",
        "schema_name": "vwap_prices_schema",
    },
    {
        "data_type": "Aggregates",
        "data_endpoints": "Count-OHLCV-VWAP",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "{}.{}/exchanges/{}/{}/{}/aggregations/count_ohlcv_vwap",
        "schema_name": "count_ohlcv_vwap_schema",
    },
    {
        "data_type": "Pricing and Valuation Services",
        "data_endpoints": "Asset Price",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "trades.{}/spot_direct_exchange_rate/{}/{}",
        "schema_name": "asset_price_schema",
    },
    {
        "data_type": "Pricing and Valuation Services",
        "data_endpoints": "Cross Price",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "trades.{}/spot_exchange_rate/{}/{}",
        "schema_name": "cross_price_schema",
    },
    {
        "data_type": "Pricing and Valuation Services",
        "data_endpoints": "Valuation",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "trades.{}/valuation",
        "schema_name": "valuation_schema",
    },
    {
        "data_type": "Pricing and Valuation Services",
        "data_endpoints": "OANDA FX Rates",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "analytics.{}/oanda_fx_rates",
        "schema_name": "oanda_fx_rates_schema",
    },
    {
        "data_type": "DEX Liquidity",
        "data_endpoints": "Liquidity Events",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "liquidity.v1/events",
        "schema_name": "liquidity_events_schema",
    },
    {
        "data_type": "DEX Liquidity",
        "data_endpoints": "Liquidity Snapshots",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "liquidity.v1/snapshots",
        "schema_name": "liquidity_snapshots_schema",
    },
    {
        "data_type": "DEX Liquidity",
        "data_endpoints": "Uniswap v3 Liquidity Snapshots",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "liquidity.v1/snapshots/usp3",
        "schema_name": "uniswap_v3_liquidity_snapshot_schema",
    },
    {
        "data_type": "Lending Protocols",
        "data_endpoints": "Lending and Borrowing Events",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "lending.v1/events",
        "schema_name": "lending_and_borrowing_schema",
    },
    {
        "data_type": "Risk Management",
        "data_endpoints": "Value at Risk",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "analytics.{}/value_at_risk",
        "schema_name": "value_at_risk_schema",
    },
    {
        "data_type": "Derivatives Metrics",
        "data_endpoints": "Reference",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "derivatives.v2/reference",
        "schema_name": "reference_schema",
    },
    {
        "data_type": "Derivatives Metrics",
        "data_endpoints": "Risk",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "derivatives.v2/price",
        "schema_name": "risk_schema",
    },
    {
        "data_type": "Derivatives Metrics",
        "data_endpoints": "Price",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "derivatives.v2/risk",
        "schema_name": "price_schema",
    },
    {
        "data_type": "Derivatives Analytics",
        "data_endpoints": "Implied Volatility Smile",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "analytics.v2/implied_volatility_smile",
        "schema_name": "iv_smile_schema",
    },
    {
        "data_type": "Market & Asset Analytics",
        "data_endpoints": "Asset Metrics",
        "url": "https://us.market-api.kaiko.io/v2/data/",
        "suffix": "analytics.v2/asset_metrics",
        "schema_name": "asset_metrics_schema",
    },
]
