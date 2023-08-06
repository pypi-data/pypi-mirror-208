import os
import urllib.request

user_profile = os.environ['USERPROFILE']
SEP = os.path.sep
DOWNLOAD_PATH = user_profile + SEP + 'Downloads' + SEP

class WindowsPackageManager():
    """
    This class will install ERLang and RabbitMQ using scoop.
    """
    def __init__(self):
        """
        This method will initialize the commands required to install ERLang and RabbitMQ using scoop.
        """
        self.scoop_url = 'https://raw.githubusercontent.com/lukesampson/scoop/master/bin/install.ps1'
        self.scoop_file = DOWNLOAD_PATH + 'scoop_install.ps1'
        self.scoop_install_command = 'powershell -ExecutionPolicy RemoteSigned -File ' + self.scoop_file

    def download_scoop(self):
        """
        This method will download scoop.
        """
        urllib.request.urlretrieve(self.scoop_url, self.scoop_file)

    def install_scoop(self):
        """
        This method will install scoop.
        """
        output = os.system(self.scoop_install_command)
        if output == 0:
            print(
                'Scoop installed successfully.'
            )
        else:
            print(
                'Scoop installation failed. Check if you have powershell installed.\nIf not, install it and try again.'
            )

    def install_required_apps(self):
        """
        This method will install ERLang and RabbitMQ using scoop.
        """
        # install ERLang and RabbitMQ using scoop
        os.system('scoop install erlang')
        os.system('scoop install rabbitmq')
        print(
            'ERLang and RabbitMQ installed via scoop successfully.'
        )

    def install_all(self):
        """
        This method will install all the required apps.
        """
        self.download_scoop()
        self.install_scoop()


class LinuxPackageManager():
    """
    This class will install ERLang and RabbitMQ using apt-get.
    """
    def __init__(self):
        """
        This method will initialize the commands required to install ERLang and RabbitMQ using apt-get.
        """
        self.update_cmd = 'sudo apt-get update'
        self.install_erlang_cmd = 'sudo apt-get install erlang'
        self.install_rabbitmq_cmd = 'sudo apt-get install rabbitmq-server'

    def install_required_apps(self):
        """
        This method will install ERLang and RabbitMQ using apt-get.
        """
        os.system(self.install_erlang_cmd)
        os.system(self.install_rabbitmq_cmd)
        print(
            'ERLang and RabbitMQ installed via apt-get successfully.'
        )

    def install_all(self):
        """
        This method will install all the required apps.
        """
        os.system(self.update_cmd)
        self.install_required_apps()


class MacOSPackageManager():
    """
    This class will install ERLang and RabbitMQ using brew.
    """
    def __init__(self):
        """
        This method will initialize the commands required to install ERLang and RabbitMQ using brew.
        """
        self.update_cmd = 'brew update'
        self.install_erlang_cmd = 'brew install erlang'
        self.install_rabbitmq_cmd = 'brew install rabbitmq'

    def install_required_apps(self):
        """
        This method will install ERLang and RabbitMQ using brew.
        """
        os.system(self.install_erlang_cmd)
        os.system(self.install_rabbitmq_cmd)
        print(
            'ERLang and RabbitMQ installed via brew successfully.'
        )

    def install_all(self):
        """
        This method will install all the required apps.
        """
        os.system(self.update_cmd)
        self.install_required_apps()