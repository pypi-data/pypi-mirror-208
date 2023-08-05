"""
some tests for the graph importers
"""

from itertools import product, combinations_with_replacement
from random import choice, random, randint, seed
from unittest import TestCase, main

from igraph import \
    Graph as IGraph
from graph_tool import \
    Graph as GTGraph
from networkx import \
    DiGraph as NXDiGraph, \
    Graph as NXGraph, \
    MultiDiGraph as NXMultiDiGraph, \
    MultiGraph as NXMultiGraph
from pygraphviz import AGraph

from yfiles_jupyter_graphs.graph import import_

seed(0)


def tuple_list_dict_of_lists_to_list_of_tuple_element_dicts(_list, dict_of_lists):
    """tuple(nodes, dict of lists) -> list of tuple(node, dicts)"""
    return [(e, {k: v[i] for k, v in dict_of_lists.items()}) for i, e in enumerate(_list)]


class GraphBuilder:
    def __init__(self, graph_class=None):
        self.graph_class = graph_class

    @staticmethod
    def get_graph_attributes(directed=False, multi=False):
        raise NotImplementedError()

    @staticmethod
    def get_vertices():
        a = '0'
        b = 1
        c = 'c'
        return [a, b, c]

    @staticmethod
    def get_vertex_attributes(vertices):
        raise NotImplementedError()

    @staticmethod
    def outer(func, multi=False, **kwargs):
        def inner(vertices):
            edges = list(func(vertices, **kwargs))
            if multi:
                edges += edges
            return edges

        return inner

    def get_edges(self, vertices, directed=False, multi=False):
        if directed:
            return self.outer(product, multi=multi, repeat=2)(vertices)
        return self.outer(combinations_with_replacement, multi=multi, r=2)(vertices)

    @staticmethod
    def get_edge_attributes(edges):
        raise NotImplementedError()

    def get_sample_data(self, directed=False, multi=False):
        vertices = self.get_vertices()
        edges = self.get_edges(vertices, directed=directed, multi=multi)
        return self.get_graph_attributes(), \
               vertices, \
               self.get_vertex_attributes(vertices), \
               edges, \
               self.get_edge_attributes(edges)

    @staticmethod
    def add_vertices(graph, vertices, **vertex_kwargs):
        raise NotImplementedError()

    @staticmethod
    def add_edges(graph, edges, **edge_kwargs):
        raise NotImplementedError()

    def build_graph(self, graph_kwargs, vertices, vertex_kwargs, edges, edge_kwargs):
        graph = self.graph_class(**graph_kwargs)
        self.add_vertices(graph, vertices, **vertex_kwargs)
        self.add_edges(graph, edges, **edge_kwargs)
        return graph

    def get_sample_graph(self, directed=False, multi=False):
        data = self.get_sample_data(directed=directed, multi=multi)
        return self.build_graph(*data)

    def __call__(self, directed=False, multi=False):
        return self.get_sample_graph(directed=directed, multi=multi)


class IGraphBuilder(GraphBuilder):
    def __init__(self):
        super().__init__(graph_class=IGraph)

    @staticmethod
    def get_graph_attributes(directed=False, multi=False):
        return dict(directed=directed)

    @staticmethod
    def get_vertex_attributes(vertices):
        return dict(attributes=dict(
            color=[choice(['red', 'green', 'blue']) for _ in vertices],
            size=[choice([0.4, 1.0, 0.3]) for _ in vertices]
        ))

    @staticmethod
    def get_edge_attributes(edges):
        return dict(attributes=dict(
            name=[str(x) + str(y) for x, y in edges],
            width=[random() for _ in edges]
        ))

    @staticmethod
    def add_vertices(graph, vertices, **vertex_kwargs):
        graph.add_vertices(vertices, **vertex_kwargs)

    @staticmethod
    def add_edges(graph, edges, **edge_kwargs):
        graph.add_edges(edges, **edge_kwargs)


class TestIGraphGraphImporter(TestCase):
    graph_builder = IGraphBuilder()

    def _check(self, graph, nodes, edges, directed):
        self.assertListEqual(graph.vs.get_attribute_values('name'), [n['properties']['name'] for n in nodes])
        self.assertListEqual(graph.es.get_attribute_values('name'), [e['properties']['name'] for e in edges])
        self.assertListEqual(graph.vs.get_attribute_values('color'), [n['properties']['color'] for n in nodes])
        self.assertListEqual(graph.vs.get_attribute_values('size'), [n['properties']['size'] for n in nodes])
        self.assertListEqual(graph.es.get_attribute_values('width'), [e['properties']['width'] for e in edges])
        self.assertEqual(graph.is_directed(), directed)

    def _test_graph(self, graph):
        _nodes, _edges, _directed = import_(graph)
        self._check(graph, _nodes, _edges, _directed)

    def test_igraph_undirected_non_multi(self):
        self._test_graph(self.graph_builder(False, False))

    def test_igraph_undirected_multi(self):
        self._test_graph(self.graph_builder(False, True))

    def test_igraph_directed_non_multi(self):
        self._test_graph(self.graph_builder(True, False))

    def test_igraph_directed_multi(self):
        self._test_graph(self.graph_builder(True, True))


