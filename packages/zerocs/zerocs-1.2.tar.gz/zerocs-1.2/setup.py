from setuptools import setup, find_packages

setup(
    name='zerocs',
    version='1.2',
    description="zerocs",
    long_description=open('zerocs/README.rst').read(),
    # long_description_content_type='text/plain',
    include_package_data=True,
    author='YanPing',
    author_email='zyphhxx@foxmail.com',
    maintainer='YanPing',
    maintainer_email='zyphhxx@foxmail.com',
    license='MIT License',
    url='https://github.com/ZYPGITA/zerocs',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=['nameko', 'pika'],
)
