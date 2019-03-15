addon_xml = plugin.video.vrt.nu/addon.xml

# Collect information to build as sensible package name
name = $(shell xmllint --xpath 'string(/addon/@id)' $(addon_xml))
version = $(shell xmllint --xpath 'string(/addon/@version)' $(addon_xml))
git_hash = $(shell git rev-parse --short HEAD)

zip_name = $(name)-$(version)-$(git_hash).zip
exclude_files = $(name).pyproj vrtnutests/ vrtnutests/*
exclude_paths = $(patsubst %,$(name)/%,$(exclude_files))
zip_dir = $(name)/

.PHONY: test


package: zip

test:
	@echo -e "\e[1;37m=\e[1;34m Starting tests\e[0m"
	tox -e py27,py36
	pylint $(name)/*.py
	pylint $(name)/resources/lib/*/*.py
	@echo -e "\e[1;37m=\e[1;34m Tests finished successfully.\e[0m"

zip:
	@echo -e "\e[1;37m=\e[1;34m Building new package\e[0m"
	rm -f $(zip_name)
	zip -r $(zip_name) $(zip_dir) -x $(exclude_paths)
	@echo -e "\e[1;37m=\e[1;34m Successfully wrote package as: \e[1;37m$(zip_name)\e[0m"