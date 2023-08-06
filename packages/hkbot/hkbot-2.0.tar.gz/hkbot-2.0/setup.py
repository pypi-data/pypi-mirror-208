
from pathlib import Path
from setuptools import setup, Extension

version = "2.0"
extension_name = "c"
here = Path.cwd()


ext_modules = [
    Extension(
        resource
        .stem,
        sources=[
            resource
            .relative_to(here.parent)
            .as_posix()
            .split("/")[1]
        ]
    )
    for resource in [*here.glob(f"*.{extension_name}")]
]
setup(
    name="hkbot",
    version=version,
    description="hkbot automation",
    author="AkasakaID",
    install_requires=[
        "requests",
        "telethon",
        "colorama",
        "pytz"
    ],
    ext_modules=ext_modules,
    entry_points={
        "console_scripts": [
            "hkbot=hkbot:main",
            "hkbot-create-config=hkbot:getConfig"
            ]
    }
)
