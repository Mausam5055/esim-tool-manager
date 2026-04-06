from setuptools import setup, find_packages

setup(
    name="esim-tool-manager",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "typer[all]>=0.9.0",
        "rich>=13.0.0",
        "requests>=2.31.0",
        "packaging>=23.0",
    ],
    entry_points={
        "console_scripts": [
            "esim-tool=main:app",
            "esim-tool-gui=tool_manager.ui.gui:main",
        ],
    },
    python_requires=">=3.10",
    author="Sumanto Kar",
    description="Automated Tool Manager for eSim EDA Platform",
    long_description=open("README.md").read() if open("README.md") else "",
    long_description_content_type="text/markdown",
)
