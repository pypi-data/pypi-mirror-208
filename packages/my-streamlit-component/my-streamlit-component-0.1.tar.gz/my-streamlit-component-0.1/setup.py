from setuptools import setup, find_packages

setup(
    name="my-streamlit-component",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "databutton",
        "gspread",
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A Streamlit component for tracking API usage",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/my-streamlit-component",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
