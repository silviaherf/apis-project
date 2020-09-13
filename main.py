 #!/usr/bin/env python3
import sys
import pandas as pd
import src.cleaning as clean
import src.manipulating  as man
import argparse
import requests

def main():
  
    movies=pd.read_csv('src/movies.csv',encoding='latin-1')
    ages=movies['Age'].unique()
    minYear =movies["Year"].min()
    maxYear =movies["Year"].max()

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
    man.select_args(movies,args)
    response=man.get_url(args)
    reviews=man.api_to_df(man.get_url(args))
    #man.merge_api_df(reviews,movies)

    i=1
    while response['has_more']==True:
        try:
            man.get_url(args)
            print(f'Loading page {i+1}')
            reviews=man.api_to_df(man.get_url(args,i=i))
            #movies=man.merge_api_df(reviews,movies)
            i+=1
        except ValueError:
            break
    #print(movies.head())

    
      

        
    

if __name__ == "__main__":
    main()
