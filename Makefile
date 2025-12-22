install:
	python -m venv .venv
	.venv/bin/pip install -r requirements.txt

add-extension:
	code --install-extension extension/macroni/macroni-*.vsix