import pandas as pd
import requests
import json
import zipfile

# Get Institutions
with zipfile.ZipFile("data/input.zip") as z:
    with z.open("input/fdic/cert_nums.csv") as f:
        banks_id = pd.read_csv(f)

url= "https://banks.data.fdic.gov/api/financials"
output = [["CERT", "DEP", "DEPINS", "ASSETS"]]
for bank in banks_id['fdic_cert_num']:
    cert_num = int(bank)
    print(bank)
    params = dict(
        filters    = "CERT:%d" % cert_num,
        fields     = "CERT,REPDTE,ASSET,DEP,DEPINS",
        sort_by    = "REPDTE",
        sort_order = "DESC",
        limit      = 10000,
        offset     = 0,
        agg_term_fields = "REPDTE",
        agg_sum_fields  = "ASSET,DEP,DEPINS",
        agg_limit       = 1
    )
    resp = requests.get(url=url, params = params)
    data = resp.json()
    try:
        output.append([data["data"][0]["data"][x] 
                          for x in ["CERT","DEP","DEPINS", "ASSET"]])
    except:
        pass

bank_data_final = (pd.DataFrame(output[1:], 
                                columns = ["CERT", "DEP", "DEPINS", "ASSETS"])
                   .merge(right=banks_id, 
                         left_on = "CERT", right_on = "fdic_cert_num"))

bank_data_final.to_csv("../data/input/fdic/bank_deposits.csv")
