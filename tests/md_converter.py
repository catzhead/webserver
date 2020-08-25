import markdown
import pydot
import re
import xml.etree.ElementTree as etree

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.blockprocessors import BlockProcessor


def analyze_graph(graph, node_list=None, edge_list=None, level=0, parent=None):
    if node_list is None:
        node_list = {}

    if edge_list is None:
        edge_list = []

    # the top graph is called 'G', we will ignore it globally
    subgraph_node = graph.get_name()

    if subgraph_node != 'G' and subgraph_node not in node_list.keys():
        has_children = False
        if len(graph.get_nodes()) > 0 or len(graph.get_subgraphs()) > 0:
            has_children = True

        node_list[subgraph_node] = {'level': level,
                                    'has_children': has_children}

        if parent is not None:
            node_list[subgraph_node]['parent'] = parent

    local_node_list = graph.get_nodes()

    for i, edge in enumerate(graph.get_edges()):

        for temp_node in [edge.get_source(), edge.get_destination()]:
            local_node_list.append(temp_node)

        edge_dict = {'source': edge.get_source(),
                     'target': edge.get_destination()}

        edge_list.append(edge_dict)

    for i, node in enumerate(local_node_list):
        if node not in node_list.keys():
            node_list[node] = {'level': level,
                               'has_children': False,
                               'parent': subgraph_node}
        elif subgraph_node != 'G' and node_list[node]['level'] < level:
            # if a node is defined both in G and in a subgraph,
            # put it in the lowest subgraph
            node_list[node]['parent'] = subgraph_node
            node_list[node]['level'] = level

    for g in graph.get_subgraphs():
        sub_node_list, sub_edge_list = \
            analyze_graph(g, node_list, edge_list, level+1, subgraph_node)
        node_list = {**node_list, **sub_node_list}
        edge_list = edge_list + sub_edge_list

    return node_list, edge_list


def graph_to_json(dotstring):
    dotobject = pydot.graph_from_dot_data(dotstring)

    graphs_as_json = []
    node_list = {}
    edge_list = []

    for graph in dotobject:
        graph_node_list, graph_edge_list = analyze_graph(graph)
        node_list = {**node_list, **graph_node_list}
        edge_list = edge_list + graph_edge_list

    for node in node_list.keys():
        node_dict = {'id': node}

        parent = node_list[node]['parent']
        if parent is not None and parent != 'G':
            node_dict['parent'] = parent

        classes_list = ['level' + str(node_list[node]['level'])]

        if node_list[node]['has_children']:
            classes_list.append('hasChildren')
        else:
            classes_list.append('hasNoChildren')

        graphs_as_json.append({'data': node_dict, 'classes': classes_list})

    for i, edge in enumerate(edge_list):
        edge_dict = {
            'id': 'edge' + str(i),
            'source': edge['source'],
            'target': edge['target']
        }

        graphs_as_json.append({'data': edge_dict})

    return graphs_as_json


class AddAttrTree(Treeprocessor):
    def run(self, root):
        # highest_heading = None
        # new_highest_heading = 3  # h3 is the top level in the result

        # for heading in range(1, 7):
        #    if root.find('h' + str(heading)):
        #        highest_heading = heading
        #        break

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
