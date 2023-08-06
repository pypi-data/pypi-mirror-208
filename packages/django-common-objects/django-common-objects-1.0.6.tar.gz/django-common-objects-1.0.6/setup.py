from setuptools import setup, find_packages

setup(
    name='django-common-objects',
    packages=find_packages(),
    version='1.0.6',
    install_requires=[
        "django>=3.2.18",
        "djangorestframework>=3.14.0",
    ],
    # extras_require={
    # },
    author='cone387',
    maintainer_email='1183008540@qq.com',
    license='MIT',
    url='https://github.com/cone387/DjangoCommonObjects',
    python_requires='>=3.7, <4',
)