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
    #print(args)
    df=pd.read_csv('src/movies1.csv',encoding='latin-1')
    #df=clean.open_csv()
   
    minYear = df["Year"].min()
    maxYear = df["Year"].max()

    parser = argparse.ArgumentParser(description='Filter the imported dataset by selected values')
    parser.add_argument('-y', dest='year',
                        default=2020,       
                        type=onlyYears(minYear,maxYear),
                        help="Selected year")
    
    parser.add_argument('-d', dest='director',                    
                        type=str,
                        help="Selected director")

    
    parser.add_argument('-a', dest='age',
                        default='7+',
                        type=str,
                        help="Selected age recommendation")

    parser.add_argument('-c', dest='country',
                        default='United States',
                        type=str,
                        help="Selected country")
                      

    args = parser.parse_args()
    if args.director:
        print(df[(df.Year==args.year) & (df.Directors==args.director) & (df.Age==args.age) & (df.Country==args.country)].head())
    else:
        print(df[(df.Year==args.year) & (df.Age==args.age) & (df.Country==args.country)].head())






if __name__ == "__main__":
    main()