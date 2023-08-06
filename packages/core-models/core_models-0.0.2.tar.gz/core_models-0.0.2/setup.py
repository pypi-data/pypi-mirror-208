from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'Liquify core package'
LONG_DESCRIPTION = 'Package that holds all models and core ' \
                   'functions/classes of Liquify project'

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="core_models",
    version=VERSION,
    author="Folayemi Bello",
    author_email="<bello.folayemi.az@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    package_data={'': ['app/templates/core_models/*']},
    include_package_data=True,
    install_requires=["django", "python-dotenv", "django-safedelete", "redis",
                      "onesignal-sdk", "django-cities-light", 'daphne', 'psycopg2-binary',
                      "django-slack", "uvicorn", "django-storages", "boto3"],
    # add any
    # additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'liquify'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",

    ]
)
