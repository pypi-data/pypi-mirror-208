from src.messaging.views import AIJMessagingServer


def main():
    # start an instance of AIJMessagingServer class
    msg = AIJMessagingServer()
    msg.run()


if __name__ == '__main__':
    main()
