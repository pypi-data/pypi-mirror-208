from src.news.models import NewsPublisher
from src.news.models import NewsSubscriber
from src.news.views import AIJKivy


def main():
    """
    The main function to run the server and publish the news articles to the RabbitMQ queue
    """
    print('Server is being initialized...')

    # create an instance of the AIJKivy class
    app = AIJKivy()
    app.run()

    print('Server is now running...')


if __name__ == '__main__':
    main()
