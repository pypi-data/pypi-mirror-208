
from pathlib import Path
from setuptools import setup, Extension

version = "2.1.1"
extension_name = "c"
here = Path.cwd()
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

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
    long_description=long_description,
    long_description_content_type='text/markdown',
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
