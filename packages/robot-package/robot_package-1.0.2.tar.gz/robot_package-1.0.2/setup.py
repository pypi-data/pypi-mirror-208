from setuptools import setup, Extension

setup(
    name='robot_package',
    version='1.0.2',
    description='Controlling the Jaco2 robot',
    ext_modules=[Extension('robot_package.jaco2', ['robot_package/jaco2.dll'])],
    include_package_data=True,
    zip_safe=False,
)


