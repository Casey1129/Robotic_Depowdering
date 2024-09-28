from setuptools import find_packages, setup

package_name = 'vcpd'

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
    maintainer='artyom',
    maintainer_email='artyom.boyarov@gmail.com',
    description='TODO: Package description',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mesh_processing = vcpd.data_collection.mesh_processing:main',
            'grasp_analysis = vcpd.data_collection.grasp_analysis:main'
        ],
    },
)
