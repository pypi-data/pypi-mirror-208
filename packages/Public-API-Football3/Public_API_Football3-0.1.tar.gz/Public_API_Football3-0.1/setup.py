from setuptools import setup, find_packages
setup(
    name='Public_API_Football3',
    version='0.1',
    author='Dmytro Chebotarov',
    author_email='chebodi@ukr.net',
    packages=find_packages(),
    license='MIT',
    install_requires=[
        'requests',
    ],
)

# packages=find_packages(exclude="Library"),
# packages=['Library'],