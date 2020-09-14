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
    print('This is a piece of the list of movies with your filters:')
    selected_movies=man.select_args(movies,args)
    print("Now, let's have some reviews information from the New York Times Movie reviews API.")
    response=man.get_url(args)
    print('Loading page 1')
    reviews=man.api_to_df(response)
    i=1
    while response['has_more']==True:
        try:
            print(f'Loading page {i+1}')
            reviews=reviews.append(man.api_to_df(man.get_url(args,i=i))).reset_index()
            i+=1
        except ValueError:
            break
    
    print('This is a piece of the reviews information:')
    print(reviews.head(10))
    print('And this is the merged table from both movies and reviews:')
    merged=man.merge_api_df(reviews,selected_movies)
    print(merged.head(10))


    print('Now, we will take some conclusions out of our movies dataset')
    n_reviews=merged[~merged['reviewer'].isnull()]['reviewer'].value_counts().sum()
    n_movies=merged['Title'].value_counts().sum()
    movies_with_reviews=list(merged[~merged['reviewer'].isnull()]['Title'])
    if n_reviews==0:
        print('There are no reviews to show with the entered filters, sorry.')
    else:
        print(f'There are just {n_reviews} out of {n_movies} movies with a published review.')
        print('Would you like to open one of them?:\nThey are the following ones:\n',movies_with_reviews)
        title=''
        title=input(f'If yes, insert one of the titles above: {title}. Otherwise, call "q"\n')
        man.open_url(title,merged)
    
    print("The next table summarizes the movies recorded every year from 2001-2020:")
    movies_age=movies.groupby('Age').agg({'Netflix':'sum','Hulu':'sum','Prime_Video':'sum','Disney+':'sum'}).sort_values(by='Age',ascending=False)
    dfi.export(movies_age, 'output/movies_age.png')
    man.print_to_stdout(movies_age) 

    age_plot=movies_age.plot(kind='pie', subplots=True, title='Number of movies in each platform by recommended Age',figsize=(16,8))
    plt.savefig('output/age.png')

    print("The next table summarizes the amount of movies per recommended age in each platform:")
    movies_years=movies[(movies['Year']<2021) & (movies['Year']>2000)].groupby('Year').agg({'Title':'count'})
    dfi.export(movies_years, 'output/movies_years.png')
    man.print_to_stdout(movies_years) 

    years_plot=movies_years.plot.bar(xlabel='Year',ylabel='Number of movies',title='Recorded movies per year between 2000-2020')
    plt.savefig('output/years.png')

    pdf.export_pdf()

    
    man.send_mail('output/report.pdf')

if __name__ == "__main__":
    main()
