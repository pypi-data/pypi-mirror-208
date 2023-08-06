import os

from setup.install import LinuxPackageManager, MacOSPackageManager, WindowsPackageManager

def main():
    """
    This method is the main method which will install all the dependencies required for the project.
    ERLang: It is a programming language used to build massively scalable soft real-time systems with requirements on high availability.
    RabbitMQ: It is an open-source message-broker software that originally implemented the Advanced Message Queuing Protocol and has since been extended with a plug-in architecture to support Streaming Text Oriented Messaging Protocol, MQ Telemetry Transport, and other protocols.
    """

    # if the os is windows, install scoop and then install erlang and rabbitmq
    if os.name == 'nt':
        scoop = WindowsPackageManager()
        scoop.install_all()

    # if the os is linux, install erlang and rabbitmq using apt-get
    elif os.name == 'posix':
        apt = LinuxPackageManager()
        apt.install_all()

    # if the os is mac, install erlang and rabbitmq using brew
    elif os.name == 'darwin':
        brew = MacOSPackageManager()
        brew.install_all()