import versioneer
from setuptools import setup, find_namespace_packages

with open('requirements.txt', 'r') as file:
    REQUIREMENTS = file.readlines()

with open('README.md', 'r') as file:
    long_description = file.read()


setup(
    name='drb-topic-sentinel5p',
    description='sentinel-5P topic for DRB Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='GAEL Systems',
    author_email='drb-python@gael.fr',
    url='https://gitlab.com/drb-python/topics/sentinel5p',
    python_requires='>=3.8',
    install_requires=REQUIREMENTS,
    packages=find_namespace_packages(include=['drb.*']),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: "
        "GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python :: 3.8",
    ],
    package_data={
        'drb.topics.sentinel5p': ['cortex.yml'],
        'drb.topics.sentinel5p.level1': ['cortex.yml'],
        'drb.topics.sentinel5p.level2': ['cortex.yml'],
        'drb.topics.sentinel5p.auxiliary': ['cortex.yml']
    },
    data_files=[('.', ['requirements.txt'])],
    entry_points={
        'drb.topic': [
            'sentinel5p=drb.topics.sentinel5p',
            'sentinel5p_l1=drb.topics.sentinel5p.level1',
            'sentinel5p_l2=drb.topics.sentinel5p.level2',
            'sentinel5p_aux=drb.topics.sentinel5p.auxiliary'
        ]
    },
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass()
)
