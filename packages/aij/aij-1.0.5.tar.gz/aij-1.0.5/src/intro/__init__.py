from intro.intro import AnimationThread


def main():
    """
    This function is the entry point of the program
    @param: None
    @return: None
    """
    # Create and start the animation thread
    animation_thread = AnimationThread()
    animation_thread.start()

    # Do some other work here
    print('Doing some other work here...')

    # Wait for the animation thread to finish
    animation_thread.join()

