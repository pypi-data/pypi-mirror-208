from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

VERSION = '0.0.5'
DESCRIPTION = 'A python package to make configs easier!'
LONG_DESCRIPTION = '''Example:
if __name__ == '__main__':
    file = open('config.config', 'w+') # open config file.
    config = Reader.load(f=file) # one way is the load function it uses an file object and then reads the config from there.
    print(config)
    # or:
    # text = file.read()
    #  config = Reader.loads(text) # Loads the config from text.
    # Get a spicific value from config without loading it: Reader.get(filename='config.config', name='The Name') # returns the value of the given name from the config.
    # Get a spicific value from config text: Reader.get_from_raw_text(name='The Name', text='Text to find the name in') # returns the value of the given name from the text
    Dumper.create_basic(filename='config.config') # creates a basic config and writes Version 1.0 in it.
    # Write something to the config: Dumper.add(filename='config.config', name='The Name', value='The Value')
    # Write Moultiple Things to your config: Dumper.dump(filename='config.config', names=['System'], values=['Windows']) # it uses the enmurate function.'''

setup(
    name="easy-configs",
    version=VERSION,
    author="tntgamer685347",
    author_email="gamer@fampl.de",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)