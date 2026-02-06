from setuptools import find_packages, setup

package_name = 'hivecore_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jie-808',
    maintainer_email='jie-808@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        	'hivecore_pub = hivecore_pkg.hivecore_pub:main',
            'hivecore_vrcol = hivecore_pkg.hivecore_vrcol:main',
            'hivecore_IK = hivecore_pkg.hivecore_IK:main',
        ],
    },
)
