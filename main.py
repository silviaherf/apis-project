 #!/usr/bin/env python3
import sys
import pandas as pd
import src.cleaning as clean
import src.manipulating  as man
import argparse
import requests

def main():
  
    df=pd.read_csv('src/movies.csv',encoding='latin-1')
    ages=df['Age'].unique()
    minYear = df["Year"].min()
    maxYear = df["Year"].max()

    parser = argparse.ArgumentParser(description='Filter the imported dataset by selected values')
    parser.add_argument('-y', dest='year',
                        default=2015,       
                        type=man.onlyYears(minYear,maxYear),
                        help="Selected year")
    
    parser.add_argument('-l', dest='language',             
                        type=str,
                        help="Selected director")

    
    parser.add_argument('-a', dest='age',
                        type=man.rangeAge(ages),
                        help="Selected age recommendation")

    parser.add_argument('-c', dest='country',  
                        default='United States',
                        type=str,
                        help="Selected country")
                      

    args = parser.parse_args()
    man.select_args(df,args)
    man.get_url(args)
    reviews=man.api_to_df(man.get_url(args))

    i=1
    while reviews['has_more']==True:
        try:
            man.get_url(args)
            print(f'Loading page {i+1}')
            reviews=man.api_to_df(man.get_url(args,i=i))
            i+=1


        except ValueError:
            break
      

        
    

if __name__ == "__main__":
    main()