class NetworkxGraphBuilder(GraphBuilder):

    def __init__(self):
        def graph_func(directed=False, multi=False):
            graph_class = NXGraph if not directed else NXDiGraph
            if multi:
                graph_class = NXMultiGraph if not directed else NXMultiDiGraph
            return graph_class()

        super().__init__(graph_class=graph_func)

    @staticmethod
    def get_graph_attributes(directed=False, multi=False):
        return dict(directed=directed, multi=multi)

    @staticmethod
    def get_vertex_attributes(vertices):
        return dict(
            color=[choice(['red', 'green', 'blue']) for _ in vertices],
            size=[choice([0.4, 1.0, 0.3]) for _ in vertices]
        )

    @staticmethod
    def get_edge_attributes(edges):
        return dict(
            width=[random() for _ in edges]
        )

    @staticmethod
    def add_vertices(graph, vertices, **vertex_kwargs):
        for k, v in vertex_kwargs.items():
            assert len(vertices) == len(v), f'{len(vertices)}!={len(v)}'
        w = tuple_list_dict_of_lists_to_list_of_tuple_element_dicts(vertices, vertex_kwargs)
        graph.add_nodes_from(w)

    @staticmethod
    def add_edges(graph, edges, **edge_kwargs):
        for k, v in edge_kwargs.items():
            assert len(edges) == len(v), f'{len(edges)}!={len(v)}'
        if edge_kwargs:
            w = tuple_list_dict_of_lists_to_list_of_tuple_element_dicts(edges, edge_kwargs)
            for e, d in w:
                graph.add_edge(*e, **d)
        graph.add_edges_from(edges)


class TestNetworkxGraphImporter(TestCase):
    graph_builder = NetworkxGraphBuilder()

    def _check(self, graph, nodes, edges, directed):
        self.assertListEqual([str(n) for n in graph.nodes], [n['properties']['label'] for n in nodes])
        __edges = [
            (nodes[e['start']]['properties']['label'],
             nodes[e['end']]['properties']['label']) for e in edges
        ]
        self.assertListEqual([(str(u), str(v)) for u, v, *_ in graph.edges], __edges)
        self.assertListEqual([graph.nodes[n] for n in graph.nodes], [n['properties'] for n in nodes])
        self.assertListEqual([graph.edges[e] for e in graph.edges], [e['properties'] for e in edges])
        self.assertEqual(graph.is_directed(), directed)

    def _test_graph(self, graph):
        _nodes, _edges, _directed = import_(graph)
        self._check(graph, _nodes, _edges, _directed)

    def test_nx_graph(self):
        self._test_graph(self.graph_builder(False, False))

    def test_nx_digraph(self):
        self._test_graph(self.graph_builder(True, False))

    def test_nx_multi_graph(self):
        self._test_graph(self.graph_builder(False, True))

    def test_nx_multi_digraph(self):
        self._test_graph(self.graph_builder(True, True))


class GraphToolGraphBuilder(GraphBuilder):
    def __init__(self):
        super().__init__(graph_class=GTGraph)

    @staticmethod
    def get_vertices():
        return range(4)

    @staticmethod
    def get_graph_attributes(directed=False, multi=False):
        return dict(directed=directed)

    @staticmethod
    def get_vertex_attributes(vertices):
        return dict(
            label=dict(values=[choice(['0', 'label', 'c', None]) for _ in vertices], type='string'),
            color=dict(values=[choice(['red', 'green', 'blue', None]) for _ in vertices], type='string'),
            size=dict(values=[choice([0.4, 1.0, 0.3, None]) for _ in vertices], type='float')
        )

    @staticmethod
    def get_edge_attributes(edges):
        return dict(
            label=dict(values=[str(x) + str(y) for x, y in edges], type='string'),
            width=dict(values=[random() for _ in edges], type='float')
        )

    @staticmethod
    def add_vertices(graph, vertices, **vertex_kwargs):
        graph.add_vertex(n=len(vertices))
        for k, v in vertex_kwargs.items():
            graph.vertex_properties[k] = graph.new_vertex_property(v['type'])
            for n, w in zip(graph.vertices(), v['values']):
                if w is not None:
                    graph.vertex_properties[k][n] = w

    @staticmethod
    def add_edges(graph, edges, **edge_kwargs):
        for s, t in edges:
            graph.add_edge(s, t)
        for k, v in edge_kwargs.items():
            graph.edge_properties[k] = graph.new_edge_property(v['type'])
            for e, w in zip(graph.edges(), v['values']):
                if w is not None:
                    graph.edge_properties[k][e] = w


