from speech.talk import AIJoke


def main():
    joke = AIJoke()
    joke.save_as_audio()
    joke.play_audio()


if __name__ == "__main__":
    main()
