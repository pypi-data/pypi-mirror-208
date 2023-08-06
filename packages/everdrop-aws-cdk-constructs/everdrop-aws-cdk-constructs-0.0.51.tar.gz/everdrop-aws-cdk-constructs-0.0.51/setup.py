import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "everdrop-aws-cdk-constructs",
    "version": "0.0.51",
    "description": "Package provides opinionated constrcuts for common patterns used in everdrop infrastructure",
    "license": "Apache-2.0",
    "url": "https://github.com/everdropde/ed-aws-cdk-constructs.git",
    "long_description_content_type": "text/markdown",
    "author": "Fabian Bosler<FBosler@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/everdropde/ed-aws-cdk-constructs.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "everdrop_aws_cdk_constructs",
        "everdrop_aws_cdk_constructs._jsii"
    ],
    "package_data": {
        "everdrop_aws_cdk_constructs._jsii": [
            "everdrop-aws-cdk-constructs@0.0.51.jsii.tgz"
        ],
        "everdrop_aws_cdk_constructs": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.1.0, <3.0.0",
        "aws-solutions-constructs.core>=2.25.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.81.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard~=2.13.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