class TestGTGraphGraphImporter(TestCase):
    graph_builder = GraphToolGraphBuilder()

    def _check_nodes(self, graph, nodes):
        def _get_vertex_properties(key):
            return [v[1] for v in graph.iter_vertices([getattr(graph.vertex_properties, key)])]

        self.assertListEqual(_get_vertex_properties('label'), [n['properties']['label'] for n in nodes])
        self.assertListEqual(_get_vertex_properties('color'), [n['properties']['color'] for n in nodes])
        self.assertListEqual(_get_vertex_properties('size'), [n['properties']['size'] for n in nodes])

    def _check_edges(self, graph, edges):
        def _get_edge_properties(key):
            return [e[2] for e in graph.iter_edges([getattr(graph.edge_properties, key)])]

        self.assertListEqual(_get_edge_properties('label'), [e['properties']['label'] for e in edges])
        self.assertListEqual(_get_edge_properties('width'), [e['properties']['width'] for e in edges])

    def _check(self, graph, nodes, edges, directed):
        self._check_nodes(graph, nodes)
        self._check_edges(graph, edges)
        self.assertEqual(graph.is_directed(), directed)

    def _test_graph(self, graph):
        nodes, edges, directed = import_(graph)
        self._check(graph, nodes, edges, directed)

    def test_undirected_non_multi_graph(self):
        self._test_graph(self.graph_builder(False, False))

    def test_undirected_multi_graph(self):
        self._test_graph(self.graph_builder(False, True))

    def test_directed_non_multi_graph(self):
        self._test_graph(self.graph_builder(True, False))

    def test_directed_multi_graph(self):
        self._test_graph(self.graph_builder(True, True))


class PyGraphvizBuilder(GraphBuilder):
    def __init__(self):
        super().__init__(graph_class=AGraph)

    @staticmethod
    def get_vertices():
        return ['1', '2', '3', ' ', 'f', 'g', 'h']

    @staticmethod
    def get_graph_attributes(directed=False, multi=False):
        return dict(directed=directed, strict=multi)

    @staticmethod
    def get_vertex_attributes(vertices):
        return dict(
            shape=[choice(['rarrow', None, 'square', 'diamond']) for _ in vertices],
            color=[choice(['red', 'green', 'blue']) for _ in vertices],
            label=[choice(['one', 'test', None]) for _ in vertices]
        )

    @staticmethod
    def get_edge_attributes(edges):
        return dict(
            label=[choice([None, choice(list('abcdefghijklmnopqrstuvwxyz')), str(randint(0, len(edges) - 1))]) for _ in
                   edges],
            len=[choice([None, str(randint(0, 99))]) for _ in edges],
            arrowhead=[choice([None, None, None, 'diamond']) for _ in edges]
        )

    @staticmethod
    def add_vertices(graph, vertices, **vertex_kwargs):
        vertices_and_properties = [
            (e, {k: None if i >= len(v) else v[i] for k, v in vertex_kwargs.items()})
            for i, e in enumerate(vertices)
        ]
        for v, p in vertices_and_properties:
            graph.add_node(v, **p)

    @staticmethod
    def add_edges(graph, edges, **edge_kwargs):
        edge_and_properties = [
            (e, {k: None if i >= len(v) else v[i] for k, v in edge_kwargs.items()})
            for i, e in enumerate(edges)
        ]
        for e, p in edge_and_properties:
            graph.add_edge(*e, **p)


class PygraphvizGraphTest(TestCase):
    graph_builder = PyGraphvizBuilder()

    @staticmethod
    def _property_factory(graph_elements):
        from yfiles_jupyter_graphs.graph.importer import pygraphviz_get_element_properties

        def _get_property(key):
            properties = []
            for index, element in enumerate(graph_elements):
                d = pygraphviz_get_element_properties(index, element)
                value = None if key not in d.keys() else d[key]
                properties.append(value)
            return properties

        return _get_property

    def _check_nodes(self, graph, nodes):
        _get_vertex_properties = self._property_factory(graph.nodes())

        for key in ['label', 'color', 'shape']:
            self.assertListEqual(_get_vertex_properties(key), [n['properties'][key] for n in nodes])

    def _check_edges(self, graph, edges):
        _get_edge_properties = self._property_factory(graph.edges())

        for key in ['label', 'len', 'arrowhead']:
            self.assertListEqual(_get_edge_properties(key), [e['properties'][key] for e in edges])

    def _check(self, graph, nodes, edges, directed):
        self._check_nodes(graph, nodes)
        self._check_edges(graph, edges)
        self.assertEqual(graph.is_directed(), directed)

    def _test_graph(self, graph):
        nodes, edges, directed = import_(graph)
        self._check(graph, nodes, edges, directed)

    def test_undirected_non_multi_graph(self):
        self._test_graph(self.graph_builder(False, False))

    def test_undirected_multi_graph(self):
        self._test_graph(self.graph_builder(False, True))

    def test_directed_non_multi_graph(self):
        self._test_graph(self.graph_builder(True, False))

    def test_directed_multi_graph(self):
        self._test_graph(self.graph_builder(True, True))


if __name__ == '__main__':
    main()
