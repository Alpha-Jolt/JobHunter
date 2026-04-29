"""Setup configuration for scraper package."""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="scraper",
    version="0.1.0",
    description="JobHunter Scraper Engine — Phase 0 MVP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="JobHunter Team",
    python_requires=">=3.10",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "playwright>=1.44.0",
        "fastapi>=0.111.0",
        "uvicorn>=0.30.1",
        "pydantic>=2.7.1",
        "pydantic-settings>=2.3.0",
        "beautifulsoup4>=4.12.3",
        "lxml>=5.2.2",
        "httpx>=0.27.0",
        "redis>=5.0.4",
        "apscheduler>=3.10.4",
        "sentry-sdk>=2.5.1",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.1",
        "email-validator>=2.1.1",
    ],
    extras_require={
        "dev": [
            "pytest>=8.2.2",
            "pytest-asyncio>=0.23.7",
            "pytest-cov>=5.0.0",
            "black>=24.4.2",
            "flake8>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "scraper=dev_mode.dev_runner:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
