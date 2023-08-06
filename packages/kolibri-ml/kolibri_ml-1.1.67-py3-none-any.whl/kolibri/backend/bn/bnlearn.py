import numpy as np
import pandas as pd
from kolibri.backend.bn.metrics import structure_score
import itertools
from tabulate import tabulate
from decimal import Decimal
from kolibri.backend.bn.BayesianNetwork import BayesianNetwork
from kolibri.backend.bn.NaiveBayes import NaiveBayes
import networkx as nx
from kolibri.backend.bn import network
import os
import matplotlib.pyplot as plt
from kolibri.backend.bn import bnlearn
import requests
from ismember import ismember
from tqdm import tqdm
from pathlib import Path
import pypickle
import re
import pickle

# %% Get node properties
def get_node_properties(model, node_color='#1f456e', node_size=None, verbose=3):
    """Collect node properties.

    Parameters
    ----------
    model : dict
        dict containing (initialized) model.
    node_color : str, (Default: '#000000')
        The default color of the edges.
    node_size : float, (Default: 1)
        The default weight of the edges.
    Print progress to screen. The default is 3.
        0: None, 1: ERROR, 2: WARN, 3: INFO (default), 4: DEBUG, 5: TRACE

    Returns
    -------
    dict.
        Node properties.

    Examples
    --------


    """
    # https://networkx.org/documentation/networkx-1.7/reference/generated/networkx.drawing.nx_pylab.draw_networkx_nodes.html
    nodes = {}
    defaults={'node_color': node_color, 'node_size': node_size}
    adjmat = model.get('adjmat', None)

    if adjmat is not None:
        if verbose>=3: print('[bnlearn] >Set node properties.')
        # For each node, use the default node properties.
        for node in adjmat.columns:
            node_property = defaults.copy()
            nodes.update({node: node_property})

    # Return dict with node properties
    return nodes


# %% Get node properties
def get_edge_properties(model, color='#000000', weight=1, minscale=1, maxscale=10, verbose=3):
    """Collect edge properties.

    Parameters
    ----------
    model : dict
        dict containing (initialized) model.
    color : str, (Default: '#000000')
        The default color of the edges.
    weight : float, (Default: 1)
        The default weight of the edges.
    minscale : float, (Default: 1)
        The minimum weight of the edge in case of test statisics are used.
    maxscale : float, (Default: 10)
        The maximum weight of the edge in case of test statisics are used.
    verbose : int, optional
        Print progress to screen. The default is 3.
        0: None, 1: ERROR, 2: WARN, 3: INFO (default), 4: DEBUG, 5: TRACE

    Returns
    -------
    dict.
        Edge properties.

    Examples
    --------

    """
    # https://networkx.org/documentation/networkx-1.7/reference/generated/networkx.drawing.nx_pylab.draw_networkx_nodes.html
    edges = {}
    defaults = {'color': color, 'weight': weight}
    adjmat = model.get('independence_test', None)
    # Use edge weights from test statistic
    if adjmat is not None:
        if verbose>=3: print('[bnlearn]> Set edge weights based on the [%s] test statistic.' %(model['independence_test'].columns[-2]))
        logp = -np.log10(model['independence_test']['p_value'])
        logp[np.isinf(logp)] = logp[np.isfinite(logp)].max()
        weights = _normalize_weights(logp.values, minscale=minscale, maxscale=maxscale)
        adjmat = vec2adjmat(model['independence_test']['source'], model['independence_test']['target'], weights=weights)
    else:
        adjmat = model.get('adjmat', None)

    # Get model edges
    model_edges = adjmat2vec(adjmat)[['source', 'target']].values
    # model_edges = model['model'].edges() if (model.get('model_edges', None) is None) else model['model_edges']

    # Store edge properties
    if adjmat is not None:
        if verbose>=3: print('[bnlearn] >Set edge properties.')
        # For each edge, use the default properties.
        for u, v in model_edges:
            edge_property = defaults.copy()
            # Use the edge weight from the adjmat
            if not isinstance(adjmat.loc[u, v], np.bool_):
                edge_property['weight']=adjmat.loc[u, v]
            # Update edges dict
            edges.update({(u, v): edge_property})

    # Return dict with node properties
    return edges


# %% Normalize weights in range
def _normalize_weights(weights, minscale=1, maxscale=10):
    if len(weights.shape)==1:
        weights=weights.reshape(-1, 1)

    from sklearn.preprocessing import MinMaxScaler
    weights = MinMaxScaler(feature_range=(minscale, maxscale)).fit_transform(weights).flatten()
    return(weights)

# %% Plot properties
def _plot_properties(G, node_properties, edge_properties, node_color, node_size):
    # Set edge properties in Graph G
    # edges=[*bnmodel.edges()]
    edges = list(edge_properties.keys())
    for edge in edges:
        color = edge_properties.get((edge[0], edge[1])).get('color', '#000000')
        weight = edge_properties.get((edge[0], edge[1])).get('weight', 1)
        G.add_edge(edge[0], edge[1], weight=weight, color=color)
        # arrowstyle = edge_properties.get((edge[0], edge[1])).get('arrowstyle', '-|>')
        # arrowsize = edge_properties.get((edge[0], edge[1])).get('arrowsize', 30)
        # G.add_edge(edge[0], edge[1], weight=weight, color=color, arrowstyle=arrowstyle, arrowsize=arrowsize)

    edgelist = list(G.edges())
    edge_colors = [G[u][v].get('color') for u, v in G.edges()]
    edge_weights = [G[u][v].get('weight') for u, v in G.edges()]
    # edge_arrowstyles = [G[u][v].get('arrowstyle') for u, v in G.edges()]
    # edge_arrowsizes = [G[u][v].get('arrowsize') for u, v in G.edges()]

    # Node properties
    nodelist = np.unique(edgelist)
    node_colors = []
    node_sizes = []
    for node in nodelist:
        if node_color is not None:
            node_colors.append(node_color)
        else:
            node_colors.append(node_properties[node].get('node_color'))
        if node_size is not None:
            node_sizes.append(node_size)
        else:
            node_sizes.append(node_properties[node].get('node_size'))
    # Return
    return nodelist, node_colors, node_sizes, edgelist, edge_colors, edge_weights



