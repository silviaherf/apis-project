 #!/usr/bin/env python3
import sys
import argparse
import pandas as pd
import src.cleaning as clean


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



def main():
    df=pd.read_csv('src/movies1.csv',encoding='latin-1')
   
    minYear = df["Year"].min()
    maxYear = df["Year"].max()

    parser = argparse.ArgumentParser(description='Filter the imported dataset by selected values')
    parser.add_argument('-y', dest='year',
                        default=2015,       
                        type=onlyYears(minYear,maxYear),
                        help="Selected year")
    
    parser.add_argument('-l', dest='language',             
                        type=str,
                        help="Selected director")

    
    parser.add_argument('-a', dest='age',
                        type=str,
                        help="Selected age recommendation")

    parser.add_argument('-c', dest='country',  
                        default='United States',
                        type=str,
                        help="Selected country")
                      

    args = parser.parse_args()
   
    if args.age is None:
        if args.language is None:
            print(df[(df.Year==args.year) & (df.Country.str.contains(f'{args.country}', regex= True, na=False))].head())
            cuenta=df[(df.Year==args.year)  & (df.Country.str.contains(f'{args.country}', regex= True, na=False))].index.value_counts().sum()

        else:
            print(df[(df.Year==args.year) & (df.Country.str.contains(f'{args.country}')) & (df.Language.str.contains(f'{args.language}', regex= True, na=False))].head())
            cuenta=df[(df.Year==args.year) & (df.Country.str.contains(f'{args.country}')) & (df.Language.str.contains(f'{args.language}', regex= True, na=False))].index.value_counts().sum()
    else:
        if args.language is None:
            print(df[(df.Year==args.year) & (df.Age==args.age) & (df.Country.str.contains(f'{args.country}', regex= True, na=False))].head())
            cuenta=df[(df.Year==args.year) & (df.Age==args.age) & (df.Country.str.contains(f'{args.country}', regex= True, na=False))].index.value_counts().sum()
        else:
            print(df[(df.Year==args.year) & (df.Age==args.age) & (df.Country.str.contains(f'{args.country}')) & (df.Language.str.contains(f'{args.language}', regex= True, na=False))].head())
            cuenta=df[(df.Year==args.year) & (df.Age==args.age) & (df.Country.str.contains(f'{args.country}')) & (df.Language.str.contains(f'{args.language}', regex= True, na=False))].index.value_counts().sum()
    
    return print(f'{cuenta} movies matched with those filters')

if __name__ == "__main__":
    main()