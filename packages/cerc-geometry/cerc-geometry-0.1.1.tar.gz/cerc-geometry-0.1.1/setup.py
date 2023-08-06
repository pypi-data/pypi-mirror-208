import setuptools
import pkg_resources
import glob

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as r:
  install_requires = [
    str(requirement)
    for requirement
    in pkg_resources.parse_requirements(r)
  ]
install_requires.append('setuptools')

setuptools.setup(
  name="cerc-geometry",
  version="0.1.1",
  author="CERC",
  author_email=" cerc@concordia.ca",
  description="CERC Geometry Library with different modules to manipulate geometric objects",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://nextgenerations-cities.encs.concordia.ca/gitea/p_yefi/geometry",
  project_urls={
    "Repository": "https://nextgenerations-cities.encs.concordia.ca/gitea/p_yefi/geometry",
    "Bug Tracker": "https://nextgenerations-cities.encs.concordia.ca/gitea/p_yefi/geometry/issues"
  },
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
    "Operating System :: OS Independent",
  ],
  data_files=[
    ('src', glob.glob('requirements.txt')),
  ],
  packages=['src'],
  setup_requires=install_requires,
  install_requires=install_requires,
  python_requires=">=3.6"
)
