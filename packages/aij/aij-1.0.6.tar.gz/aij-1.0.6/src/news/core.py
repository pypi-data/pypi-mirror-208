import json
import os
import time
from threading import Timer

import pandas as pd
import pika
from newsapi import NewsApiClient

from newsapi.newsapi_exception import NewsAPIException


class NewsPublisher:
    """
    A class to publish news articles to a RabbitMQ queue using the NewsAPI
    @param api_key: the api key to access the NewsAPI
    @param host: the host name of the RabbitMQ server
    @param queue_name: the name of the queue to publish the news articles
    """
    def __init__(self, api_key, host='localhost', queue_name='news_stream'):
        self.api = NewsApiClient(api_key=api_key)
        self.host = host
        self.queue_name = queue_name
        # set up a connection to RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel = self.connection.channel()
        self.sources = 'bbc-news, cnn, fox-news, google-news, time, wired, the-new-york-times, the-wall-street-journal, the-washington-post, usa-today, abc-news, associated-press, bloomberg, business-insider, cbs-news, cnbc, entertainment-weekly, espn, fortune, fox-sports, mtv-news, national-geographic, nbc-news, new-scientist, newsweek, politico, reddit-r-all, reuters, the-hill, the-huffington-post, the-verge, the-washington-times, vice-news'

        try:
            self.articles = self.api.get_everything(sources=self.sources)
            self.headlines = self.api.get_top_headlines(sources=self.sources)
        except NewsAPIException as api_exception:
            print(f"Could not request results from NewsAPI; {api_exception}")
            print("Loading the news from the database...")

    def publish(self):
        """
        Publish the news articles to the RabbitMQ queue one by one and save the news to the database
        """
        try:
            for _article in self.articles['articles']:
                _body = json.dumps(_article).encode('utf-8')
                self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=_body)
                print(f"Published a news article to the queue: {_article['title']}")
                # wait for 1 second before publishing the next article
                time.sleep(1)

            for _headline in self.headlines['articles']:
                _body = json.dumps(_headline).encode('utf-8')
                self.channel.basic_publish(exchange='', routing_key=f"{self.queue_name}_headlines", body=_body)
                print(f"Published a news headline to the queue: {_headline['title']}")
                # wait for 1 second before publishing the next article
                time.sleep(1)
        except NewsAPIException as api_exception:
            print(f"Could not request results from NewsAPI; {api_exception}")
            print("Loading the news from the database...")
            

        # do not close the connection until the message is delivered
        if self.connection.is_open:
            self.connection.close()

        # call the function again after 100 seconds because there are max. 100 results per page
        Timer(100, self.publish).start()


    def destroy(self):
        """
        Destroy the connection to the RabbitMQ server
        """
        self.connection.close()


class NewsSubscriber:
    """
    This class implements a RabbitMQ consumer.
    """
    def __init__(self, host, callback_function):
        """
        This method initializes the consumer.
        """
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='news_stream')
        self.callback_function = callback_function

    def subscribe(self):
        """
        This method starts consuming messages from the RabbitMQ queue.
        """
        self.channel.basic_consume(queue='news_stream', on_message_callback=self.callback, auto_ack=True)
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        """
        This method is called when a message is received from the RabbitMQ queue.
        """
        self.callback_function(method.routing_key, body)
        time.sleep(1)

    def destroy(self):
        """
        This method closes the connection to the RabbitMQ server.
        """
        if self.connection.is_open:
            self.connection.close()