import setuptools

requirements = []

for pkg in open('requirements.txt').read().splitlines():
    if pkg.startswith('#'):
        continue

    if pkg:
        requirements.append(pkg)

setuptools.setup(
    install_requires=requirements
)