from setuptools import setup, find_packages

setup(
    name='wake_up_bright',
    version='0.0.1',
    packages=find_packages(include=[
        'wake_up_bright',
        'wake_up_bright.*',
    ]),
    tests_require=[
        'pytest',
        'coverage'
        # Add any more packages required for testing only here
    ],
    install_requires=[
        'Flask',  # Required for web UI
        'python-dotenv',  # Required for the web UI
        'SQLAlchemy',
        'Flask-SQLAlchemy',
        'PyMySQL',
        'mysqlclient',
        'Flask-WTF',
        'matplotlib',
        'pandas',
        'mariadb',  # install to read from database
        'rpi-ws281x',
        'mysqlclient',
        'mpu6050-raspberrypi'
        # Add any more packages required for regular functionality
    ]
)
