nightsky: code_head.py bake_catalog.py nightsky.py bright_star_catalog_v50
	./bake_catalog.py
	cat ./code_head.py ./bake_catalog ./nightsky.py > nightsky
	chmod a+x nightsky
	\rm ./bake_catalog
