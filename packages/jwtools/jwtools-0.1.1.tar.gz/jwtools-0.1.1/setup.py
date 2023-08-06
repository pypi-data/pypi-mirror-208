from setuptools import setup, find_packages

setup(
    name='jwtools',
    version='0.1.1',
    description="jwtools",
    long_description=open('README.md').read(),
    include_package_data=True,
    author='jinghewang',
    author_email='jinghewang@163.com',
    license='MIT License',  # 协议
    url='',  # github或者自己的网站地址
    packages=find_packages(),  # 包的目录
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.10',
    install_requires=[''],
    entry_points={
        'console_scripts': [''],
    },

)
