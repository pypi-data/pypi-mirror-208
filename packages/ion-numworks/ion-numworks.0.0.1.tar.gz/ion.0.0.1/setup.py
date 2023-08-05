from setuptools import setup, find_packages

setup(
    name="ion-numworks",
    version="0.0.1",
    author="ZetaMap",
    description="",
    license='MIT',
    long_description="no content,
    long_description_content_type='text/markdown',
    url="https://github.com/ZetaMap/Ion-numworks",
    project_urls={
        "Bug Tracker": "https://github.com/ZetaMap/Ion-numworks/issues",
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=["keyboard"],
)
