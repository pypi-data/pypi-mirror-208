import setuptools
with open("README.md", "r") as fh:
  long_description = fh.read()
setuptools.setup(
  name="Daystar",
  version="0.0.4",
  author="Siddhu Pendyala",
  author_email="siddhu.pendyala@outlook.com",
  description="Sun calculation class from Solarflare module",
  long_description=long_description,  # don't touch this, this is your README.md
  long_description_content_type="text/markdown",
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  python_requires='>=3.6',
  install_requires=["Solarflare"])
