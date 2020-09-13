import pandas as pd
import re
import os
import argparse
import src.cleaning as clean
#import cleaning as clean
import requests
from dotenv import load_dotenv
#from pathlib import Path  
#env_path = Path('/src') / '.env'
#load_dotenv(dotenv_path=env_path)
load_dotenv()

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
        #return pd.read_csv(f'{file}.csv',encoding='latin-1')


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



def get_url(args,api_key=os.getenv('NYT_APIKEY'),i=0):
    """
    This function gets information out of an API 

    """
    baseUrl='https://api.nytimes.com/svc/movies/v2/reviews'
    url = f"{baseUrl}/search.json?offset={20*i}&opening-date={args.year}-01-01%3B{args.year}-12-31&order=by-title&api-key={api_key}"

    requestHeaders = {
    "Accept": "application/json"
}
    
    response = requests.get(url, headers=requestHeaders)
    

    if response.status_code != 200:
        data=response.json()
        raise ValueError(f'Invalid NYTimes api call: {data["fault"]["faultstring"]}')
        
    else:
        print(f"Requested data to {baseUrl}; status_code:{response.status_code}")
        data=response.json()
        return data


def api_to_df(data):
    df=pd.DataFrame.from_dict(data['results'], orient='columns')
    clean.rename_columns(df)
    df=clean.drop_columns(df,['critics_pick','mpaa_rating','summary_short','opening_date','date_updated','multimedia'])
    df=df.rename(columns={"byline": "reviewer"})
    df=clean.capital_names(df,'reviewer')
    df=clean.special_characters(df,'headline')
    df=clean.special_characters(df,'display_title')
    df['link']=df['link'].map(lambda x: x['url'])
    print(df.head())
    return df

            

def merge_api_df(api,df):
    """This function merges the DataFrame took out of an API, and the original DataFrame coming from a csv file.
    First of all, it needs to compare movies' titles to find matches

    """
    for movie in list(df.Title):
        for review in list(api.display_title):
            res = re.findall(r"%s" % review,r"(.*)%s(.*)" % movie)
            if res:
                review=res[0]
    
    merged=df.merge(api, how='left', left_on='Title', copy=True, indicator=True)       
    return merged