# %% PLOT
def plot(model,
         pos=None,
         scale=1,
         interactive=False,
         title='bnlearn_causal_network',
         node_color=None,
         node_size=None,
         node_properties=None,
         edge_properties=None,
         params_interactive={'width': '70%', 'height': '800px', 'notebook': False, 'layout': None, 'font_color': False, 'bgcolor': '#ffffff', 'select_menu': True, 'filter_menu': True, 'cdn_resources': 'remote'},
         params_static={'minscale': 1, 'maxscale': 10, 'figsize': (15, 10), 'width': None, 'height': None, 'font_size': 14, 'font_family': 'sans-serif', 'alpha': 0.8, 'node_shape': 'o', 'layout': 'spring_layout', 'font_color': '#000000', 'facecolor': 'white', 'edge_alpha': 0.8, 'arrowstyle': '-|>', 'arrowsize': 30, 'visible': True},
         verbose=3, visible=True):
    """Plot the learned stucture.

    Parameters
    ----------
    model : dict
        Learned model from the .fit() function.
    pos : graph, optional
        Coordinates of the network. If there are provided, the same structure will be used to plot the network.. The default is None.
    scale : int, optional
        Scaling parameter for the network. A larger number will linearily increase the network.. The default is 1.
    interactive : Bool, (default: True)
        True: Interactive web-based graph.
        False: Static plot
    title : str, optional
        Title for the plots.
    node_color : str, optional
        Color each node in the network using a hex-color, such as '#8A0707'
    node_size : int, optional
        Set the node size for each node in the network. The default size when using static plolts is 800, and for interactive plots it is 10.
    node_properties : dict (default: None)
        Dictionary containing custom node_color and node_size parameters for the network.
        The node properties can easily be retrieved using the function: node_properties = bn.get_node_properties(model)
        node_properties = {'node1':{'node_color':'#8A0707','node_size':10},
                           'node2':{'node_color':'#000000','node_size':30}}
    edge_properties : dict (default: None).
        Dictionary containing custom node_color and node_size parameters for the network. The edge properties can be retrieved with:
        edge_properties = bn.get_edge_properties(model)
    params_interactive : dict.
        Dictionary containing various settings in case of creating interactive plots.
    params_static : dict.
        Dictionary containing various settings in case of creating static plots.
        layout: 'spring_layout', 'planar_layout', 'shell_layout', 'spectral_layout', 'pydot_layout', 'graphviz_layout', 'circular_layout', 'spring_layout', 'random_layout', 'bipartite_layout', 'multipartite_layout',
    verbose : int, optional
        Print progress to screen. The default is 3.
        0: None, 1: Error, 2: Warning, 3: Info (default), 4: Debug, 5: Trace

    Returns
    -------
    dict containing pos and G
        pos : list.
            Positions of the nodes.
        G : Graph.
            Graph model
        node_properties: dict.
            Node properties.

    Examples
    --------

    """
    fig = None
    # Check whether edges are available
    if model['adjmat'].sum().sum()==0:
        if verbose>=3: print('[bnlearn]> Nothing to plot because no edges are present between nodes. ')
        return None

    # Plot properties
    defaults = {'height': '800px', 'width': '70%', 'notebook': False, 'layout': None, 'font_color': False, 'bgcolor': '#ffffff', 'directed': True, 'cdn_resources': 'remote', 'select_menu': True, 'filter_menu': True}
    params_interactive = {**defaults, **params_interactive}
    defaults = {'minscale': 1, 'maxscale': 10, 'figsize': (15, 10), 'height': None, 'width': None, 'font_size': 14, 'font_family': 'sans-serif', 'alpha': 0.8, 'layout': 'spring_layout', 'font_color': 'k', 'facecolor': '#ffffff', 'node_shape': 'o', 'edge_alpha': 0.8, 'arrowstyle': '-|>', 'arrowsize': 30, 'visible': True}
    params_static = {**defaults, **params_static}
    params_static['visible']=visible
    # DEPRECATED IN LATER VERSION
    if (params_static.get('width') is not None) or (params_static.get('height') is not None):
        # if verbose>=2: print('[bnlearn]> Warning: [height] and [width] will be removed in further version. Please use: params_static={"figsize": (15, 10)}.')
        params_static['figsize'] = (15 if params_static['width'] is None else params_static['width'], 10 if params_static['height'] is None else params_static['height'])
    # END BLOCK

    out = {}
    G = nx.DiGraph()  # Directed graph
    node_size_default = 10 if interactive else 800
    if (node_properties is not None) and (node_size is not None):
        if verbose>=2: print('[bnlearn]> Warning: if both "node_size" and "node_properties" are used, "node_size" will be used.')

    # Get node and edge properties if not user-defined
    if node_properties is None:
        node_properties = get_node_properties(model, node_size=node_size_default)
    if edge_properties is None:
        edge_properties = get_edge_properties(model, minscale=params_static['minscale'], maxscale=params_static['maxscale'])

    # Set default node size based on interactive True/False
    for key in node_properties.keys():
        if node_properties[key]['node_size'] is None:
            node_properties[key]['node_size']=node_size_default

    # Extract model if in dict
    if 'dict' in str(type(model)):
        bnmodel = model.get('model', None)
    else:
        bnmodel = model.copy()

    # get node properties
    nodelist, node_colors, node_sizes, edgelist, edge_colors, edge_weights = _plot_properties(G, node_properties, edge_properties, node_color, node_size)

    # Bayesian model
    if ('bayes' in str(type(bnmodel)).lower()) or ('pgmpy' in str(type(bnmodel)).lower()):
        if verbose>=3: print('[bnlearn] >Plot based on Bayesian model')
        # positions for all nodes
        G = nx.DiGraph(model['adjmat'])
        pos = network.graphlayout(G, pos=pos, scale=scale, layout=params_static['layout'], verbose=verbose)
    elif 'networkx' in str(type(bnmodel)):
        if verbose>=3: print('[bnlearn] >Plot based on networkx model')
        G = bnmodel
        pos = network.graphlayout(G, pos=pos, scale=scale, layout=params_static['layout'], verbose=verbose)
    else:
        if verbose>=3: print('[bnlearn] >Plot based on adjacency matrix')
        G = network.adjmat2graph(model['adjmat'])
        # Get positions
        pos = network.graphlayout(G, pos=pos, scale=scale, layout=params_static['layout'], verbose=verbose)

    # Plot
    if interactive:
        # Make interactive plot
        fig = _plot_interactive(model, params_interactive, nodelist, node_colors, node_sizes, edgelist, edge_colors, edge_weights, title, verbose=verbose)
    else:
        # Make static plot
        fig = _plot_static(model, params_static, nodelist, node_colors, node_sizes, G, pos, edge_colors, edge_weights, visible=params_static['visible'])

    # Store
    out['fig']=fig
    out['ax']=fig  # Should be removed in later releases
    out['pos']=pos
    out['G']=G
    out['node_properties']=node_properties
    out['edge_properties']=edge_properties
    return out




