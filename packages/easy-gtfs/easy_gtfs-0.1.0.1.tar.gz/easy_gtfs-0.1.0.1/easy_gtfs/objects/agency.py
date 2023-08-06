
from pydantic import BaseModel, validator
from typing import Optional
from urllib.parse import urlparse


class Agency(BaseModel):
    """
        https://developers.google.com/transit/gtfs/reference#agencytxt

        :param id [Optional[str]] -- The unique id for this agency (only needed if multiple agencies are present in the dataset)
        :param name [str] -- The full name of the agency
        :param url [str] -- The url of the agency
        :param timezone [str] -- The timezone of the agency (if multiple agencies in this dataset, all must have the same timezone)
        :param lang [Optional[str]] -- The primary language this agency uses
        :param phone [Optional[str]] -- A phone number for the agency
        :param fare_url [Optional[]] -- The website on which travellers can buy tickets to travel with this agency
        :param email [Optional[str]] -- An email address to reach the agency (should be the support email address of the agency or another email which is actively used by the agency)
    """
    agency_id: Optional[str] = ""
    agency_name: str
    agency_url: str
    agency_timezone: str
    agency_lang: Optional[str] = ""
    agency_phone: Optional[str] = ""
    agency_fare_url: Optional[str] = ""
    agency_email: Optional[str] = ""


    @validator("agency_url")
    def is_agency_url_valid(cls, url):
        if isinstance(url, str):      
            # https://stackoverflow.com/a/52455972/21595907
            try:
                result = urlparse(url)
                if all([result.scheme, result.netloc]):
                    return url

            except ValueError:
                # ValueError can happen if an invalid ip (v4, v6) or a byte object has been passed
                return ValueError("must be a valid url")
        
        raise ValueError("must be a valid url")
    

    @validator("agency_fare_url")
    def is_agency_fare_url_valid(cls, url):
        if isinstance(url, str):
            if len(url) < 1: # url is empty and we can accept that (mainly for when parsing from file)
                return url
            
            # https://stackoverflow.com/a/52455972/21595907
            try:
                result = urlparse(url)
                if all([result.scheme, result.netloc]):
                    return url

            except ValueError:
                # ValueError can happen if an invalid ip (v4, v6) or a byte object has been passed
                return ValueError("must be a valid url")
        
        raise ValueError("must be a valid url")


