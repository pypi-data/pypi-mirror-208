from setuptools import setup, find_packages

VERSION = '1.0.0' 
DESCRIPTION = 'Lunar date library for Python'
LONG_DESCRIPTION = 'Lunar date library for Python'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="lunar_ar_date", 
        version=VERSION,
        author="DarkCalendar",
        author_email="blackcalendar110@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'date', 'lunar', 'calendar'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)