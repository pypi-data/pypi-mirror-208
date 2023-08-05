from setuptools import setup, find_packages, Command
import os

here = os.path.abspath(os.path.dirname(__file__))
req_file = os.path.join(here, 'requirements.txt')
with open(req_file, 'r') as f:
    REQUIREMENTS = [line.strip() for line in f.readlines()]
LONG_DESCRIPTION = 'Pygame N-Body gravity simulation app'

setup(
   name='gravitypy',
   version='1.1.7',
   description='GravityPy',
   license="MIT",
   author='WiktorK02',
   author_email='wiktor.kidon@hotmail.com',
   url="https://github.com/WiktorK02/gravityPy",
   long_description_content_type="text/markdown",
   package_data={'gravitypy': ['*']},
   include_package_data=True,
   long_description=LONG_DESCRIPTION,
   packages=find_packages(),
   data_files=[('gravitypy/resources/fonts', ['gravitypy/resources/fonts/minecraft_font.ttf'])],
   install_requires=REQUIREMENTS, 
    entry_points={
        'console_scripts': [
            'gravitypy = gravitypy.__main__:main'
        ]
    },

)
