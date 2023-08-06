from setuptools import setup, find_packages

setup(
    name='devpytools',
    version='0.1.0.dev5',
    description='Various dev tools.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/glowlex/devpytools',
    author='glowlex',
    author_email='antonioavocado777@gmail.com',
    license='MIT',
    packages=find_packages(include=['devpytools', 'devpytools.*']),
    zip_safe=False,
    test_suite="tests",
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    install_requires=[
        "pydashlite",  # 0.1.5
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['tools', 'cache', 'dev'],
    )
