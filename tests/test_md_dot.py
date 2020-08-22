import json
import markdown
import pydot
import re
import xml.etree.ElementTree as etree

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.blockprocessors import BlockProcessor


def graph_to_json(dotstring):
    dotobject = pydot.graph_from_dot_data(dotstring)

    graphs_as_json = []

    for graph in dotobject:
        node_list = []
        graph_as_dict = []

        for i, edge in enumerate(graph.get_edges()):
            for temp_node in [edge.get_source(), edge.get_destination()]:
                if temp_node not in node_list:
                    node_list.append(temp_node)
                    node_dict = {'id': temp_node}
                    graph_as_dict.append({'data': node_dict})

            edge_dict = {
                'id': 'edge' + str(i),
                'source': edge.get_source(),
                'target': edge.get_destination()
            }

            graph_as_dict.append({'data': edge_dict})

        graphs_as_json.append(json.dumps(graph_as_dict))

    return graphs_as_json


class AddAttrTree(Treeprocessor):
    def run(self, root):
        highest_heading = None
        new_highest_heading = 3  # h3 is the top level is the result

        for heading in range(1, 7):
            if root.find('h' + str(heading)):
                highest_heading = heading
                break

        for h2 in root.iter('h2'):
            h2.tag = 'h4'
            h2.attrib['class'] = 'yo'


class DotBlockProcessor(BlockProcessor):

    RE = re.compile(r'^..\s+(\w+)\s*::')

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
                div = etree.SubElement(parent, 'div')
                div.set('gtype', block_type)
        else:
            div = self.lastChild(parent)

        if rest:
            blocks.insert(0, rest)

        div.text = str(graph_to_json(block))


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


with open('markdown_with_dot.md', 'r') as f:
    extensions = [AddAttrExt(), DotBlockExt()]
    html = markdown.markdown(f.read(), extensions=extensions)
    print(html)
