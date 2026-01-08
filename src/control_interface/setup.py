from setuptools import setup

package_name = 'control_interface'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    install_requires=['setuptools'],
    entry_points={
        'console_scripts': [
            'gui = control_interface.gui:main',
        ],
    },
)