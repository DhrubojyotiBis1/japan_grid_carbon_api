import copy
import logging
import pandas as pd
from google.cloud import storage
from google.cloud import bigquery
from google.api_core import retry

import utilities.tepco.analysis.tepco_carbon_intensity as tci

cache = {}


def _get_intensity_query_string(utility):
    carbonIntensity = tci.getCarbonIntensityFactors()

    return """
    AVG((
        (daMWh_nuclear * {intensity_nuclear}) + 
        (daMWh_fossil * {intensity_fossil}) + 
        (daMWh_hydro * {intensity_hydro}) + 
        (daMWh_geothermal * {intensity_geothermal}) + 
        (daMWh_biomass * {intensity_biomass}) +
        (daMWh_solar_output * {intensity_solar_output}) +
        (daMWh_wind_output * {intensity_wind_output}) +
        (daMWh_pumped_storage * {intensity_pumped_storage}) +
        (daMWh_interconnectors * {intensity_interconnectors}) 
        ) / daMWh_total
        ) as carbon_intensity
    FROM japan-grid-carbon-api.{utility}.historical_data_by_generation_type
    """.format(
        utility=utility,
        intensity_nuclear=carbonIntensity["kWh_nuclear"],
        intensity_fossil=carbonIntensity["kWh_fossil"],
        intensity_hydro=carbonIntensity["kWh_hydro"],
        intensity_geothermal=carbonIntensity["kWh_geothermal"],
        intensity_biomass=carbonIntensity["kWh_biomass"],
        intensity_solar_output=carbonIntensity["kWh_solar_output"],
        intensity_wind_output=carbonIntensity["kWh_wind_output"],
        intensity_pumped_storage=carbonIntensity["kWh_pumped_storage"],
        intensity_interconnectors=carbonIntensity["kWh_interconnectors"]
    )


def _extract_daily_carbon_intensity_from_big_query(utility):

    query = """
    SELECT
    EXTRACT(HOUR FROM datetime) AS hour,
    """ + _get_intensity_query_string(utility) + """
    GROUP BY hour
    order by hour asc
    """

    return pd.read_gbq(query)


def _extract_daily_carbon_intensity_by_month_from_big_query(utility):

    query = """
    SELECT
    EXTRACT(MONTH FROM datetime) AS month,
    EXTRACT(HOUR FROM datetime) AS hour,
    """ + _get_intensity_query_string(utility) + """
    GROUP BY month, hour
    order by month, hour asc
    """

    return pd.read_gbq(query)


def _extract_daily_carbon_intensity_by_month_and_weekday_from_big_query(utility):

    query = """
    SELECT
    EXTRACT(MONTH FROM datetime) AS month,
    EXTRACT(DAYOFWEEK FROM datetime) AS dayofweek,
    EXTRACT(HOUR FROM datetime) AS hour,
    """ + _get_intensity_query_string(utility) + """
    GROUP BY month, dayofweek, hour
    order by month, dayofweek, hour asc
    """

    return pd.read_gbq(query)


def daily_intensity():
    # Check Cache
    if "_tepco_daily_intensity" in cache:
        print("Returning cache._tepco_daily_intensity:")
        return cache["_tepco_daily_intensity"]

    df = _extract_daily_carbon_intensity_from_big_query("tepco")

    df.reset_index(inplace=True)

    output = {"carbon_intensity_by_hour": df[[
        'hour', 'carbon_intensity']].to_dict("records"),
        "fromCache": True}

    # Populate Cache
    cache['_tepco_daily_intensity'] = copy.deepcopy(output)
    output["fromCache"] = False
    return output


def daily_intensity_by_month():
    # Check Cache
    if "_tepco_daily_intensity_by_month" in cache:
        print("Returning cache._tepco_daily_intensity_by_month:")
        return cache["_tepco_daily_intensity_by_month"]

    df = _extract_daily_carbon_intensity_by_month_from_big_query("tepco")

    df.reset_index(inplace=True)

    output = {
        "carbon_intensity_by_month": df.groupby('month')
        .apply(
            lambda month: month[['hour', 'carbon_intensity']]
            .to_dict(orient='records')
        ).to_dict(),
        "fromCache": True
    }

    # Populate Cache
    cache['_tepco_daily_intensity_by_month'] = copy.deepcopy(output)
    output["fromCache"] = False
    return output


def daily_intensity_by_month_and_weekday():
    # Check Cache
    if "_tepco_daily_intensity_by_month_and_weekday" in cache:
        print("Returning cache._tepco_daily_intensity_by_month_and_weekday:")
        return cache["_tepco_daily_intensity_by_month_and_weekday"]

    df = _extract_daily_carbon_intensity_by_month_and_weekday_from_big_query(
        "tepco")

    df.reset_index(inplace=True)

    output = {
        "carbon_intensity_by_month_and_weekday": df.groupby('month')
        .apply(
            lambda month: month.groupby('dayofweek').apply(
                lambda day: day[['hour', 'carbon_intensity']]
                .to_dict(orient='records')
            ).to_dict()
        ).to_dict(),
        "fromCache": True
    }

    # Populate Cache
    cache['_tepco_daily_intensity_by_month_and_weekday'] = copy.deepcopy(
        output)
    output["fromCache"] = False
    return output
