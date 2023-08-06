from setuptools import setup, find_packages

setup(
    name="dabbas",
    version="0.1.10",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "db = db.main:main",
            "dabbas = db.main:main",
        ],
    },
    install_requires=[
        "pandas_flavor",
        "SQLAlchemy",
        "pandas",
        "geopandas",
        "psycopg2-binary",
        "shapely",
        "folium",
        "strawberry-graphql",
        "supabase"
        # Add any required dependencies here
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
