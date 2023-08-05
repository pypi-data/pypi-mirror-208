import importlib
import pandas as pd
from kaiko_research.endpoint_schemas import endpoints_mapping

# from cerberus import Validator
from kaiko_research.utils import ParamsValidator

schemas = importlib.import_module("kaiko_research.endpoint_schemas")
endpoints_mapping = pd.DataFrame(endpoints_mapping)
endpoints_mapping = endpoints_mapping.set_index("data_endpoints")


class ReqUrlHandler:
    def initiate_endpoint(self, endpoint):
        try:
            self.url = endpoints_mapping.at[endpoint, "url"]
            self.suffix = endpoints_mapping.at[endpoint, "suffix"]
            self.data_type = endpoints_mapping.at[endpoint, "data_type"]
            self.schema_name = endpoints_mapping.at[endpoint, "schema_name"]
        except:
            raise ValueError(
                "Data endpoint provided does not exist in Kaiko API")

    def create_query(self, query):
        query_string = "?"
        query_string = query_string + "&".join(
            [f"{_}={query[_]}" for _ in query.keys()]
        )
        if query_string == "?":
            return ""
        return query_string

    def validate_and_split_parameters(self, parameters, schema):
        validator = ParamsValidator(schema, allow_unknown=True)
        if not validator.validate(parameters):
            raise ValueError(validator.errors)
        validated_parameters = validator.validated(parameters)
        query = {}
        non_query = {}
        for key, value in validated_parameters.items():
            if schema[key].get("part_of_query", True):
                query[key] = value
            else:
                non_query[key] = value
        return non_query, query

    def define_headers(self, api_key):
        headers = {
            "Accept": "application/json",
            "X-Api-Key": api_key,
        }
        return headers

    def construct_url(self, endpoint, parameters):
        self.initiate_endpoint(endpoint)
        url = self.url
        if self.schema_name != "":
            schema = getattr(schemas, self.schema_name)
            pms, query = self.validate_and_split_parameters(parameters, schema)
        if self.data_type in ["Trade data", "Order Book data", "Aggregates"]:
            suffix = self.suffix.format(
                pms["commodity"],
                pms["data_version"],
                pms["exchange"],
                pms["instrument_class"],
                pms["instrument"],
            )
        elif endpoint in ["Asset Price", "Cross Price"]:
            suffix = self.suffix.format(
                pms["data_version"], pms["base_asset"], pms["quote_asset"]
            )
        elif endpoint in ["Valuation", "OANDA FX Rates", "Value at Risk"]:
            suffix = self.suffix.format(pms["data_version"])
        else:
            suffix = self.suffix
        url += suffix
        if self.schema_name != "":
            url += self.create_query(query)
        return url

    def convert_date(self, date):
        # if it's already a string - convert to Pandas datetime format
        if type(date) == str:
            # print('Date is already a string')
            date = pd.to_datetime(date)
        return date.strftime("%Y-%m-%dT%H:%M:%SZ")
