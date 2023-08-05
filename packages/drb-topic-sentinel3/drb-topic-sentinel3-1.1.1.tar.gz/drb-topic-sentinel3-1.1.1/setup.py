import versioneer
from setuptools import setup, find_namespace_packages

with open('requirements.txt', 'r') as file:
    REQUIREMENTS = file.readlines()

with open('README.md', 'r') as file:
    long_description = file.read()


setup(
    name='drb-topic-sentinel3',
    description='Sentinel-3 topic for DRB Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='GAEL Systems',
    author_email='drb-python@gael.fr',
    url='https://gitlab.com/drb-python/topics/sentinel-3',
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
        'drb.topics.sentinel3': ['cortex.yml'],

        'drb.topics.sentinel3.OLCI': ['cortex.yml'],
        'drb.topics.sentinel3.OLCI.level0': ['cortex.yml'],
        'drb.topics.sentinel3.OLCI.level1': ['cortex.yml'],
        'drb.topics.sentinel3.OLCI.level2': ['cortex.yml'],

        'drb.topics.sentinel3.SLSTR': ['cortex.yml'],
        'drb.topics.sentinel3.SLSTR.level0': ['cortex.yml'],
        'drb.topics.sentinel3.SLSTR.level1': ['cortex.yml'],
        'drb.topics.sentinel3.SLSTR.level2': ['cortex.yml'],

        'drb.topics.sentinel3.SRAL': ['cortex.yml'],
        'drb.topics.sentinel3.SRAL.level0': ['cortex.yml'],
        'drb.topics.sentinel3.SRAL.level1': ['cortex.yml'],
        'drb.topics.sentinel3.SRAL.level2': ['cortex.yml'],

        'drb.topics.sentinel3.SYN': ['cortex.yml'],
        'drb.topics.sentinel3.SYN.level1': ['cortex.yml'],
        'drb.topics.sentinel3.SYN.level2': ['cortex.yml'],

        'drb.topics.sentinel3.MRW.level0': ['cortex.yml'],
        'drb.topics.sentinel3.MRW.level1': ['cortex.yml'],

        'drb.topics.sentinel3.GNSS.level0': ['cortex.yml'],

        'drb.topics.sentinel3.DORIS.level0': ['cortex.yml'],

        'drb.topics.sentinel3.Telemetry.level0': ['cortex.yml'],

        'drb.topics.sentinel3.Auxiliary': ['cortex.yml'],

    },
    data_files=[('.', ['requirements.txt'])],
    entry_points={
        'drb.topic': [
            'sentinel3=drb.topics.sentinel3',

            'sentinel3_olci=drb.topics.sentinel3.OLCI',
            'sentinel3_olci_level0=drb.topics.sentinel3.OLCI.level0',
            'sentinel3_olci_level1=drb.topics.sentinel3.OLCI.level1',
            'sentinel3_olci_level2=drb.topics.sentinel3.OLCI.level2',

            'sentinel3_slstr=drb.topics.sentinel3.SLSTR',
            'sentinel3_slstr_level0=drb.topics.sentinel3.SLSTR.level0',
            'sentinel3_slstr_level1=drb.topics.sentinel3.SLSTR.level1',
            'sentinel3_slstr_level2=drb.topics.sentinel3.SLSTR.level2',

            'sentinel3_sral=drb.topics.sentinel3.SRAL',
            'sentinel3_sral_level0=drb.topics.sentinel3.SRAL.level0',
            'sentinel3_sral_level1=drb.topics.sentinel3.SRAL.level1',
            'sentinel3_sral_level2=drb.topics.sentinel3.SRAL.level2',

            'sentinel3_syn=drb.topics.sentinel3.SYN',
            'sentinel3_syn_level1=drb.topics.sentinel3.SYN.level1',
            'sentinel3_syn_level2=drb.topics.sentinel3.SYN.level2',

            'sentinel3_mrw_level0=drb.topics.sentinel3.MRW.level0',
            'sentinel3_mrw_level1=drb.topics.sentinel3.MRW.level1',

            'sentinel3_gnss_level0=drb.topics.sentinel3.GNSS.level0',

            'sentinel3_doris_level0=drb.topics.sentinel3.DORIS.level0',

            'sentinel3_telemetry_level0=drb.topics.sentinel3.Telemetry.level0',

            'sentinel3_auxiliary=drb.topics.sentinel3.Auxiliary',
        ]


    },
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass()
)
