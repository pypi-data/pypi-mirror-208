from setuptools import setup, find_packages
    
setup(name="glaceon",
      version="1.3.0",
      description="A Simple And Clean Logging Library That Can Be Used For Any Type Of Application.",
      long_description_content_type="text/markdown",
      long_description=open("README.md", encoding="utf-8").read(),
      packages=find_packages(exclude=['tests']),
      author="Zappy",
      url="https://pypi.python.org/pypi/glaceon",
      author_email="monkey@monk.com",
      license="MIT",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Topic :: Scientific/Engineering",
          "Topic :: Scientific/Engineering :: Information Analysis",
          "Topic :: Scientific/Engineering :: Mathematics",
          "Topic :: Scientific/Engineering :: Visualization",
          "Topic :: Software Development :: Libraries",
          "Topic :: Utilities",
      ],
      project_urls={
        'Homepage': 'https://github.com/BornPaster/Glaceon',
        'Suggestions': 'https://github.com/BornPaster/Glaceon/issues',
      },
    
      python_requires="~=3.7",

      install_requires=[

      ]
)