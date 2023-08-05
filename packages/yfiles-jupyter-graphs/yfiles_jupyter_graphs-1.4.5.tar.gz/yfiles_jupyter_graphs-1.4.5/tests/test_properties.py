"""
stupid simple property tests
"""
from unittest import TestCase, main
from yfiles_jupyter_graphs import GraphWidget


class GraphWidgetPropertyTestCase(TestCase):
    def test_graph_layout_property(self):
        """ """
        graph_widget = GraphWidget()
        # initial
        self.assertEqual(graph_widget.graph_layout, {})

        # setter direct simple
        graph_widget.organic_layout()
        self.assertEqual(graph_widget.graph_layout, graph_widget.get_graph_layout())
        self.assertEqual(graph_widget.graph_layout, dict(algorithm='organic', options={}))

        # setter direct algorithm
        # noinspection PyTypeChecker
        graph_widget.set_graph_layout(algorithm='organic')
        self.assertEqual(graph_widget.graph_layout, graph_widget.get_graph_layout())
        self.assertEqual(graph_widget.graph_layout, dict(algorithm='organic', options={}))

        # setter direct algorithm from dict
        graph_widget.set_graph_layout(**dict(algorithm='circular'))
        self.assertEqual(graph_widget.graph_layout, graph_widget.get_graph_layout())
        self.assertEqual(graph_widget.graph_layout, dict(algorithm='circular', options={}))

        # indirect property algorithm
        graph_widget.graph_layout = dict(algorithm='orthogonal')
        self.assertEqual(graph_widget.graph_layout, graph_widget.get_graph_layout())
        self.assertEqual(graph_widget.graph_layout, dict(algorithm='orthogonal', options={}))

        # indirect property algorithm with options
        graph_widget.graph_layout = dict(algorithm='radial', options={'only_param': 'some stuff'})
        self.assertEqual(graph_widget.graph_layout, graph_widget.get_graph_layout())
        self.assertEqual(graph_widget.graph_layout, dict(algorithm='radial', options={}))

        # direct property algorithm
        graph_widget.graph_layout = 'tree'
        self.assertEqual(graph_widget.graph_layout, graph_widget.get_graph_layout())
        self.assertEqual(graph_widget.graph_layout, dict(algorithm='tree', options={}))

    # noinspection PyArgumentList
    # affects only max_distance argument/parameter
    # disappears if typing hints and default values are removed from signature
    # see long list of similar and/or possible issues with pycharm itself
    # https://youtrack.jetbrains.com/issue/PY-17877
    # https://youtrack.jetbrains.com/issue/PY-19701
    # https://youtrack.jetbrains.com/issue/PY-28663
    # https://youtrack.jetbrains.com/issue/PY-40845
    # https://intellij-support.jetbrains.com/hc/en-us/community/posts/360008130679--Unexpected-Argument-False-Warning

    def test_neighborhood_property(self):
        """ """
        graph_widget = GraphWidget()
        # initial
        self.assertEqual(graph_widget.neighborhood, {})

        # setter direct empty
        graph_widget.set_neighborhood()
        self.assertEqual(graph_widget.neighborhood, graph_widget.get_neighborhood())
        self.assertEqual(graph_widget.neighborhood, dict(max_distance=1, selected_nodes=[]))

        # setter direct max distance
        graph_widget.set_neighborhood(max_distance=3)
        self.assertEqual(graph_widget.neighborhood, graph_widget.get_neighborhood())
        self.assertEqual(graph_widget.neighborhood, dict(max_distance=3, selected_nodes=[]))

        # setter direct selected nodes
        graph_widget.set_neighborhood(selected_nodes=[0])
        self.assertEqual(graph_widget.neighborhood, graph_widget.get_neighborhood())
        self.assertEqual(graph_widget.neighborhood, dict(max_distance=1, selected_nodes=[0]))

        # setter direct max distance and selected nodes
        graph_widget.set_neighborhood(max_distance=4, selected_nodes=[1])
        self.assertEqual(graph_widget.neighborhood, graph_widget.get_neighborhood())
        self.assertEqual(graph_widget.neighborhood, dict(max_distance=4, selected_nodes=[1]))

        # indirect property max distance
        graph_widget.neighborhood = dict(max_distance=5)
        self.assertEqual(graph_widget.neighborhood, graph_widget.get_neighborhood())
        self.assertEqual(graph_widget.neighborhood, dict(max_distance=5, selected_nodes=[]))

        # indirect property selected nodes
        graph_widget.neighborhood = dict(selected_nodes=[1, 2])
        self.assertEqual(graph_widget.neighborhood, graph_widget.get_neighborhood())
        self.assertEqual(graph_widget.neighborhood, dict(max_distance=1, selected_nodes=[1, 2]))

        # indirect property max distance and selected nodes
        graph_widget.neighborhood = dict(max_distance=3, selected_nodes=[3, 4])
        self.assertEqual(graph_widget.neighborhood, graph_widget.get_neighborhood())
        self.assertEqual(graph_widget.neighborhood, dict(max_distance=3, selected_nodes=[3, 4]))

        # direct property max distance
        graph_widget.neighborhood = 5
        self.assertEqual(graph_widget.neighborhood, graph_widget.get_neighborhood())
        self.assertEqual(graph_widget.neighborhood, dict(max_distance=5, selected_nodes=[]))

    def test_sidebar_property(self):
        """ """
        graph_widget = GraphWidget()
        # initial
        self.assertEqual(graph_widget.sidebar, dict(enabled=True, start_with=''))

        # setter direct empty
        graph_widget = GraphWidget()
        graph_widget.set_sidebar()
        self.assertEqual(graph_widget.sidebar, graph_widget.get_sidebar())
        self.assertEqual(graph_widget.sidebar, dict(enabled=True, start_with=''))

        # setter direct enabled
        graph_widget = GraphWidget()
        # noinspection PyArgumentList
        graph_widget.set_sidebar(enabled=False)
        self.assertEqual(graph_widget.sidebar, graph_widget.get_sidebar())
        self.assertEqual(graph_widget.sidebar, dict(enabled=False, start_with=''))

        # setter direct start with
        graph_widget = GraphWidget()
        graph_widget.set_sidebar(start_with='Neighborhood')
        self.assertEqual(graph_widget.sidebar, graph_widget.get_sidebar())
        self.assertEqual(graph_widget.sidebar, dict(enabled=True, start_with='Neighborhood'))

        # setter direct both
        graph_widget = GraphWidget()
        # noinspection PyArgumentList
        graph_widget.set_sidebar(enabled=False, start_with='Data')
        self.assertEqual(graph_widget.sidebar, graph_widget.get_sidebar())
        self.assertEqual(graph_widget.sidebar, dict(enabled=False, start_with='Data'))

        # indirect property enabled
        graph_widget = GraphWidget()
        graph_widget.sidebar = dict(enabled=False)
        self.assertEqual(graph_widget.sidebar, graph_widget.get_sidebar())
        self.assertEqual(graph_widget.sidebar, dict(enabled=False, start_with=''))

        # indirect property start with
        graph_widget = GraphWidget()
        graph_widget.sidebar = dict(start_with='Search')
        self.assertEqual(graph_widget.sidebar, graph_widget.get_sidebar())
        self.assertEqual(graph_widget.sidebar, dict(enabled=True, start_with='Search'))

        # indirect property both
        graph_widget = GraphWidget()
        graph_widget.sidebar = dict(enabled=False, start_with='About')
        self.assertEqual(graph_widget.sidebar, graph_widget.get_sidebar())
        self.assertEqual(graph_widget.sidebar, dict(enabled=False, start_with='About'))

        # direct property
        graph_widget = GraphWidget()
        graph_widget.sidebar = False
        self.assertEqual(graph_widget.sidebar, graph_widget.get_sidebar())
        self.assertEqual(graph_widget.sidebar, dict(enabled=False, start_with=''))

    def test_overview_property(self):
        """ """
        graph_widget = GraphWidget()
        # initial
        self.assertEqual(graph_widget.overview, None)

        # setter direct
        graph_widget = GraphWidget()
        graph_widget.set_overview()
        self.assertEqual(graph_widget.overview, graph_widget.get_overview())
        self.assertEqual(graph_widget.overview, True)

        # indirect property
        graph_widget = GraphWidget()
        graph_widget.overview = False
        self.assertEqual(graph_widget.overview, graph_widget.get_overview())
        self.assertEqual(graph_widget.overview, False)


if __name__ == '__main__':
    main()
