import hashlib
import hmac
import json
import requests
import time
from urllib.parse import quote_plus


class WooClientError(Exception):
    def __init__(self, response):
        self.status_code = response.status_code
        try:
            self.msg = response.json()
        except ValueError:
            self.msg = response.text
        self.response = response
        self.request = getattr(response, "request", None)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"WooClientError(status_code={self.status_code}, response={self.msg})"


class WooClient:
    def __init__(
        self,
        base_url: str,
        api_key: str = None,
        api_secret: str = None,
        application_id: str = None,
    ):
        self._base_url = base_url.removesuffix("/")
        self._api_key = api_key
        self._api_secret = api_secret
        self._application_id = application_id
        if api_key is not None:
            self._api_key_bytes = bytes(self._api_secret, "utf-8")

    @staticmethod
    def _get_request_path(version: int, end_point: str) -> str:
        return f"/v{version}/{end_point}"

    def _get_url(self, version: int, end_point: str) -> str:
        return f"{self._base_url}/v{version}/{end_point}"

    @staticmethod
    def _format_param(param):
        if isinstance(param, bool):
            return str(param).lower()
        else:
            return param

    def _prepare_query_params(self, params):
        sorted_not_none_params = {
            key: self._format_param(value)
            for key, value in sorted(params.items())
            if value is not None
        }
        return sorted_not_none_params

    @staticmethod
    def _prepare_json_params(params):
        sorted_not_none_params = {
            key: value for key, value in sorted(params.items()) if value is not None
        }
        return sorted_not_none_params

    @staticmethod
    def _get_query_string(prepared_params: dict[str, str]) -> str:
        if len(prepared_params) == 0:
            return ""
        else:
            return "&".join(
                f"{key}={quote_plus(str(value))}"
                for key, value in prepared_params.items()
            )

    @staticmethod
    def _get_json_body(prepared_params: dict[str, str]) -> str:
        if prepared_params:
            return json.dumps(prepared_params, separators=(",", ":"))
        else:
            return ""

    def _get_v1_signature(self, time_ms: str, query_params_string: str) -> str:
        msg = f"{query_params_string}|{time_ms}"
        msg_bytes = bytes(msg, "utf-8")
        return (
            hmac.new(self._api_key_bytes, msg=msg_bytes, digestmod=hashlib.sha256)
            .hexdigest()
            .upper()
        )

    def _get_v3_signature(
        self,
        time_ms: str,
        method: str,
        request_path: str,
        query_params_string: str,
        json_body: str,
    ) -> str:
        if len(query_params_string) > 0:
            query_params_string = "?" + query_params_string
        msg = f"{time_ms}{method}{request_path}{query_params_string}{json_body}"
        msg_bytes = bytes(msg, "utf-8")
        return (
            hmac.new(self._api_key_bytes, msg=msg_bytes, digestmod=hashlib.sha256)
            .hexdigest()
            .upper()
        )

    def _get_headers(
        self,
        method: str,
        version: int,
        end_point: str,
        private: bool,
        request_path: str,
        query_params_string: str,
        json_body: str,
    ) -> dict[str, str]:
        if version == 1:
            content_type = "application/x-www-form-urlencoded"
        else:
            content_type = "application/json"

        if private:
            if (self._api_key is None) or (self._api_secret is None):
                raise ValueError(
                    f"API key and secret are required for the private endpoint {end_point}."
                )

            time_ms = str(int(time.time() * 1000))

            if version == 1:
                signature = self._get_v1_signature(time_ms, query_params_string)
            else:
                signature = self._get_v3_signature(
                    time_ms, method, request_path, query_params_string, json_body
                )

            return {
                "Content-Type": content_type,
                "x-api-key": self._api_key,
                "x-api-signature": signature,
                "x-api-timestamp": time_ms,
            }
        else:
            return {"Content-Type": content_type}

    def _get(self, version: int, end_point: str, private: bool, **params):
        _METHOD = "GET"
        prepared_params = self._prepare_query_params(params)
        query_params_string = self._get_query_string(prepared_params)

        request_path = self._get_request_path(version, end_point)
        headers = self._get_headers(
            _METHOD,
            version,
            end_point,
            private,
            request_path,
            query_params_string,
            "",
        )
        url = self._base_url + request_path
        if len(query_params_string) > 0:
            url += "?" + query_params_string

        response = requests.get(url, headers=headers)

        if not str(response.status_code).startswith("2"):
            raise WooClientError(response)

        return response.json()

    def _non_get_request(
        self, method: str, version: int, end_point: str, private: bool, **params
    ):
        if version == 1:
            prepared_params = self._prepare_query_params(params)
            query_params_string = self._get_query_string(prepared_params)
            json_body = ""
            body = query_params_string
        else:
            prepared_params = self._prepare_json_params(params)
            query_params_string = ""
            json_body = self._get_json_body(prepared_params)
            body = json_body

        request_path = self._get_request_path(version, end_point)
        headers = self._get_headers(
            method,
            version,
            end_point,
            private,
            request_path,
            query_params_string,
            json_body,
        )
        url = self._base_url + request_path

        response = requests.request(
            method,
            url,
            headers=headers,
            data=body,
        )

        if not str(response.status_code).startswith("2"):
            raise WooClientError(response)

        return response.json()

    def _post(self, version: int, end_point: str, private: bool, **params):
        return self._non_get_request("POST", version, end_point, private, **params)

    def _delete(self, version: int, end_point: str, private: bool, **params):
        return self._non_get_request("DELETE", version, end_point, private, **params)

    def get_public_info(self, symbol: str):
        return self._get(1, f"public/info/{symbol}", False)

    def get_kline(self, symbol: str, interval: str, limit: int = None):
        return self._get(1, "kline", True, symbol=symbol, type=interval, limit=limit)

    def get_balances(self):
        return self._get(3, "balances", True)

    def get_positions(self):
        return self._get(3, "positions", True)

    def get_orders(
        self,
        symbol: str = None,
        side: str = None,
        size: int = None,
        order_type: str = None,
        order_tag: str = None,
        realized_pnl: bool = False,
        status: str = None,
        start_t: float = None,
        end_t: float = None,
        page: int = None,
    ):
        return self._get(
            1,
            "orders",
            True,
            symbol=symbol,
            side=side,
            size=size,
            order_type=order_type,
            order_tag=order_tag,
            realized_pnl=realized_pnl,
            status=status,
            start_t=start_t,
            end_t=end_t,
            page=page,
        )

    def get_algo_orders(
        self,
        algo_type: str,
        symbol: str = None,
        side: str = None,
        size: int = None,
        order_type: str = None,
        realized_pnl: bool = False,
        status: str = None,
        created_time_start: float = None,
        created_time_end: float = None,
        is_triggered: bool = None,
        order_tag: str = None,
        page: int = None,
    ):
        return self._get(
            3,
            "algo/orders",
            True,
            algoType=algo_type,
            createdTimeEnd=created_time_end,
            createdTimeStart=created_time_start,
            isTriggered=is_triggered,
            orderTag=order_tag,
            page=page,
            realizedPnl=realized_pnl,
            side=side,
            size=size,
            status=status,
            symbol=symbol,
            orderType=order_type,
        )

    def post_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        client_order_id: str = None,
        order_tag: str = None,
        order_price: str = None,
        order_quantity: str = None,
        order_amount: str = None,
        reduce_only: bool = None,
        visible_quantity: str = None,
    ):
        self._post(
            1,
            "order",
            True,
            symbol=symbol,
            broker_id=self._application_id,
            client_order_id=client_order_id,
            order_tag=order_tag,
            order_type=order_type,
            order_price=order_price,
            order_quantity=order_quantity,
            order_amount=order_amount,
            reduce_only=reduce_only,
            visible_quantity=visible_quantity,
            side=side,
        )

    def post_algo_order(
        self,
        symbol: str,
        side: str,
        algo_type: str,
        order_type: str,
        activated_price: str = None,
        callback_rate: str = None,
        callback_value: str = None,
        child_orders: str = None,
        client_order_id: str = None,
        order_tag: str = None,
        order_price: str = None,
        order_quantity: str = None,
        reduce_only: bool = None,
        trigger_price: str = None,
        trigger_price_type: str = None,
        visible_quantity: str = None,
    ):
        self._post(
            3,
            "algo/order",
            True,
            activatedPrice=activated_price,
            algoType=algo_type,
            brokerId=self._application_id,
            callbackRate=callback_rate,
            callbackValue=callback_value,
            childOrders=child_orders,
            symbol=symbol,
            clientOrderId=client_order_id,
            orderTag=order_tag,
            price=order_price,
            quantity=order_quantity,
            reduceOnly=reduce_only,
            triggerPrice=trigger_price,
            triggerPriceType=trigger_price_type,
            type=order_type,
            visibleQuantity=visible_quantity,
            side=side,
        )

    def delete_order(self, order_id: int, symbol: str):
        return self._delete(1, "order", True, order_id=order_id, symbol=symbol)

    def delete_algo_order(self, order_id: int):
        return self._delete(3, f"algo/order/{order_id}", True)
