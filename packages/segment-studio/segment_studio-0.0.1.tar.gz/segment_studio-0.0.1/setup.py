# [metadata]
# name = segment_studio_test
# version = 0.0.1
# author = shanmukanaks
# author_email = shanmukanaks@gmail.com
# description = A small example package
# long_description = file: README.md
# long_description_content_type = text/markdown
# url = https://github.com/shanmukanaks/Segment-Studio
# project_urls =
#     Bug Tracker = https://github.com/pypa/sampleproject/issues
# classifiers =
#     Programming Language :: Python :: 3
#     License :: OSI Approved :: MIT License
#     Operating System :: OS Independent

# [options]
# package_dir =
#     = src
# packages = find:
# python_requires = >=3.6

# [options.packages.find]
# where = src

from setuptools import setup

# # read the contents of your README file
# from pathlib import Path
# this_directory = Path(__file__).parent
# long_description = (this_directory / "README.md").read_text()

setup(
    name='segment_studio',
    version='0.0.1',
    description='Segmentation Studio',
    # long_description=long_description,
    # long_description_content_type='text/markdown'
    classifiers=[
    'Programming Language :: Python :: 3.9',
    ],
    keywords='object detection image editor segmention',
    url='https://github.com/shanmukanaks/Segment-Studio.git',
    author='shanmukanaks',
    author_email='shanmukanaks@gmail.com',
    # license='MIT',
    # packages=['funniest'],
    # install_requires=[
    #     'markdown',
    # ],
    # test_suite='nose.collector',
    # tests_require=['nose', 'nose-cover3'],
    # entry_points={
    #     'console_scripts': ['funniest-joke=funniest.command_line:main'],
    # },
    zip_safe=False
)