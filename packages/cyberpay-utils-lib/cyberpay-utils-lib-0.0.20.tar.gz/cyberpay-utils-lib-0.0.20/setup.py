from setuptools import find_packages, setup

setup(
    name="cyberpay-utils-lib",
    version="0.0.20",
    description="Cyberpay utils library",
    author="MADI SPACE",
    license="MIT",
    packages=find_packages(where="."),
    package_dir={"": "."},
    package_data={
        "cyberpay_utils.auth.proto": ["*.proto", "*.pyi"],
        "cyberpay_utils.billing.proto": ["*.proto", "*.pyi"],
        "cyberpay_utils.company.proto": ["*.proto", "*.pyi"],
        "cyberpay_utils.email.proto": ["*.proto", "*.pyi"],
        "cyberpay_utils.tinkoff.proto": ["*.proto", "*.pyi"],
        "cyberpay_utils.user.proto": ["*.proto", "*.pyi"],
    },
    install_requires=[
        "Django",
        "djangorestframework-simplejwt",
        "grpc-interceptor",
        "grpcio",
        "protobuf",
        "transliterate",
    ],
    zip_safe=False,
)