# %% Plot interactive
# def _plot_static(model, params_static, nodelist, node_colors, node_sizes, title, verbose=3):
def _plot_static(model, params_static, nodelist, node_colors, node_sizes, G, pos, edge_colors, edge_weights, visible=True):
    # Bootup figure
    fig = plt.figure(figsize=params_static['figsize'], facecolor=params_static['facecolor'])
    # nodes
    nx.draw_networkx_nodes(G, pos, nodelist=nodelist, node_size=node_sizes, alpha=params_static['alpha'], node_color=node_colors, node_shape=params_static['node_shape'])
    # edges
    # nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=30, edge_color=edge_color, width=edge_weights)
    nx.draw_networkx_edges(G, pos, arrowstyle=params_static['arrowstyle'], arrowsize=params_static['arrowsize'], edge_color=edge_colors, width=edge_weights, alpha=params_static['edge_alpha'])
    # Labels
    nx.draw_networkx_labels(G, pos, font_size=params_static['font_size'], font_family=params_static['font_family'], font_color=params_static['font_color'])
    # Plot text of the weights
    # nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'), font_color=params_static['font_color'])
    # Making figure nice
    # fig = plt.gca()
    # fig.set_axis_off()
    if visible:
        plt.show()
    # Return
    return fig



# %% Plot interactive
def _plot_interactive(model, params_interactive, nodelist, node_colors, node_sizes, edgelist, edge_colors, edge_weights, title, verbose=3):
    # If not notebook
    if not params_interactive['notebook']:
        # https://pyvis.readthedocs.io/en/latest/tutorial.html?highlight=cdn_resources#using-pyvis-within-jupyter-notebook
        params_interactive['cdn_resources']='local'

    # Try to import pyvis
    try:
        from pyvis.network import Network
        from IPython.core.display import display, HTML
    except ModuleNotFoundError:
        if verbose>=1: raise Exception('[bnlearn] >"pyvis" module is not installed. Please pip install first: "pip install pyvis"')
    # Convert adjacency matrix into Networkx Graph
    G = network.adjmat2graph(model['adjmat'])
    # Setup of the interactive network figure
    g = Network(**params_interactive)
    # Convert from graph G
    g.from_nx(G)
    # Nodes
    for i, _ in enumerate(g.nodes):
        g.nodes[i]['color']=node_colors[np.where(nodelist==g.nodes[i].get('label'))[0][0]]
        g.nodes[i]['size']=node_sizes[np.where(nodelist==g.nodes[i].get('label'))[0][0]]

    # Edges
    g_edges = list(map(lambda x: (x.get('from'), x.get('to')), g.edges))
    for i, _ in enumerate(g.edges):
        idx = np.where(list(map(lambda x: g_edges[i]==x, edgelist)))[0][0]
        g.edges[i]['color']=edge_colors[idx]
        g.edges[i]['weight']=edge_weights[idx]

    # Create advanced buttons
    g.show_buttons(filter_=['physics'])
    # Display
    filename = title.strip().replace(' ', '_') + '.html'
    g.show(filename, local=params_interactive['notebook'])
    display(HTML(filename))
    # webbrowser.open('bnlearn.html')
    return os.path.abspath(filename)


