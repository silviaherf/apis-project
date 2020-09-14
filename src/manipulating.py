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
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.message import EmailMessage
from email.policy import SMTP
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
    """
    This function checks if the entered year is an integer, and tries to convert it in case it is a proper string (with 4 characters).
    Otherwise, raises an error

    """
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
    """
    This function checks if the entered year is among the reported years in the dataset.

    """  
    def wrapper(age):    
        if age in ages:
            return age
        else:
            raise argparse.ArgumentTypeError(f"Age parameter must be one out of the folowing ones: {ages}")
    return wrapper


def select_args(df,args):
    """
    This function takes the arguments entered to the terminal, and returns a dataFrame with those arguments as filters

    """  
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
    This function gets information out of an API for the year previously entered as a terminal argument.

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
    """
    This function transforms the information from the API to a dataFrame. It also make some cleaning operations. It just needs the
    return of a get_url function. 

    """
    df=pd.DataFrame.from_dict(data['results'], orient='columns')
    clean.rename_columns(df)
    df=clean.drop_columns(df,['critics_pick','mpaa_rating','summary_short','opening_date','date_updated','multimedia'])
    df=df.rename(columns={"byline": "reviewer"})
    df=clean.capital_names(df,'reviewer')
    df=clean.special_characters(df,'headline','display_title')
    df['link']=df['link'].map(lambda x: x['url'])
    return df

def similar(a, b):
    """
    This function matches from 0 to 1 the similarity of two strings. The parameters it needs are those two strings.

    """
    return SequenceMatcher(None, a, b).ratio()           

def merge_api_df(api,df):
    """
    This function merges a dataFrame (in fact, the return for the api_to_df function) , and another DataFrame, in this case coming from a csv file.
    First of all, it needs to compare movies' titles to find matches, and then, substitute the original title from the API from the one in movie.
    The parameters are the two dataFrames: the right-to-be-joined one, and the left-to-be-joined one.

    """
    
    for movie in list(df.Title):
        for review in list(api.display_title):
            match=similar(review,movie)
            if match>=0.7:
                api['display_title'] = api['display_title'].replace(review,movie)

    merged=pd.merge(left=df,right=api, how='left', left_on='Title', right_on='display_title')   
    return merged

def open_url(title,merged):
    """
    This function opens a review url in your default browser.
    It need two parameters:
    -title: the title of the movie 
    -merged: the return of mer_api_df function (dataFrame)
    You can cancell this function by entering "q"
    """
    if title=="q":
        pass
    else:
        df=merged[merged['Title']==f'{title}']
        url=list(df['link'])[0]
        return webbrowser.open(url)

def print_to_stdout(*a): 
    """
    This function prints information in the terminal. It accepts as arguments as needed.
    E.g. the name of a dataframe, a filtered, table, etc.

    """
  

    print(*a, file = sys.stdout) 



def send_mail(file,sender_email='silviaherf@gmail.com',receiver_email='silviaherf@gmail.com',password=os.getenv('GMAIL_PASS')):  
    """
    This function sends a pdf attachment to the a selected mail account. The parameters needed are:
    -file: the attachament, a .pdf file
    -sender_email: the account where the mail will be sent. Optional, mine by default
    -receiver_email: optional, mine by default
    -password: the sign in password for the account where the mail will be sent. Optional, mine by default

    """
    port = 465 
    subject = "Apis-project report"
    body = "This is an email with apis-project report attached"

    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "Here is the exported report with the conclusions from the datasets"))

    filename = "output/report.pdf"  

    with open(filename, "rb") as attachment: 
        attachment_opened = attachment.read()

    data = MIMEApplication(attachment_opened, _subtype = "pdf", _encoder =encoders.encode_base64)
    data.add_header('content-disposition', 'attachment', filename = filename)
    message.attach(data)

    text = message.as_string()

 
    ctx=ssl.create_default_context()
       
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ctx)
        server.ehlo()
        server.login(sender_email,password)
        server.sendmail(sender_email, receiver_email, text)
        server.close()
        return print('Email was succesfully sent')


    except Exception as e:
        print(f'Something went wrong...{e}')
    
  





