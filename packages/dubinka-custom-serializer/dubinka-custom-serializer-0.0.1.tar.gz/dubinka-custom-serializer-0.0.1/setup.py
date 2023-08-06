from setuptools import setup

setup(
    name='dubinka-custom-serializer',
    version='0.0.1',
    packages=['custom_serializer.src'],
    entry_points={
        "console_scripts": [
            "custom-serialize = custom_serializer.src.custom_serializer:main"
        ]
    },
    url='',
    license='',
    author='misha-rab-ymniy',
    author_email='',
    description=''
)
