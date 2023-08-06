from setuptools import setup

readme = ''
with open('README.md') as rf:
    readme = rf.read()

requirements = [
    'click==8.1.3',
    'Flask==2.2.2',
    'Flask-Cors==3.0.10',
    'Flask-Login==0.6.2',
    'Flask-WTF==1.0.1',
    'gevent==22.10.2',
    'greenlet==2.0.1',
    'gunicorn==20.1.0',
    'importlib-metadata==5.2.0',
    'itsdangerous==2.1.2',
    'Jinja2==3.1.2',
    'MarkupSafe==2.1.1',
    'marshmallow==3.19.0',
    'packaging==22.0',
    'six==1.16.0',
    'webargs==8.2.0',
    'Werkzeug==2.2.2',
    'WTForms==3.0.1',
    'zipp==3.11.0',
    'zope.event==4.6',
    'zope.interface==5.5.2'
]

setup(
    name='assistant-fulfillment-helper',
    author="TotvsLabs",
    version='1.0.6',
    author_email='info@totvslabs.com',
    python_requires='>=3.7',
    description="Assistant Fulfillment Helper Server",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    include_package_data=True,
    keywords='assistant fulfillment helper carol totvs carolina carolapp',
    packages=[
        'assistant_fulfillment_helper',
        'assistant_fulfillment_helper.app',
        'assistant_fulfillment_helper.app.controllers',
        'assistant_fulfillment_helper.app.data',
        'assistant_fulfillment_helper.app.exceptions',
        'assistant_fulfillment_helper.app.models',
        'assistant_fulfillment_helper.app.responses',
        'assistant_fulfillment_helper.app.server'
    ],
    url='https://github.com/totvslabs/assistant-fulfillment-helper'
)
