import json
import pydot

dotobject = pydot.graph_from_dot_file('simple_digraph.dot')

for graph in dotobject:
    # print(graph.get_graph_type())

    node_list = []
    graph_as_dict = []

    for i, edge in enumerate(graph.get_edges()):
        # print(edge.get_source() + ' -> ' + edge.get_destination())

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

    graph_as_json = json.dumps(graph_as_dict)
    print(graph_as_json)
