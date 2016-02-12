from setuptools import setup, find_packages

setup(
    name='pytalog',
    version='1.0',
    long_description=__doc__,
    packages=['pytalog'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'werkzeug==0.8.3',
        'flask==0.10',
        'Flask-Login==0.1.3',
        'oauth2client',
        'requests',
        'httplib2',
        'flask-debugtoolbar',
        'Flask-SQLAlchemy',
        'Flask-Script',
    ]
)
