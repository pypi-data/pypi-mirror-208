from setuptools import find_packages, setup
from pathlib import Path
from datetime import datetime


version = '0.1.8'
changes = "bug with regression normalized fixed"

SHIFT = "=" * 30
date = datetime.now()
changes = f"\n{SHIFT}\n{date} | {version}\n{changes}\n"

if __name__ == "__main__":
    with open("./CHANGELOG.txt", "a") as f:
        f.write(changes)

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='sar_handler',
    packages=find_packages(include=['sar_handler']),
    version=version,
    description='Handler SAR images',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Felecort',
    # author_email="@gmail.com",
    url="https://github.com/Felecort/SAR_Handler",
    license='MIT',
    install_requires=["numpy",
                      "Pillow",
                      "scipy",
                      "tqdm",
                      "torch",
                      ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)

