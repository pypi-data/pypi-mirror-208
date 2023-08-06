from setuptools import setup, find_packages

with open("README.md", "r",encoding='UTF-8') as readme_file:
    readme = readme_file.read()

requirements = [
    "lxml",
    'requests',
    "xmltodict",
    'tqdm',
    'aiohttp==3.8.3',
    'pandas',
    'openai==0.27.0',
    'shillelagh==1.1.5',
    'shillelagh[gsheetsapi]'
]

setup(
    name="requests-toolkit-stable",
    version="0.25.0",
    author="Tao Xiang",
    author_email="tao.xiang@tum.de",
    description="A package of APIs using requests.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/leoxiang66/requests-toolkit",
    packages=find_packages(),
    # py_modules=['timedd']
    install_requires=requirements,
    classifiers=[
	"Programming Language :: Python :: 3.10",
	"License :: OSI Approved :: MIT License",
    ],
)
