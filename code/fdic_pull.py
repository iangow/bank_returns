import pandas as pd
import requests
import json
import zipfile

# Get Institutions
with zipfile.ZipFile("data/input.zip") as z:
    with z.open("input/fdic/cert_nums.csv") as f:
        banks_id = pd.read_csv(f)

import requests

def get_bank_data(certs):
    url = "https://banks.data.fdic.gov/api/financials"

    cert_filter = " OR ".join(f"CERT:{c}" for c in certs)
    repdte_filter = "REPDTE:20211231"

    filter_expr = f"({cert_filter}) AND {repdte_filter}"
    
    params = dict(
        filters  = filter_expr,
        fields     = "CERT,REPDTE,ASSET,DEP,DEPINS",
        sort_by    = "REPDTE",
        sort_order = "DESC",
        limit      = 10000,
        offset     = 0,
        agg_term_fields = "REPDTE",
        agg_sum_fields  = "ASSET,DEP,DEPINS",
        agg_limit       = 1
    )
    
    resp = requests.get(url, params=params)
    resp.raise_for_status()

    data = resp.json()["data"]
    return data


certs = banks_id["fdic_cert_num"].to_list()

bank_data = (
    pd.DataFrame(d['data'] for d in get_bank_data(certs))
    .rename(columns={"ASSET": "ASSETS"})
    .sort_values(["CERT", "REPDTE"])
    .drop_duplicates("CERT", keep="last")
    [["CERT", "DEP", "DEPINS", "ASSETS"]]
    .reset_index(drop=True)
)

bank_data_final = (bank_data
    .merge(right=banks_id, 
           left_on = "CERT", right_on = "fdic_cert_num")
    .sort_values(["CERT", "ID_RSSD_PARENT"])
)

bank_data_final.to_csv("data/input/fdic/bank_deposits.csv")