# %% Make DAG
def make_DAG(DAG, CPD=None, methodtype='bayes', checkmodel=True, verbose=3):
    """Create Directed Acyclic Graph based on list.

    Parameters
    ----------
    DAG : list
        list containing source and target in the form of [('A','B'), ('B','C')].
    CPD : list, array-like
        Containing TabularCPD for each node.
    methodtype : str (default: 'bayes')
        * 'bayes': Bayesian model
        * 'nb' or 'naivebayes': Special case of Bayesian Model where the only edges in the model are from the feature variables to the dependent variable. Or in other words, each tuple should start with the same variable name such as: edges = [('A', 'B'), ('A', 'C'), ('A', 'D')]
        * 'markov': Markov model
    checkmodel : bool
        Check the validity of the model. The default is True
    verbose : int, optional
        Print progress to screen. The default is 3.
        0: None, 1: ERROR, 2: WARN, 3: INFO (default), 4: DEBUG, 5: TRACE

    Returns
    -------
    dict keys:
        * 'adjmat': Adjacency matrix
        * 'model': pgmpy.models
        * 'methodtype': methodtype
        * 'model_edges': Edges

    Examples
    --------

    """
    if (CPD is not None) and (not isinstance(CPD, list)):
        CPD=[CPD]

    if methodtype=='nb': methodtype='naivebayes'

    if isinstance(DAG, dict):
        DAG = DAG.get('model', None)

    if (not isinstance(DAG, list)) and ('pgmpy' not in str(type(DAG))):
        raise Exception("[bnlearn] >Error: Input DAG should be a list. in the form [('A','B'), ('B','C')] or a <pgmpy.models.BayesianNetwork>")
    elif ('pgmpy' in str(type(DAG))):
        # Extract methodtype from existing model.
        if ('bayesianmodel' in str(type(DAG)).lower()):
            methodtype='bayes'
        elif('naivebayes' in str(type(DAG)).lower()):
            methodtype='naivebayes'
        if verbose>=3: print('[bnlearn] >No changes made to existing %s DAG.' %(methodtype))
    elif isinstance(DAG, list) and methodtype=='naivebayes':
        if verbose>=3: print('[bnlearn] >%s DAG created.' %(methodtype))
        edges=DAG
        DAG = NaiveBayes()
        DAG.add_edges_from(edges)
        # modeel.add_nodes_from(DAG)
    elif isinstance(DAG, list) and methodtype=='bayes':
        if verbose>=3: print('[bnlearn] >%s DAG created.' %(methodtype))
        DAG = BayesianNetwork(DAG)
    elif isinstance(DAG, list) and methodtype=='markov':
        from kolibri.backend.bn.MarkovNetwork import MarkovNetwork
        if verbose>=3: print('[bnlearn] >%s DAG created.' %(methodtype))
        DAG = MarkovNetwork(DAG)

    if CPD is not None:
        for cpd in CPD:
            DAG.add_cpds(cpd)
            if verbose>=3: print('[bnlearn] >Add CPD: %s' %(cpd.variable))
        # Check model
        if checkmodel:
            check_model(DAG, verbose=verbose)

    # Create adjacency matrix from DAG
    out = {}
    out['adjmat'] = dag2adjmat(DAG)
    out['model'] = DAG
    out['methodtype'] = methodtype
    out['model_edges'] = DAG.edges()
    return out



# %%  Convert adjacency matrix to vector
def vec2adjmat(source, target, weights=None, symmetric=True):
    """Convert source and target into adjacency matrix.

    Parameters
    ----------
    source : list
        The source node.
    target : list
        The target node.
    weights : list of int
        The Weights between the source-target values
    symmetric : bool, optional
        Make the adjacency matrix symmetric with the same number of rows as columns. The default is True.

    Returns
    -------
    pd.DataFrame
        adjacency matrix.

    Examples
    --------

    """
    if len(source)!=len(target): raise ValueError('[hnet] >Source and Target should have equal elements.')
    if weights is None: weights = [1] *len(source)

    df = pd.DataFrame(np.c_[source, target], columns=['source', 'target'])
    # Make adjacency matrix
    adjmat = pd.crosstab(df['source'], df['target'], values=weights, aggfunc='sum').fillna(0)
    # Get all unique nodes
    nodes = np.unique(list(adjmat.columns.values) +list(adjmat.index.values))
    # nodes = np.unique(np.c_[adjmat.columns.values, adjmat.index.values].flatten())

    # Make the adjacency matrix symmetric
    if symmetric:
        # Add missing columns
        node_columns = np.setdiff1d(nodes, adjmat.columns.values)
        for node in node_columns:
            adjmat[node]=0

        # Add missing rows
        node_rows = np.setdiff1d(nodes, adjmat.index.values)
        adjmat=adjmat.T
        for node in node_rows:
            adjmat[node]=0
        adjmat=adjmat.T

        # Sort to make ordering of columns and rows similar
        [IA, IB] = ismember(adjmat.columns.values, adjmat.index.values)
        adjmat = adjmat.iloc[IB, :]
        adjmat.index.name='source'
        adjmat.columns.name='target'

    return(adjmat)


# %% Convert DAG into adjacency matrix
def dag2adjmat(model, verbose=3):
    """Convert model into adjacency matrix.

    Parameters
    ----------
    model : object
        Model object.
    verbose : int, optional
        Print progress to screen. The default is 3.
        0: None, 1: ERROR, 2: WARN, 3: INFO (default), 4: DEBUG, 5: TRACE

    Returns
    -------
    pd.DataFrame
        adjacency matrix.

    Examples
    --------


    """
    adjmat = None
    if hasattr(model, 'nodes') and hasattr(model, 'edges'):
        adjmat = pd.DataFrame(data=False, index=model.nodes(), columns=model.nodes()).astype('bool')
        # Fill adjmat with edges
        edges = model.edges()
        # Run over the edges
        for edge in edges:
            adjmat.loc[edge[0], edge[1]]=True
        adjmat.index.name='source'
        adjmat.columns.name='target'
    else:
        if verbose>=1: print('[bnlearn] >Could not convert to adjmat because nodes and/or edges were missing.')
    return(adjmat)


# %% Check model CPDs
def check_model(DAG, verbose=3):
    """Check if the CPDs associated with the nodes are consistent.

    Parameters
    ----------
    DAG : Object.
        Object containing CPDs.
    verbose : int, optional
        Print progress to screen. The default is 3.
        0: None, 1: ERROR, 2: WARN, 3: INFO (default), 4: DEBUG, 5: TRACE

    Returns
    -------
    None.

    """
    if verbose>=3: print('[bnlearn] >Check whether CPDs sum up to one.')
    if isinstance(DAG, dict): DAG = DAG.get('model', None)
    if DAG is not None:
        for cpd in DAG.get_cpds():
            if not np.all(cpd.values.astype(Decimal).sum(axis=0)==1):
                if verbose>=3: print('[bnlearn] >CPD [%s] does not add up to 1 but is: %s' %(cpd.variable, cpd.values.sum(axis=0)))
        if verbose>=3: print('[bnlearn] >Check whether CPDs associated with the nodes are consistent: %s' %(DAG.check_model()))
    else:
        if verbose>=2: print('[bnlearn] >No model found containing CPDs.')
