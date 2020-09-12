import pandas as pd
import os
import argparse
import src.cleaning as clean
import requests
from dotenv import load_dotenv
from pathlib import Path  
env_path = Path('/src') / '.env'
load_dotenv(dotenv_path=env_path)

def open_csv():

    """
    This function opens a cvs file from a folder in the project, in a shape of a pandas DataFrame
    No parameters are needed, except of the name and the folder the function will ask you
    """
    folder=input("Please, enter the folder where your cvs file is saved:\n")
    file=input('Please, enter the name for the cvs file you want to open without extension:\n')
    if folder=='input':
        return pd.read_csv(f'../{folder}/{file}.csv',encoding='latin-1')
    elif folder=='src':
        return pd.read_csv(f'{folder}/{file}.csv',encoding='latin-1')




def export_csv(df):
    """ 
    This function export a cvs file to src folder in the project.
    To use it, it needs one parameter:
    df:the DataFrame we are willing to export to cvs
    """
    name=input('Please, enter the name for the cvs file you want to export')
    df.to_csv(f"{name}.csv",index = False)
    return f"{name} has been exported to cvs file"


def onlyYears(minYear=1902, maxYear=2020):
    def wrapper(yearStr):
        year = 2020
        try:
            year = int(yearStr)
        except Exception:
            raise argparse.ArgumentTypeError(f"{yearStr} is an invalid positive int value")
        
        if year >= minYear and year <= maxYear:
            return year
        else:
            raise argparse.ArgumentTypeError(f"year must be between {minYear} and {maxYear}")
    return wrapper

def rangeAge(ages):    
    def wrapper(age):    
        if age in ages:
            return age
        else:
            raise argparse.ArgumentTypeError(f"Age parameter must be one out of the folowing ones: {ages}")
    return wrapper


def select_args(df,args):
    if args.age is None:
        if args.language is None:
            df=df[(df.Year==args.year) & (df.Country.str.contains(f'{args.country}', regex= True, na=False))]
        else:
            df=df[(df.Year==args.year) & (df.Country.str.contains(f'{args.country}')) & (df.Language.str.contains(f'{args.language}', regex= True, na=False))]
    else:
        if args.language is None:
            df=df[(df.Year==args.year) & (df.Age==args.age) & (df.Country.str.contains(f'{args.country}', regex= True, na=False))]

        else:
            df=df[(df.Year==args.year) & (df.Age==args.age) & (df.Country.str.contains(f'{args.country}')) & (df.Language.str.contains(f'{args.language}', regex= True, na=False))]
    
    print(df.head())             
    cuenta=df.index.value_counts().sum()
    print(f'{cuenta} movies matched with those filters')
    return df



def getUrl(query,api_key=os.getenv('NYT_APIKEY')):
    """
    This function gets information out of an API 

    """

    baseUrl='https://api.nytimes.com/svc/movies/v2/reviews'
    url = f"{baseUrl}/search.json?query={query}&api-key={api_key}"
    
    requestHeaders = {
    "Accept": "application/json"
  }

    response = requests.get(url, headers=requestHeaders)
    print(f"Requested data; status_code:{response.status_code}")
    data=response.json()
    return data

