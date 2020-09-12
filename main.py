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
    df=clean.open_csv()
   
    minYear = df["Year"].min()
    maxYear = df["Year"].max()

    parser = argparse.ArgumentParser(description='Filter the imported dataset by selected values')
    parser.add_argument('-y', dest='year',
                        default=2020,
                        type=onlyYears(minYear,maxYear),
                        help="Selected year")
    """
     parser.add_argument('-d', dest='director',
                        default=2015,
                        type=onlyYears(minYear,maxYear),
                        help="Año seleccionado")
    parser.add_argument('-y', dest='year',
                        default=2015,
                        type=onlyYears(minYear,maxYear),
                        help="Año seleccionado")
    parser.add_argument('-y', dest='year',
                        default=2015,
                        type=onlyYears(minYear,maxYear),
                        help="Año seleccionado")
                        """

    args = parser.parse_args()

    print(df[df.Year==args.year].head())





if __name__ == "__main__":
    main()