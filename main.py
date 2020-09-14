 #!/usr/bin/env python3
import sys
import pandas as pd
import src.cleaning as clean
import src.manipulating  as man
import argparse
import requests
import matplotlib.pyplot as plt
import src.pdf as pdf
import dataframe_image as dfi


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
                        help="Selected language")

    
    parser.add_argument('-a', dest='age',
                        type=man.rangeAge(ages),
                        help="Selected age recommendation")

    parser.add_argument('-c', dest='country',  
                        default='United States',
                        type=str,
                        help="Selected country")
                      

    args = parser.parse_args()
    selected_movies=man.select_args(movies,args)
    response=man.get_url(args)
    reviews=man.api_to_df(man.get_url(args))
    i=1
    while response['has_more']==True:
        try:
            print(f'Loading page {i+1}')
            reviews=reviews.append(man.api_to_df(man.get_url(args,i=i))).reset_index()
            i+=1
        except ValueError:
            break

    print(reviews.head(20))

    merged=man.merge_api_df(reviews,selected_movies)
    print(merged.head(20))


    print('Now, we will take some conclusions out of our movies dataset')

    n_reviews=merged[~merged['reviewer'].isnull()]['reviewer'].value_counts().sum()
    n_movies=merged['Title'].value_counts().sum()

    print(f'There are just{n_reviews} out of {n_movies} movies with a published review.')
    
    movies_age=movies.groupby('Age').agg({'Netflix':'sum','Hulu':'sum','Prime_Video':'sum','Disney+':'sum'}).sort_values(by='Age',ascending=False)
    dfi.export(movies_age, 'output/movies_age.png')
    man.print_to_stdout(movies_age) 

    age_plot=movies_age.plot(kind='pie', subplots=True, title='Number of movies in each platform by recommended Age',figsize=(16,8))
    plt.savefig('output/age.png')
    
    movies_years=movies[(movies['Year']<2021) & (movies['Year']>2000)].groupby('Year').agg({'Title':'count'})
    dfi.export(movies_years, 'output/movies_years.png')
    man.print_to_stdout(movies_years) 

    years_plot=movies_years.plot.bar(xlabel='Year',ylabel='Number of movies',title='Recorded movies per year between 2000-2020')
    plt.savefig('output/years.png')

    #pdf.export_pdf(movies_age,Age_plot,movies_years,years_plot)

    
    #man.send_mail('output/file.txt')

if __name__ == "__main__":
    main()
