from distutils.core import setup
from pathlib import Path

setup(
    name="quick_resto_API",
    version="1.2.4",
    description='Quick Resto API',
    package_dir={"quick_resto_API": "quick_resto_API"},
    author_email='sergey.rukin1425@gmail.com',
    author='sergeyrukin',
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type='text/markdown',
)