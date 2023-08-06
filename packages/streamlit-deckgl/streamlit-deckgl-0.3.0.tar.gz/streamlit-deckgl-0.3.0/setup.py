from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="streamlit-deckgl",
    version="0.3.0",
    author="Oceanum",
    author_email="developers@oceanum.science",
    description="Streamlit component for deck.gl visualisation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["streamlit_deckgl"],
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.7",
    keywords=["streamlit", "pydeck", "deck.gl", "visualisation"],
    install_requires=["streamlit>=1.2", "jinja2", "pydeck>=0.8"],
    entry_points={},
)
