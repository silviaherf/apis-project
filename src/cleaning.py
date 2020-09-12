import pandas as pd 
import re


def rename_columns(df):
    """ 
    This function checks the name of the columns in a DataFrame and replace blank spaces with "_".
    The only argument needed is df:the DataFrame
    """
    actual_col={}
    for column in df.columns:
        actual_col[column]=column.replace(r" ","_")
    df=df.rename(columns = actual_col, inplace = True)
    return df

def drop_columns(df,*columns):
    """ 
    This function drop from the DataFrame the selected columns.
    The arguments needed are 
    df:the DataFrame 
    columns*:the columns we want to drop. It accept columns as needed; just enter them as string separated by comma ","
    """
    for column in columns:
        df=df.drop(column,axis=1)
    return df


def rounding(df):
    """
    This function rounds every numerical column in a DataFrame to 2 decimals.
    The only argument needed is df:the DataFrame
    """
    for column in df.select_dtypes(include=['int','float']).columns:
        df[column]=df[column].map(lambda x:round(x,2))
    return df

def rounding_value(num):
    """
    This function rounds a numerical value to 2 decimals.
    The only argument needed is num:the value we want to round
    """

    return  round(num,2)

def white_spaces(df,column):
    """
    This function removes every white space in the selected column in a DataFrame.
    The two arguments needed are:
    df:the DataFrame
    column:the column from the dataFrame as a string
    """

    df[column]=df[column].map(lambda x: "".join(x.split()))

    return df   

def convert_integer(df,column):
    """
    This function changes the type of values of a column in a DataFrame to integer.
    The two arguments needed are:
    df:the DataFrame
    column:the column from the dataFrame as a string
    """
    df[column]=df[column].map(lambda x: int(x))
    return df   

