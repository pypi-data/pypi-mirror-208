import setuptools

with open('README.md') as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name="robin-chat",
    version="0.0.2.2",
    author="Chris Doyle",
    author_email="chris@robinai.co.uk",
    description="Streamlit component for rendering RobinAI chat messages",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/chrisdoyleie/robin-chat",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords="chat streamlit streamlit-component",
    python_requires=">=3.8",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 0.63",
    ],
)
