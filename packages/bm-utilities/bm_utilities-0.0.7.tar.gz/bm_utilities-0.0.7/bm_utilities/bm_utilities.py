from Address_finder import AddressFinder as af
import geopandas as gpd
import pandas as pd
def address_finder(geodf,address):
    construct = af.AddressFinder(geodf)
    address = af.find_address(address)
    return address
