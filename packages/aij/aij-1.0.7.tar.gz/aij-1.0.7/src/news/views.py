# using Kivy to create a GUI for the publisher and subscriber
import logging as log
import os
import time
from threading import Thread

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


class AIJKivy(App):
    """
    A class to create a GUI for the publisher and subscriber
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # create an API key for the News API
        api_key = os.environ.get('NEWSAPI_ORG')
        if not api_key:
            raise ValueError('API key is not set')

        # create an instance of the NewsPublisher class
        self.publisher = NewsPublisher(
            api_key=api_key,
            host='localhost',
            queue_name='aij_news'
        )

        # create an instance of the NewsSubscriber class
        self.subscriber = NewsSubscriber(
            host='localhost',
            queue_name='aij_news',
            callback=self.print_news
        )

        self.title = 'AIJ News'
        self.icon = 'logo.png'

        # create a layout for the publisher
        self.publisher_layout = BoxLayout(orientation='vertical', padding=10)
        self.publisher_label = Label(text='Publisher', size_hint=(1, 0.90))
        self.publisher_button = Button(text='Publish', size_hint=(1, 0.10))

        # create a layout for the subscriber
        self.subscriber_layout = BoxLayout(orientation='vertical', padding=10)
        self.subscriber_label = Label(text='Subscriber', size_hint=(1, 0.90))
        self.subscriber_button = Button(text='Subscribe', size_hint=(1, 0.10))

        # create a layout for the main window
        self.main_layout = BoxLayout(orientation='horizontal', padding=10)

    def build(self):
        """
        Build the GUI for the publisher and subscriber
        """

        # add the label, text input and button to the publisher layout
        self.publisher_layout.add_widget(self.publisher_label)
        self.publisher_layout.add_widget(self.publisher_button)

        # add the label, text input and button to the subscriber layout
        self.subscriber_layout.add_widget(self.subscriber_label)
        self.subscriber_layout.add_widget(self.subscriber_button)

        # add the publisher and subscriber layouts to the main layout
        self.main_layout.add_widget(self.publisher_layout)
        self.main_layout.add_widget(self.subscriber_layout)

        # bind the button to the publish method
        self.publisher_button.bind(on_press=self.publisher)

        # bind the button to the subscribe method
        self.subscriber_button.bind(on_press=self.subscriber)

        Window.bind(on_keyboard=self.on_keyboard)

        return self.main_layout

    def publish(self, *args):
        """
        The method to publish the news articles to the RabbitMQ queue
        """

        # starts a thread to publish the news articles to the RabbitMQ queue
        news_publisher_thread = Thread(target=self.publisher.publish)

        # start the thread
        news_publisher_thread.start()

    def subscribe(self, *args):
        """
        The method to subscribe to the RabbitMQ queue and receive the news articles
        """

        # starts a thread to subscribe to the RabbitMQ queue and receive the news articles
        news_subscriber_thread = Thread(target=self.subscriber.subscribe)

        # start the thread
        news_subscriber_thread.start()

    def print_news(self, ch, method, properties, body):
        """
        This method is called when a message is received from the RabbitMQ queue.
        """
        response = body.decode('utf-8')
        print(
            f'-------------------------\n'
            f'{response}'
            f'-------------------------\n'
        )
        time.sleep(1)

    # add a on destroy method to stop the RabbitMQ server when the app is closed
    def on_stop(self):
        """
        The method to stop the RabbitMQ server when the app is closed
        """
        os.system('rabbitmqctl stop')

    # add a keyboard key event to stop the RabbitMQ server when the app is closed
    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        """
        The method to stop the RabbitMQ server when the app is closed
        The key event is triggered when the escape key is pressed
        """
        log.info(
            f'window: {window}\n'
            f'key: {key}\n'
            f'scancode: {scancode}\n'
            f'codepoint: {codepoint}\n'
            f'modifier: {modifier}\n'
        )
