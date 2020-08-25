import markdown
import pydot
import re
import xml.etree.ElementTree as etree

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.blockprocessors import BlockProcessor


def analyze_graph(graph, node_list=None, level=0):
    graph_as_json = []

    if node_list is None:
        node_list = []

    # the top graph is called 'G', we will ignore it globally
    parent_node = graph.get_name()

    if parent_node != 'G' and parent_node not in node_list:
        node_list.append(parent_node)
        node_dict = {'id': parent_node}

        classes_list = ['level' + str(level)]
        if len(graph.get_nodes()) > 0 or len(graph.get_subgraphs()) > 0:
            classes_list.append('hasChildren')

        graph_as_json.append({'data': node_dict,
                              'classes': classes_list})

    for i, node in enumerate(graph.get_nodes()):
        if node not in node_list:
            node_list.append(node)

    for i, edge in enumerate(graph.get_edges()):
        for temp_node in [edge.get_source(), edge.get_destination()]:
            if temp_node not in node_list:
                node_list.append(temp_node)
                node_dict = {'id': temp_node, 'parent': parent_node}
                if parent_node != 'G':
                    graph_as_json.append({'data': node_dict})
                else:
                    graph_as_json.append({'data': node_dict})

        edge_dict = {
            'id': 'edge' + '_' + parent_node + '_' + str(i),
            'source': edge.get_source(),
            'target': edge.get_destination()
        }

        graph_as_json.append({'data': edge_dict})

    for g in graph.get_subgraphs():
        subgraph_as_json, sub_node_list = analyze_graph(g, node_list, level+1)
        graph_as_json = graph_as_json + subgraph_as_json
        node_list = node_list + sub_node_list

    return graph_as_json, node_list


def graph_to_json(dotstring):
    dotobject = pydot.graph_from_dot_data(dotstring)

    graphs_as_json = []

    for graph in dotobject:
        graph_as_json, _ = analyze_graph(graph)
        graphs_as_json = graphs_as_json + graph_as_json

    return graphs_as_json


class AddAttrTree(Treeprocessor):
    def run(self, root):
        highest_heading = None
        new_highest_heading = 3  # h3 is the top level in the result

        for heading in range(1, 7):
            if root.find('h' + str(heading)):
                highest_heading = heading
                break

        for h2 in root.iter('h2'):
            h2.tag = 'h4'
            h2.attrib['class'] = 'yo'


class DotBlockProcessor(BlockProcessor):

    RE = re.compile(r'^..\s+(\w+)\s*::')

    def __init__(self, *args, **kwargs):
        super(DotBlockProcessor, self).__init__(*args, **kwargs)
        self.cy_index = 0

    def test(self, parent, block):
        return self.RE.search(block)

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.search(block)

        if m:
            block = block[m.end():]  # remove the first line

        block, rest = self.detab(block)

        if m:
            block_type = m.group(1).lower()

            if block_type is not None:
                div_graph = etree.SubElement(parent, 'div')
                div_graph_id = 'graph' + str(self.cy_index)
                div_graph.set('id', div_graph_id)
                div_graph.set('class', 'graph')

                div_cy = etree.SubElement(div_graph, 'div')
                div_cy_id = 'cy' + str(self.cy_index)
                div_cy.set('id', div_cy_id)
                div_cy.set('class', 'cygraph big')

                script = etree.SubElement(div_cy, 'script')
                script.set('language', 'javascript')
                script.text = 'cytoscape_data_' + div_cy_id + ' = ' +\
                              str(graph_to_json(block)) + ';'

                self.cy_index += 1

        if rest:
            blocks.insert(0, rest)


class AddAttrExt(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(item=AddAttrTree(md),
                                   name='add_attr',
                                   priority=10)


class DotBlockExt(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(item=DotBlockProcessor(md.parser),
                                           name='dot_block',
                                           priority=100)


def md_convert(filename):
    with open(filename, 'r') as f:
        extensions = [AddAttrExt(), DotBlockExt()]
        html = markdown.markdown(f.read(), extensions=extensions)
        return html


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='markdown converter for'
                                     'django blog application')
    parser.add_argument('md_filename', nargs=1, help='markdown file name')
    args = parser.parse_args()

    print(md_convert(args.md_filename[0]))
