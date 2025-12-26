install: build-extension
	./scripts/bootstrap.sh

test:
	@echo "=== Running Macroni Test Suite ==="
	@for test in tests/test_*.macroni; do \
		echo ""; \
		echo "Running $$test..."; \
		python3 -m macroni.cli --file "$$test" || exit 1; \
		echo "✓ $$test passed"; \
	done
	@echo ""
	@echo "=== All Tests Passed ==="

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