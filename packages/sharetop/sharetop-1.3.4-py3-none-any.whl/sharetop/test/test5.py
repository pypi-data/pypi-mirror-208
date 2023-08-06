from sharetop.core.country.country_base_info import get_country_base_info
from sharetop.core.oil.oil_detail import get_oil_reserves, get_oil_products, get_oil_consumption, \
    get_oil_refinerythroughput, get_oil_refinerycapacity, get_oil_crudeoilpricehistory
from sharetop.core.pig.pig_detail import get_fcr

# d = get_country_base_info()
# d = get_oil_crudeoilpricehistory()
d = get_fcr('2023-05-01', '2023-05-16')
# d = get_country_base_info(10)
# d = get_oil_crudeoilpricehistory(20)
print(d)
