from setuptools import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name="atmoswing-toolbox",
    version="1.3.4",
    author="Pascal Horton",
    author_email="pascal.horton@giub.unibe",
    description="Python tools for AtmoSwing",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=['atmoswing_toolbox', 'atmoswing_toolbox.datasets',
              'atmoswing_toolbox.parsers', 'atmoswing_toolbox.plots',
              'atmoswing_toolbox.utils'],
    package_dir={'atmoswing_toolbox': 'atmoswing_toolbox/datasets',
                 'atmoswing_toolbox.datasets': 'atmoswing_toolbox/datasets',
                 'atmoswing_toolbox.parsers': 'atmoswing_toolbox/parsers',
                 'atmoswing_toolbox.plots': 'atmoswing_toolbox/plots',
                 'atmoswing_toolbox.utils': 'atmoswing_toolbox/utils',
                 },
    zip_safe=False,
    extras_require={"test": ["pytest>=6.0"]},
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    readme="README.md",
    project_urls={
        "Source Code": "https://github.com/atmoswing/atmoswing-python-toolbox",
        "Bug Tracker": "https://github.com/atmoswing/atmoswing-python-toolbox/issues",
    },
    license="MIT",
)
