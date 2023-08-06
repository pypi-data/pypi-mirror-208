from setuptools import setup, find_packages

setup(
    name='velait_api',
    version='0.5.3',
    license='LICENSE.md',
    packages=find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'django',
        'djangorestframework',
        'djangorestframework-camel-case',
        'drf_yasg',
        'django-safedelete',
        'django-auditlog',
        'django-defender',
    ],
)
