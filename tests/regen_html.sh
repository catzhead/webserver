sed -e /INSERT_DATA_HERE/r<(python md_converter.py $1) ../html/index_cytoscape4_template.html > ../html/index_cytoscape4.html
