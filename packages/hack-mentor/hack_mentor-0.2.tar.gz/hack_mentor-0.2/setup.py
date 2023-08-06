from setuptools import setup, find_packages

setup(
    name='hack_mentor',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'langchain',
        'flask',
        'python-dotenv',
        'rich',
        'openai'
    ],
    entry_points={
        'console_scripts': [
            'hack_mentor = hack_mentor.main:main',
        ],
    },

)
