import pandas as pd 

def open_cvs():

    """
    This function opens a cvs file from src folder in the project, in a shape of a pandas DataFrame
    No parameters are needed, except of the name and the folder the function will ask you
    """
    folder=input("Please, enter the folder where your cvs file is saved:\n")
    file=input('Please, enter the name for the cvs file you want to open without extension:\n')

    return pd.read_csv(f'../{folder}/{file}.csv')


