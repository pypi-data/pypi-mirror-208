import os
import urllib.request

user_profile = os.environ['USERPROFILE']
SEP = os.path.sep


def kernel():
    """
    Get the operating system kernel name
    @return: the operating system kernel name
    """
    return os.uname().sysname


def install():
    """
    Install packages via the related operating system package manager
    """
    if kernel() == 'Darwin':
        os.system('brew install python')
        os.system('brew install rabbitmq')
        os.system('brew install redis')

    elif kernel() == 'Linux':

        if os.uname().nodename == 'raspberrypi' or os.uname().nodename == 'debian' or os.uname().nodename == 'ubuntu':
            os.system('sudo apt-get install python3-pip')
            os.system('sudo apt-get install rabbitmq-server')
            os.system('sudo apt-get install redis-server')

        elif os.uname().nodename == 'archlinux':
            os.system('sudo pacman -S python')
            os.system('sudo pacman -S rabbitmq')
            os.system('sudo pacman -S redis')

        elif os.uname().nodename == 'fedora':
            os.system('sudo dnf install python')
            os.system('sudo dnf install rabbitmq-server')
            os.system('sudo dnf install redis')

        elif os.uname().nodename == 'centos':
            os.system('sudo yum install python')
            os.system('sudo yum install rabbitmq-server')
            os.system('sudo yum install redis')

        elif os.uname().nodename == 'opensuse':
            os.system('sudo zypper install python')
            os.system('sudo zypper install rabbitmq-server')
            os.system('sudo zypper install redis')

        elif os.uname().nodename == 'gentoo':
            os.system('sudo emerge dev-lang/python')
            os.system('sudo emerge rabbitmq-server')
            os.system('sudo emerge redis')

        elif os.uname().nodename == 'alpine':
            os.system('sudo apk add python')
            os.system('sudo apk add rabbitmq-server')
            os.system('sudo apk add redis')

        elif os.uname().nodename == 'manjaro':
            os.system('sudo pacman -S python')
            os.system('sudo pacman -S rabbitmq')
            os.system('sudo pacman -S redis')

    elif kernel() == 'Windows':

        # install the scoop package manager
        urllib.request.urlretrieve('https://get.scoop.sh', f'{user_profile}{SEP}scoop.ps1')

        # add scoop to the PATH environment variable
        os.system(f'set-executionpolicy remotesigned -scope currentuser')

        # install scoop
        os.system(f'{user_profile}{SEP}scoop.ps1')

        # use scoop to install the packages
        os.system('scoop install python')
        os.system('scoop install rabbitmq')
        os.system('scoop install redis')


def main():
    """
    The main function to run the script
    """
    install()


if __name__ == '__main__':
    main()