def query2df(query, variables=None, verbose=3):
    """Convert query from inference model to a dataframe.

    Parameters
    ----------
    query : Object from the inference model.
        Convert query object to a dataframe.
    variables : list
        Order or select variables.

    Returns
    -------
    df : pd.DataFrame()
        Dataframe with inferences.

    """
    states = []
    getP = []
    for value_index, prob in enumerate(itertools.product(*[range(card) for card in query.cardinality])):
        states.append(prob)
        getP.append(query.values.ravel()[value_index])

    df = pd.DataFrame(data=states, columns=query.scope())
    df['p'] = getP
    # Order or filter on input variables
    if variables is not None:
        # Add Pvalue column
        variables = variables + ['p']
        df = df[variables]

    # Print table to screen
    if verbose>=3:
        print('[bnlearn] >Data is stored in [query.df]')
        print(tabulate(df, tablefmt="grid", headers="keys"))

    return df
def print_CPD(DAG, checkmodel=False, verbose=3):
    """Print DAG-model to screen.

    Parameters
    ----------
    DAG : pgmpy.models.BayesianNetwork
        model of the DAG.
    checkmodel : bool
        Check the validity of the model. The default is True

    Returns
    -------
    dict
        Dictionary containing the CPDs.

    Examples
    --------

    """
    # config = None
    CPDs = {}
    if isinstance(DAG, dict):
        DAG = DAG.get('model', None)

    # Print CPDs
    # if config['method']=='ml' or config['method']=='maximumlikelihood':
    try:
        if ('markovnetwork' in str(type(DAG)).lower()):
            if verbose>=3: print('[bnlearn] >Converting markovnetwork to Bayesian model')
            DAG=DAG.to_bayesian_model()

        if 'MaximumLikelihood' in str(type(DAG)):
            # print CPDs using Maximum Likelihood Estimators
            for node in DAG.state_names:
                print(DAG.estimate_cpd(node))
        elif ('bayesiannetwork' in str(type(DAG)).lower()) or ('naivebayes' in str(type(DAG)).lower()):
            # print CPDs using Bayesian Parameter Estimation
            if len(DAG.get_cpds())==0:
                raise Exception('[bnlearn] >Error! This is a Bayesian DAG containing only edges, and no CPDs. Tip: you need to specify or learn the CPDs. Try: DAG=bn.parameter_learning.fit(DAG, df). At this point you can make a plot with: bn.plot(DAG).')
                return
            for cpd in DAG.get_cpds():
                CPDs[cpd.variable] = query2df(cpd, verbose=verbose)
                if verbose>=3:
                    print("CPD of {variable}:".format(variable=cpd.variable))
                    print(cpd)
            if ('bayesiannetwork' in str(type(DAG)).lower()):
                if verbose>=3: print('[bnlearn] >Independencies:\n%s' %(DAG.get_independencies()))

            if verbose>=3:
                print('[bnlearn] >Nodes: %s' %(DAG.nodes()))
                print('[bnlearn] >Edges: %s' %(DAG.edges()))

        if checkmodel:
            check_model(DAG, verbose=3)
    except Exception as e:
        print(e)
        if verbose>=2: print('[bnlearn] >No CPDs to print. Hint: Add CPDs as following: <bn.make_DAG(DAG, CPD=[cpd_A, cpd_B, etc])> and use bnlearn.plot(DAG) to make a plot.')

    # Returning dict with CPDs
    return CPDs

# %% Compute structure scores.
def structure_scores(model, df, scoring_method=['k2', 'bds', 'bic', 'bdeu'], verbose=3, **kwargs):
    """Compute structure scores.

    Description
    -----------
    Each model can be scored based on its structure. However, the score doesn't have very straight forward
    interpretebility but can be used to compare different models. A higher score represents a better fit.
    This method only needs the model structure to compute the score. The structure score functionality
    can be found here: :func:`bnlearn.bnlearn.structure_scores`.

    Parameters
    ----------
    model: The bnlearn instance such as pgmpy.base.DAG or pgmpy.models.BayesianNetwork
        The model whose score needs to be computed.

    df: pd.DataFrame instance
        The dataset against which to score the model.

    scoring_method: str ( k2 | bdeu | bds | bic )
        The following four scoring methods are supported currently: 1) K2Score
        2) BDeuScore 3) BDsScore 4) BicScore

    kwargs: kwargs
        Any additional parameters parameters that needs to be passed to the
        scoring method.

    Returns
    -------
    Model score: float
        A score value for the model.

    Examples
    --------
    """
    method = None
    show_message = True
    scores = {}
    # Get models and method
    if isinstance(model, dict):
        method = model.get('config')['method']
        model = model.get('model', None)
    if isinstance(scoring_method, str): scoring_method = [scoring_method]
    if verbose>=3: print('[bnlearn] >Compute structure scores %s for model comparison (higher is better).' %(scoring_method))

    # Return if method not supported
    if np.any(np.isin(method, ['cs', 'constraintsearch'])):
        if verbose>=2: print('[bnlearn] >Warning: Structure scoring could not be computed. Method [%s] not supported.' %(method))
        return scores

    # Compute structure scores
    if model is not None:
        for s in scoring_method:
            try:
                scores[s] = structure_score(model, df, scoring_method=s)
            except:
                if verbose>=2 and show_message:
                    print('[bnlearn] >Warning: Structure scoring could not be computed. DataFrame issues (?)')
                    show_message=False
    # Return
    return scores


def _filter_df(adjmat, df, verbose=3):
    """Adjacency matrix and dataframe columns are checked for consistency."""
    remcols = df.columns[~np.isin(df.columns.values, adjmat.columns.values)].values
    if len(remcols)>0:
        if verbose>=3: print('[bnlearn] >Removing columns from dataframe to make consistent with DAG [%s]' %(remcols))
        df.drop(labels=remcols, axis=1, inplace=True)
    return df


