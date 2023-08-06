import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-iot-core-certificates",
    "version": "1.0.12",
    "description": "cdk-iot-core-certificates",
    "license": "MIT",
    "url": "https://github.com/polyperception/cdk-iot-core-certificates",
    "long_description_content_type": "text/markdown",
    "author": "DevOps@Home<devops.at.home@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/polyperception/cdk-iot-core-certificates"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_iot_core_certficates",
        "cdk_iot_core_certficates._jsii"
    ],
    "package_data": {
        "cdk_iot_core_certficates._jsii": [
            "cdk-iot-core-certificates@1.0.12.jsii.tgz"
        ],
        "cdk_iot_core_certficates": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.43.1, <3.0.0",
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
