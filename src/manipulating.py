import pandas as pd
import re
from difflib import SequenceMatcher
import sys
import os
import argparse
import src.cleaning as clean
#import cleaning as clean
import requests
import webbrowser
import smtplib, ssl
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
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
        return pd.read_csv(f'{file}.csv',encoding='latin-1')
       


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
    df=clean.special_characters(df,'headline','display_title')
    df['link']=df['link'].map(lambda x: x['url'])
    return df

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()           

def merge_api_df(api,df):
    """This function merges the DataFrame took out of an API, and the original DataFrame coming from a csv file.
    First of all, it needs to compare movies' titles to find matches, and then, substitute the original title from the API from the one in movie

    """
    
    for movie in list(df.Title):
        for review in list(api.display_title):
            match=similar(review,movie)
            if match>=0.7:
                api['display_title'] = api['display_title'].replace(review,movie)

    merged=pd.merge(left=df,right=api, how='left', left_on='Title', right_on='display_title')   
    return merged

def open_url(title,merged):
    if title=="q":
        pass
    else:
        df=merged[merged['Title']==f'{title}']
        url=list(df['link'])[0]
        return webbrowser.open(url)

def print_to_stdout(*a): 
  
    # Here a is the array holding the objects 
    # passed as the arguement of the function 
    print(*a, file = sys.stdout) 

def send_mail(file,sender_email='silviaherf@gmail.com',receiver_email='silviaherf@gmail.com',password=os.getenv('GMAIL_PASS')):  
    port = 465 

    subject = "Apis-project report"
    body = "This is an email with apis-project report attached"

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = "file.txt"  # In same directory as script

    # Open PDF file in binary mode
    with open(file, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Create a secure SSL context
    context = ssl.create_default_context()

        
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, context=context)
        server.ehlo()
        server.login(sender_email,password)
        server.sendmail(sender_email, receiver_email, message)
        server.close()
        return 'Email was sent'


    except:
        print('Something went wrong...')
    






