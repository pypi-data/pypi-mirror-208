import os

from news.core import NewsPublisher

def main():
    """
    The main function to run the server and publish the news articles to the RabbitMQ queue
    """
    print('Server is being initialized...')

    # get the api key from the environment variable. If it is not set, use argument parser to get the api key
    api_key = os.environ.get('NEWSAPI_ORG')

    # create an instance of the NewsPublisher class
    api = NewsPublisher(api_key)

    # get the news from the newsapi
    api.publish()

    print('Server is now running...')