# %%  Convert adjacency matrix to vector
def adjmat2vec(adjmat, min_weight=1):
    """Convert adjacency matrix into vector with source and target.

    Parameters
    ----------
    adjmat : pd.DataFrame()
        Adjacency matrix.

    min_weight : float
        edges are returned with a minimum weight.

    Returns
    -------
    pd.DataFrame()
        nodes that are connected based on source and target

    Examples
    --------

    """
    # Convert adjacency matrix into vector
    adjmat = adjmat.stack().reset_index()
    # Set columns
    adjmat.columns = ['source', 'target', 'weight']
    # Remove self loops and no-connected edges
    Iloc1 = adjmat['source']!=adjmat['target']
    Iloc2 = adjmat['weight']>=min_weight
    Iloc = Iloc1 & Iloc2
    # Take only connected nodes
    adjmat = adjmat.loc[Iloc, :]
    adjmat.reset_index(drop=True, inplace=True)
    return(adjmat)

def to_bayesiannetwork(model, verbose=3):
    """Convert adjacency matrix to BayesianNetwork.

    Description
    -----------
    Convert a adjacency to a Bayesian model. This is required as some of the
    functionalities, such as ``structure_learning`` output a DAGmodel.
    If the output of ``structure_learning`` is provided, the adjmat is extracted and processed.

    Parameters
    ----------
    model : pd.DataFrame()
        Adjacency matrix.

    Raises
    ------
    Exception
        The input should not be None and if a model (as dict) is provided, the key 'adjmat' should be included.

    Returns
    -------
    BayesianNetwork : Object
        BayesianNetwork that can be used in ``parameter_learning.fit``.

    """
    if isinstance(model, dict):
        adjmat = model.get('adjmat', None)
    else:
        adjmat = model
    if adjmat is None: raise Exception('[bnlearn] >Error: input for "bayesiannetwork" should be adjmat or a dict containing a key "adjmat".')

    if verbose>=3: print('[bnlearn] >Converting adjmat to BayesianNetwork.')

    # Convert to vector
    vec = adjmat2vec(adjmat)[['source', 'target']].values.tolist()
    # Make BayesianNetwork
    bayesianmodel = BayesianNetwork(vec)
    # Return
    return bayesianmodel

# %%  Convert vector into sparse dataframe
def vec2df(source, target, weights=None):
    """Convert source-target edges into sparse dataframe.

    Description
    -----------
    Convert edges between source and taget into a dataframe based on the weight.
    A weight of 2 will result that a row with the edge is created 2x.

    Parameters
    ----------
    source : array-like
        The source node.
    target : array-like
        The target node.
    weights : array-like of int
        The Weights between the source-target values

    Returns
    -------
    pd.DataFrame

    Examples
    --------
    >>> # Example 1
    >>> import kolibri.backend.bn as bn
    >>> source=['Cloudy','Cloudy','Sprinkler','Rain']
    >>> target=['Sprinkler','Rain','Wet_Grass','Wet_Grass']
    >>> weights=[1,2,1,3]
    >>> df = bn.vec2df(source, target, weights=weights)

    >>> # Example 2
    >>> import kolibri.backend.bn as bn
    >>> vec = bn.import_example("stormofswords")
    >>> df = bn.vec2df(vec['source'], vec['target'], weights=vec['weight'])

    """
    if (isinstance(source, pd.DataFrame)) or (isinstance(source, pd.Series)):
        source=source.values
    if (isinstance(target, pd.DataFrame)) or (isinstance(target, pd.Series)):
        target=target.values
    if (isinstance(weights, pd.DataFrame)) or (isinstance(weights, pd.Series)):
        weights=weights.values

    rows = []
    edges = list(zip(source, target))
    if weights is None:
        weights = np.ones_like(source).astype(int)

    columns=np.unique(np.c_[source, target].ravel())
    for i, edge in enumerate(edges):
        row = [np.logical_or(columns==edge[0], columns==edge[1])] * int(weights[i])
        rows = rows + row

    return pd.DataFrame(np.array(rows), columns=columns)

# %% Make directed graph from adjmatrix
def to_undirected(adjmat):
    """Transform directed adjacency matrix to undirected.

    Parameters
    ----------
    adjmat : np.array()
        Adjacency matrix.

    Returns
    -------
    Directed adjacency matrix : pd.DataFrame()
        Converted adjmat with undirected edges.

    """
    num_rows=adjmat.shape[0]
    num_cols=adjmat.shape[1]
    adjmat_directed=np.zeros((num_rows, num_cols), dtype=int)
    tmpadjmat=adjmat.astype(int)

    for i in range(num_rows):
        for j in range(num_cols):
            adjmat_directed[i, j] = tmpadjmat.iloc[i, j] + tmpadjmat.iloc[j, i]

    adjmat_directed=pd.DataFrame(index=adjmat.index, data=adjmat_directed, columns=adjmat.columns, dtype=bool)
    return(adjmat_directed)


def adjmat2dict(adjmat):
    """Convert adjacency matrix to dict.

    Parameters
    ----------
    adjmat : pd.DataFrame
        Adjacency matrix.

    Returns
    -------
    graph : dict
        Graph.

    """
    adjmat=adjmat.astype(bool)
    graph={}
    rows=adjmat.index.values
    for r in rows:
        graph.update({r: list(rows[adjmat.loc[r, :]])})
    return graph


# %%
def topological_sort(adjmat, start=None):
    """Topological sort.

    Description
    -----------
    Get nodes list in the topological sort order.

    Parameters
    ----------
    adjmat: pd.DataFrame or bnlearn object.
        Adjacency matrix.
    start: str, optional
        Start position. The default is None and the whole network is examined.

    Returns
    -------
    list
        Topological sort order.

    Example
    -----------
    import bnlearn as bn
    DAG = bn.import_DAG('sprinkler', verbose=0)
    bn.topological_sort(DAG, 'Rain')
    bn.topological_sort(DAG)


    References
    ----------
    https://stackoverflow.com/questions/47192626/deceptively-simple-implementation-of-topological-sorting-in-python

    """
    # Convert to adjmat
    if isinstance(adjmat, dict):
        adjmat = adjmat.get('adjmat', None)
    elif np.all(np.isin(adjmat.columns, ['source', 'target', 'weight'])):
        adjmat = vec2adjmat(adjmat['source'], adjmat['target'])

    # Convert to graph
    graph = adjmat2dict(adjmat)
    # Do the topological sort
    seen = set()
    stack = []    # path variable is gone, stack and order are new
    order = []    # order will be in reverse order at first
    if start is None:
        q = list(graph)
    else:
        q = [start]
    while q:
        v = q.pop()
        if v not in seen:
            seen.add(v)  # no need to append to path any more
            q.extend(graph[v])

            while stack and v not in graph[stack[-1]]:  # new stuff here!
                order.append(stack.pop())
            stack.append(v)

    return stack + order[::-1]


