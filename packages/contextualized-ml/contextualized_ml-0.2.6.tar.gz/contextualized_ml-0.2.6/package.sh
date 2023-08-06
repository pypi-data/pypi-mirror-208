nvim setup.py
nvim pyproject.toml
python3 -m build
python3 -m twine upload --repository testpypi dist/*
python3 -m pip install --index-url https://test.pypi.org/simple/ contextualized-ml==<new version>
python3 -m twine upload dist/*
python3 -m pip install contextualized-ml
