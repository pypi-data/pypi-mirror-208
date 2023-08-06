from setuptools import setup

setup(
    name='dubinka-custom-serializer',
    version='0.0.5',
    packages=['custom_serializer'],
    entry_points={
        "console_scripts": [
            "custom-serialize = custom_serializer.custom_serializer:main"
        ]
    },
    url='',
    license='',
    author='misha-rab-ymniy',
    author_email='',
    description=''
)
