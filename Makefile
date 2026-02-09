
.PHONY: release
release:
	 uvx \
        --from zest-releaser \
        --with zest-releaser'[recommended]' \
        --with zestreleaser-towncrier fullrelease