# %% Download data from github source
def _download_example(data, verbose=3):
    # Set url location
    url = 'https://erdogant.github.io/datasets/'
    url=url + data + '.zip'

    curpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    PATH_TO_DATA = os.path.join(curpath, wget.filename_from_url(url))
    if not os.path.isdir(curpath):
        os.mkdir(curpath)

    # Check file exists.
    if not os.path.isfile(PATH_TO_DATA):
        if verbose>=3: print('[bnlearn] >Downloading example [%s] dataset..' %(data))
        wget.download(url, PATH_TO_DATA)

    return PATH_TO_DATA

# %% Pre-processing of input raw dataset
def df2onehot(df, y_min=10, perc_min_num=0.8, dtypes='pandas', excl_background=None, verbose=3):
    """Convert dataframe to one-hot matrix.

    Parameters
    ----------
    df : pd.DataFrame()
        Input dataframe for which the rows are the features, and colums are the samples.
    dtypes : list of str or 'pandas', optional
        Representation of the columns in the form of ['cat','num']. By default the dtype is determiend based on the pandas dataframe.
    y_min : int [0..len(y)], optional
        Minimal number of sampels that must be present in a group. All groups with less then y_min samples are labeled as _other_ and are not used in the enriching model. The default is None.
    perc_min_num : float [None, 0..1], optional
        Force column (int or float) to be numerical if unique non-zero values are above percentage. The default is None. Alternative can be 0.8
    verbose : int, optional
        Print message to screen. The default is 3.
        0: None, 1: ERROR, 2: WARN, 3: INFO (default), 4: DEBUG, 5: TRACE

    Returns
    -------
    pd.DataFrame()
        One-hot dataframe.

    """
    from df2onehot import df2onehot as df2hot

    # Convert dataframe to onehot by keeping only categorical variables.
    out = df2hot(df, y_min=y_min, perc_min_num=perc_min_num, dtypes=dtypes, excl_background=excl_background, hot_only=True, verbose=verbose)
    # Numerical
    df_num = out['numeric'].iloc[:, out['dtypes']=='cat']
    df_num = df_num.astype(int)
    # One-hot
    df_hot = out['onehot']
    df_hot.columns = df_hot.columns.str.replace('_4.0', '_4', regex=True)
    df_hot.columns = df_hot.columns.str.replace('_3.0', '_3', regex=True)
    df_hot.columns = df_hot.columns.str.replace('_2.0', '_2', regex=True)
    df_hot.columns = df_hot.columns.str.replace('_1.0', '_1', regex=True)
    df_hot.columns = df_hot.columns.str.replace('_0.0', '_0', regex=True)

    return df_hot, df_num


# %% Make prediction in inference model
# @njit
def predict(model, df, variables, to_df=True, method='max', verbose=3):
    """Predict on data from a Bayesian network.

    Description
    -----------
    The inference on the dataset is performed sample-wise by using all the available nodes as evidence (obviously, with the exception of the node whose values we are predicting).
    The states with highest probability are returned.

    Parameters
    ----------
    model : Object
        An object of class from bn.fit.
    df : pd.DataFrame
        Each row in the DataFrame will be predicted
    variables : str or list of str
        The label(s) of node(s) to be predicted.
    to_df : Bool, (default is True)
        The output is converted to dataframe output. Note that this heavily impacts the speed.
    method : str
        The method that is used to select the for the inferences.
        'max' : Return the variable values based on the maximum probability.
        None : Returns all Probabilities
    verbose : int, optional
        Print progress to screen. The default is 3.
        0: None, 1: ERROR, 2: WARN, 3: INFO (default), 4: DEBUG, 5: TRACE

    Returns
    -------
    P : dict or DataFrame
        Predict() returns a dict with the evidence and states that resulted in the highest probability for the input variable.

    Examples
    --------
    >>> import kolibri.backend.bn.bnlearn as bn
    >>> model = bn.import_DAG('sprinkler')
    >>>
    >>> # Make single inference
    >>> query = bn.inference.fit(model, variables=['Rain', 'Cloudy'], evidence={'Wet_Grass':1})
    >>> print(query)
    >>> print(bn.query2df(query))
    >>>
    >>> # Lets create an example dataset with 100 samples and make inferences on the entire dataset.
    >>> df = bn.sampling(model, n=1000)
    >>>
    >>> # Each sample will be assesed and the states with highest probability are returned.
    >>> Pout = bn.predict(model, df, variables=['Rain', 'Cloudy'])
    >>>
    >>> print(Pout)
    >>> #     Cloudy  Rain         p
    >>> # 0        0     0  0.647249
    >>> # 1        0     0  0.604230
    >>> # ..     ...   ...       ...
    >>> # 998      0     0  0.604230
    >>> # 999      1     1  0.878049

    """
    if not isinstance(df, pd.DataFrame): raise Exception('[bnlearn] >Error: Input requires a pd.DataFrame.')
    if not isinstance(model, dict): raise Exception('[bnlearn] >Error: Input requires a dict that contains the key: model.')
    if isinstance(variables, str): variables=[variables]
    # Remove columns that are used as priors
    dfX = df.loc[:, ~np.isin(df.columns.values, variables)]
    if verbose>=3: print('[bnlearn]> Remaining columns for inference: %d' %(dfX.shape[1]))

    # Get only the unique records in the DataFrame to reduce computation time.
    dfU = dfX.drop_duplicates()
    dfU.reset_index(drop=True, inplace=True)
    # Make empty array
    P = np.array([None] *dfX.shape[0])

    evidences = list(map(lambda x: dfU.iloc[x, :].to_dict(), range(dfU.shape[0])))
    dfU_shape = dfU.shape[1]
    # for i in tqdm(range(dfU.shape[0])):
    for evidence in tqdm(evidences):
        # Get input data and create a dict.
        # evidence = dfU.iloc[i, :].to_dict()
        # Do the inference.
        query = bnlearn.inference.fit(model, variables=variables, evidence=evidence, to_df=False, verbose=0)
        # Find original location of the input data.
        # loc = np.sum((dfX==dfU.iloc[i, :]).values, axis=1)==dfU_shape
        loc = np.sum(dfX.values==[*evidence.values()], axis=1)==dfU_shape
        # Store inference
        P[loc] = _get_prob(query, method=method)

    # Make list
    P = list(P)
    # Make dataframe
    if to_df: P = pd.DataFrame(P)
    return P


