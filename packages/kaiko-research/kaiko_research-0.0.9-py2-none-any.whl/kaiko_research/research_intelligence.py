from kaiko_research.api_client import DataAPIClient
from kaiko_research.request_handler import ReqUrlHandler


class ApplyResearchIntelligence(DataAPIClient):
    def __init__(self, api_key, req_data={}):
        self.api = api_key
        self.params = req_data
        self.req_handler = ReqUrlHandler()
        self.headers = self.req_handler.define_headers(api_key)

        pass

    def preprocess_params(self, df_params, cols_init, cols_params):
        params = [
            {cols_params[i]: row[i] for i in range(len(cols_params))}
            for ind, row in df_params[cols_init].dropna().drop_duplicates().iterrows()
        ]
        return params

    def exchange_volume_usd(self):
        params = self.params.copy()
        for item in ["start_time", "end_time"]:
            if item in self.params.keys():
                del self.params[item]
        instruments_url = self.treat_request_data("Instruments")
        instruments = self.fetch_raw_data(instruments_url)
        instruments = instruments.loc[instruments["class"] == "spot"].reset_index(
            drop=True
        )
        instruments = instruments.loc[
            instruments["exchange_code"].str.contains(
                "|".join(self.params["exchange"]))
        ]
        ohlcvs_params = self.preprocess_params(
            instruments, ["exchange_code", "code"], ["exchange", "instrument"]
        )
        for item in ["start_time", "end_time"]:
            if item in params.keys():
                self.params[item] = params[item]
        self.params["page_size"] = 100000
        volume_data = self.fetch_data_batches(
            "Count-OHLCV-VWAP", ohlcvs_params)
        volume_data[["base_asset", "quote_asset"]] = volume_data.instrument.str.split(
            "-", expand=True
        )
        volume_data = volume_data.rename(columns={"index": "timestamp"})

        instruments["code"] = instruments["code"].str.replace("-.*", "-usd")
        del self.params["exchange"]
        del self.params["instrument"]
        asset_price_params = self.preprocess_params(
            instruments, ["code"], ["instrument"]
        )
        asset_price_params = [
            {
                "base_asset": _["instrument"].split("-")[0],
                "quote_asset": _["instrument"].split("-")[1],
            }
            for _ in asset_price_params
        ]
        self.params["page_size"] = 1000
        asset_price_data = self.fetch_data_batches(
            "Cross Price", asset_price_params)
        asset_price_data = asset_price_data.rename(
            columns={"price": "usd_price"})
        usd_price_map = asset_price_data.set_index(["timestamp", "base_asset"])[
            "usd_price"
        ].to_dict()
        volume_data["usd_price"] = volume_data.apply(
            lambda row: usd_price_map.get((row["timestamp"], row["base_asset"])), axis=1
        )
        volume_data["volume_usd"] = volume_data["volume"].astype(float) * volume_data[
            "usd_price"
        ].astype(float)

        return volume_data
