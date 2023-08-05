import os

from setuptools import setup, find_packages

requires = open("requirements.txt", "r").readlines() if os.path.exists("requirements.txt") else open("./vive_tracker_apiserver.egg-info/requires.txt", "r").readlines()
print("#-------------------    ", str(os.listdir("./")))
setup(
    name="vive-tracker-apiserver",
    version="0.0.5",
    author="davidliyutong",
    author_email="davidliyutong@sjtu.edu.cn",
    description="Vive Tracker APIServer",
    packages=find_packages() + ["vive_tracker_apiserver.third_party.triad_openvr." + pkg for pkg in find_packages('vive_tracker_apiserver.third_party.triad_openvr')],
    python_requires=">=3.7",
    install_requires=requires,
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown"
)