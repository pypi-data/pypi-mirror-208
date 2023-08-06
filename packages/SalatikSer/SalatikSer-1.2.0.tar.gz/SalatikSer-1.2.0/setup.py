from setuptools import setup, find_packages


setup(
    name="SalatikSer",
    version="1.2.0",
    description="JSON and XLM serializer",
    author="Daniil Litvinets",
    author_email="salatik.dan@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
    'console_scripts': [ 
        'serializer = MySerializer.serializer:main' 
    ] 
},
)