# %%
def _get_prob(query, method='max'):
    # Setup all combinations
    allcomb = np.array(list(itertools.product([0, 1], repeat=len(query.variables))))
    # Get highest P-value and gather data
    Pq = query.values.flatten()
    if method=='max':
        idx = np.argmax(Pq)
        comb = allcomb[idx]
        p = Pq[idx]
        # Store in dict
        out = dict(zip(query.variables, comb))
        out['p']=p
    else:
        out = bnlearn.query2df(query).to_dict()
    return out


# %% Save model
def save(model, filepath='bnlearn_model.pkl', overwrite=False, verbose=3):
    """Save learned model in pickle file.

    Parameters
    ----------
    filepath : str, (default: 'bnlearn_model.pkl')
        Pathname to store pickle files.
    overwrite : bool, (default=False)
        Overwite file if exists.
    verbose : int, optional
        Show message. A higher number gives more informatie. The default is 3.

    Returns
    -------
    bool : [True, False]
        Status whether the file is saved.

    """
    if (filepath is None) or (filepath==''):
        filepath = 'bnlearn_model.pkl'
    if filepath[-4:] != '.pkl':
        filepath = filepath + '.pkl'
    filepath = str(Path(filepath).absolute())

    # Store data
    # storedata = {}
    # storedata['model'] = model
    # Save
    status = pypickle.save(filepath, model, overwrite=overwrite, verbose=verbose)
    # return
    return status

def _default_ouptut_file_name(pre_fix):
    file_name=pre_fix+'bnleran.model.pkl'

    return re.sub('[^A-Za-z0-9-\.]+', '', file_name)

def save_to_azure(model, container_name, pre_fix):
    """
    Save model
    Args:
        model_path:
    """

    connect_str=os.environ.get("STORAGE_CONTAINER_STRING")
    from kdmt.cloud.azure import  upload_file
    import tempfile
    td=tempfile.TemporaryDirectory()
    model_dir=td.name
    local_model_file = os.path.join(model_dir, _default_ouptut_file_name(pre_fix))
    pypickle.save(local_model_file, model)
#    joblib.dump(model, local_model_file)
    blob_model_file=_default_ouptut_file_name(pre_fix)
    upload_file(connect_str, container_name, local_model_file, blob_model_file, overwrite=True)

    return container_name



def load_from_azure(pre_fix, container_name=None):
    from kdmt.cloud.azure import get_blob
    connect_str=os.environ.get("STORAGE_CONTAINER_STRING")

    blob_model_file=_default_ouptut_file_name(pre_fix)

    downloader=get_blob(connect_str, container_name, blob_model_file)
    b = downloader.readall()
    model = pickle.loads(b)



    return model
# %% Load model.
def load(filepath='bnlearn_model.pkl', verbose=3):
    """Load learned model.

    Parameters
    ----------
    filepath : str
        Pathname to stored pickle files.
    verbose : int, optional
        Show message. A higher number gives more information. The default is 3.

    Returns
    -------
    Object.

    """
    if (filepath is None) or (filepath==''):
        filepath = 'bnlearn_model.pkl'
    if filepath[-4:]!='.pkl':
        filepath = filepath + '.pkl'
    filepath = str(Path(filepath).absolute())
    # Load
    model = pypickle.load(filepath, verbose=verbose)
    # Store in self.
    if model is not None:
        return model
    else:
        if verbose>=2: print('[bnlearn] >WARNING: Could not load data from [%s]' %(filepath))



# %% Remove not significant edges.
def _prune(model, test, alpha, verbose=3):
    independence_test = model.get('independence_test', None)

    # Prune based on significance alpha
    if independence_test is not None:
        # Find the none significant associations.
        Irem = ~independence_test['stat_test']
        idxrem = np.where(Irem)[0]

        # Set not-significant edges to False
        for idx in idxrem:
            edge = list(model['independence_test'].iloc[idx][['source', 'target']])
            model['adjmat'].loc[edge[0], edge[1]]=False
            model['adjmat'].loc[edge[1], edge[0]]=False
            # Remove edges
            if np.any(np.isin(model['model_edges'], edge).sum(axis=1)==2):
                model['model_edges'].remove((edge[0], edge[1]))
            # Remove from list
            if verbose>=3: print('[bnlearn] >Edge [%s <-> %s] [P=%g] is excluded because it was not significant (P<%.2f) with [%s]' %(edge[0], edge[1], model['independence_test'].iloc[idx]['p_value'], alpha, test))

        # Remove not-significant edges from the test statistics
        model['independence_test'] = model['independence_test'].loc[~Irem, :]
        model['independence_test'].reset_index(inplace=True, drop=True)

    # Return
    return model


# %% Retrieve files files.
class wget:
    """Retrieve file from url."""

    def filename_from_url(url):
        """Return filename."""
        return os.path.basename(url)

    def download(url, writepath):
        """Download.

        Parameters
        ----------
        url : str.
            Internet source.
        writepath : str.
            Directory to write the file.

        Returns
        -------
        None.

        """
        r = requests.get(url, stream=True)
        with open(writepath, "wb") as fd:
            for chunk in r.iter_content(chunk_size=1024):
                fd.write(chunk)