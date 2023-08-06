
from setuptools import setup, find_packages


setup(name='dockx_checker',
    version='0.0.1',
    description='a check tools',
    url='https://github.com/xxx',
    author='auth',
    author_email='xxx@gmail.com',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    install_requires=['tqdm','termcolor','bayoo-docx','flask'],
    entry_points={
        'console_scripts': ['docx-checker-service=dockx_checker_src.cmd:main']
    },

)
