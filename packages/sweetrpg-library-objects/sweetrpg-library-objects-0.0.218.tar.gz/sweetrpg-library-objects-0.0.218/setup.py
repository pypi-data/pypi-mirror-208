from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="sweetrpg-library-objects",
    install_requires=[
        "Flask<3.0",
        "mongoengine==0.26.0",
        "sweetrpg-db",
        "sweetrpg-model-core",
        "marshmallow-jsonapi",
        "sweetrpg-api-core",
    ],
)
