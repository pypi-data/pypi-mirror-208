#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 17:39:58 2023

@author: evgenijrabcenkov
"""
from kaiko_research.request_handler import ReqUrlHandler
import itertools
from kaiko_research.utils import flatten_dataframe
import dask.bag as db
from tqdm import tqdm
import pandas as pd
import requests


class DataAPIClient:
    def __init__(self, api_key, req_data={}):
        self.api = api_key
        self.params = req_data
        self.req_handler = ReqUrlHandler()
        self.headers = self.req_handler.define_headers(api_key)

    # General functions to process request parameters and response
    def treat_request_data(self, endpoint, params={}):
        return self.req_handler.construct_url(endpoint, params)

    def combine_lists_of_params(self, fields, lists_of_params):
        product_lists_of_params = itertools.product(*lists_of_params)
        final_list = []
        for product in product_lists_of_params:
            obj = {}
            for i, item in enumerate(product):
                obj[fields[i]] = item
            final_list.append(obj)
        return final_list

    def treat_inputs(self):
        list_params = []
        fields = []
        for item in [
            "instrument",
            "exchange",
            "asset",
            "base_asset",
            "quote_asset",
        ]:
            if item in self.params.keys():
                fields.append(item)
                list_params.append(self.params[item])
                del self.params[item]
        if len(list_params) > 0:
            flattened_list_params = self.combine_lists_of_params(
                fields, list_params)
            return flattened_list_params
        return list_params

    def fetch_raw_data(self, url, params={}):
        response = requests.get(url, headers=self.headers).json()
        res_data = response["data"]
        while (response.get("next_url") is not None) & (response["data"] != []):
            response = requests.get(
                response["next_url"], headers=self.headers).json()
            res_data = res_data + response["data"]
        data_res = pd.DataFrame()
        try:
            data_res = pd.DataFrame(res_data)
            for item in [
                "instrument",
                "exchange",
                "asset",
                "base_asset",
                "quote_asset",
            ]:
                if item in params.keys():
                    data_res[item] = params[item]
        except ValueError as ve:
            print(
                f"error in generating dataset {ve} the response that you are getting:"
            )
            print(response)
        return data_res

    def fetch_data_batches(self, endpoint, list_of_parameters=[]):
        if len(list_of_parameters) == 0:
            list_of_parameters = self.treat_inputs()
        if len(list_of_parameters) == 0:
            self.url = self.treat_request_data(endpoint, self.params)
            data = self.fetch_raw_data(self.url)
        else:
            urls = []
            data = pd.DataFrame()
            # list_of_parameters = list_of_parameters[0:10]
            for param in tqdm(list_of_parameters, "Generating URLs..."):
                for key in param.keys():
                    self.params[key] = param[key]
                url = []
                self.url = self.treat_request_data(endpoint, self.params)
                url += [self.url]
                url += [param.copy()]
                urls.append(url)
            chunks = [urls[i: i + 5000] for i in range(0, len(urls), 5000)]
            for i, chunk in enumerate(tqdm(chunks, "Fetching data in batches...")):
                bag = db.from_sequence([(url[0], url[1]) for url in chunk]).map(
                    lambda x: self.fetch_raw_data(*x)
                )
                try:
                    data_chunk = bag.compute()
                    data_chunk = pd.concat(data_chunk).reset_index(drop=True)
                except Exception as e:
                    print(f"Error occurred while fetching data: {e}")
                    return None
                data = pd.concat([data, data_chunk]).reset_index(drop=True)
        # data = flatten_dataframe(data)
        return data
