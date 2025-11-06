from setuptools import setup, find_packages
import os


def local_scheme(version):
    if os.environ.get("IS_PULL_REQUEST"):
        return f".dev{os.environ.get('GITHUB_RUN_ID', 'local')}"
    return ""


try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""


setup(
    name='mcp-server-generator',
    author='Vinayak Menon',
    author_email='vinayakmenon+pypi@users.noreply.github.com',
    description='Generate dual-mode MCP servers with best practices',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hitoshura25/mcp-server-generator',
    use_scm_version={"local_scheme": local_scheme},
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Jinja2>=3.0',
        'pypi-workflow-generator>=0.3.0',
    ],
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={
        'console_scripts': [
            'mcp-server-generator=mcp_server_generator.server:main',
            'mcp-server-generator-cli=mcp_server_generator.cli:main',
        ],
    },
)
