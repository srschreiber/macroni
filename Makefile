install: build-extension
	./scripts/bootstrap.sh

build-extension:
	cd macroni/extension/macroni && vsce package
	mv macroni/extension/macroni/*.vsix .
	code --install-extension macroni-*.vsix

# build and check distribution package
build-dist:
	python3 -m build
	twine check dist/*
