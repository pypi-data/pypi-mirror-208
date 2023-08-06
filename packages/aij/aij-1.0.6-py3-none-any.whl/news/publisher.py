from threading import Thread
from news.core import NewsPublisher, NewsSubscriber

class NewsPublisherThread(Thread):
    """
    This class represents a thread that publishes news articles to a RabbitMQ queue
    @param api_key: the api key to access the NewsAPI
    @param host: the host name of the RabbitMQ server
    @param queue_name: the name of the queue to publish the news articles
    """
    def __init__(self, api_key, host='localhost', queue_name='news_stream'):
        Thread.__init__(self)
        self.pub = NewsPublisher(api_key, host, queue_name)

    def run(self):
        """
        This method is called when the thread is started
        """
        self.pub.publish()

    def destroy(self):
        """
        Destroy the connection to the RabbitMQ server
        """
        self.pub.destroy()


class NewsSubscriberThread(Thread):
    """
    This class represents a thread that subscribes to the RabbitMQ queue.
    """
    def __init__(self, host, callback_function):
        Thread.__init__(self)
        self.sub = NewsSubscriber(host, callback_function)

    def run(self):
        """
        This method is called when the thread is started.
        """
        self.sub.subscribe()

    def destroy(self):
        """
        This method closes the connection to the RabbitMQ server.
        """
        self.sub.destroy()
