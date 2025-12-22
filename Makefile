install: build-extension
	./scripts/bootstrap.sh

build-extension:
	cd macroni/extension/macroni && vsce package
	mv macroni/extension/macroni/*.vsix .
	code --install-extension macroni-*.vsix

# build and check distribution package
build-dist:
	rm -rf dist
	python3 -m build
	twine check dist/*

publish-dist:
	twine upload dist/*

build-and-publish: build-dist publish-dist

publish-extension:
	vsce login srschreiber
	cd macroni/extension/macroni && vsce publish