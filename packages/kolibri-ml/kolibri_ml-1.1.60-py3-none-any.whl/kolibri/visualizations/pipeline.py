import pprint
from collections import OrderedDict
import numpy
import pandas
from sklearn.base import TransformerMixin, ClassifierMixin, RegressorMixin, BaseEstimator
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor



def _pipeline_info(pipe, data, context, former_data=None):
    """
    Internal function to convert a pipeline into
    some graph.
    """
    def _get_name(context, prefix='-v-', info=None, data=None):
        if info is None:
            raise RuntimeError("info should not be None")  # pragma: no cover
        if isinstance(prefix, list):
            return [_get_name(context, el, info, data) for el in prefix]
        if isinstance(prefix, int):
            prefix = former_data[prefix]
        if isinstance(prefix, int):
            raise TypeError(  # pragma: no cover
                f"prefix must be a string.\ninfo={info}")
        sug = "%s%d" % (prefix, context['n'])
        while sug in context['names']:
            context['n'] += 1
            sug = "%s%d" % (prefix, context['n'])
        context['names'][sug] = info
        return sug

    def _get_name_simple(name, data):
        if isinstance(name, str):
            return name
        res = data[name]
        if isinstance(res, int):
            raise RuntimeError(  # pragma: no cover
                f"Column name is still a number and not a name: {name} and {data}.")
        return res

    if isinstance(pipe, Pipeline):
        infos = []
        for _, model in pipe.steps:
            info = _pipeline_info(model, data, context)
            data = info[-1]["outputs"]
            infos.extend(info)
        return infos

    if isinstance(pipe, ColumnTransformer):
        infos = []
        outputs = []
        for _, model, vs in pipe.transformers:
            if all(map(lambda o: isinstance(o, int), vs)):
                new_data = []
                if isinstance(data, OrderedDict):
                    new_data = [_[1] for _ in data.items()]
                else:
                    mx = max(vs)
                    while len(new_data) < mx:
                        if len(data) > len(new_data):
                            new_data.append(data[len(new_data)])
                        else:
                            new_data.append(data[-1])
            else:
                new_data = OrderedDict()
                for v in vs:
                    new_data[v] = data.get(v, v)

            info = _pipeline_info(
                model, new_data, context, former_data=new_data)
            #new_outputs = []
            # for o in info[-1]['outputs']:
            #    add = _get_name(context, prefix=o, info=info)
            #    outputs.append(add)
            #    new_outputs.append(add)
            #info[-1]['outputs'] = new_outputs
            outputs.extend(info[-1]['outputs'])
            infos.extend(info)

        final_hat = False
        if pipe.remainder == "passthrough":

            done = [set(d['inputs']) for d in info]
            merged = done[0]
            for d in done[1:]:
                merged.union(d)
            new_data = OrderedDict(
                [(k, v) for k, v in data.items() if k not in merged])

            info = _pipeline_info(
                "passthrough", new_data, context, former_data=new_data)
            outputs.extend(info[-1]['outputs'])
            infos.extend(info)
            final_hat = True

        if len(pipe.transformers) > 1 or final_hat:
            info = {'name': 'union', 'inputs': outputs, 'type': 'transform'}
            info['outputs'] = [_get_name(context, info=info)]
            infos.append(info)
        return infos

    if isinstance(pipe, FeatureUnion):
        infos = []
        outputs = []
        for _, model in pipe.transformer_list:
            info = _pipeline_info(model, data, context)
            new_outputs = []
            for o in info[-1]['outputs']:
                add = _get_name(context, prefix=o, info=info)
                outputs.append(add)
                new_outputs.append(add)
            info[-1]['outputs'] = new_outputs
            infos.extend(info)
        if len(pipe.transformer_list) > 1:
            info = {'name': 'union', 'inputs': outputs, 'type': 'transform'}
            info['outputs'] = [_get_name(context, info=info)]
            infos.append(info)
        return infos

    if isinstance(pipe, TransformedTargetRegressor):
        raise NotImplementedError(  # pragma: no cover
            "Not yet implemented for TransformedTargetRegressor.")

    if isinstance(pipe, TransformerMixin):
        info = {'name': pipe.__class__.__name__, 'type': 'transform'}
        if len(data) == 1:
            info['outputs'] = data
            info['inputs'] = data
            info = [info]
        else:
            info['inputs'] = [_get_name(context, info=info)]
            info['outputs'] = [_get_name(context, info=info)]
            info = [{'name': 'union', 'outputs': info['inputs'],
                     'inputs': data, 'type': 'transform'}, info]
        return info

    if isinstance(pipe, ClassifierMixin):
        info = {'name': pipe.__class__.__name__, 'type': 'classifier'}
        exp = ['PredictedLabel', 'Probabilities']
        if len(data) == 1:
            info['outputs'] = exp
            info['inputs'] = data
            info = [info]
        else:
            info['outputs'] = exp
            info['inputs'] = [_get_name(context, info=info)]
            info = [{'name': 'union', 'outputs': info['inputs'], 'inputs': data,
                     'type': 'transform'}, info]
        return info

    if isinstance(pipe, RegressorMixin):
        info = {'name': pipe.__class__.__name__, 'type': 'regressor'}
        exp = ['Prediction']
        if len(data) == 1:
            info['outputs'] = exp
            info['inputs'] = data
            info = [info]
        else:
            info['outputs'] = exp
            info['inputs'] = [_get_name(context, info=info)]
            info = [{'name': 'union', 'outputs': info['inputs'], 'inputs': data,
                     'type': 'transform'}, info]
        return info

    if isinstance(pipe, str):
        if pipe == "passthrough":
            info = {'name': 'Identity', 'type': 'transform'}
            info['inputs'] = [_get_name_simple(n, former_data) for n in data]
            if isinstance(data, (OrderedDict, dict)) and len(data) > 1:
                info['outputs'] = [
                    _get_name(context, data=k, info=info)
                    for k in data]
            else:
                info['outputs'] = _get_name(context, data=data, info=info)
            info = [info]
        else:
            raise NotImplementedError(  # pragma: no cover
                f"Not yet implemented for keyword '{type(pipe)}'.")
        return info

    raise NotImplementedError(  # pragma: no cover
        f"Not yet implemented for {type(pipe)}.")

def enumerate_pipeline_models(pipe, coor=None, vs=None):
    """
    Enumerates all the models within a pipeline.
    @param      pipe        *scikit-learn* pipeline
    @param      coor        current coordinate
    @param      vs          subset of variables for the model, None for all
    @return                 iterator on models ``tuple(coordinate, model)``
    See notebook :ref:`visualizepipelinerst`.
    """
    if coor is None:
        coor = (0,)
    if pipe == "passthrough":
        class PassThrough:
            "dummy class to help display"
            pass
        yield coor, PassThrough(), vs
    else:
        yield coor, pipe, vs
        if hasattr(pipe, 'transformer_and_mapper_list') and len(pipe.transformer_and_mapper_list):
            # azureml DataTransformer
            raise NotImplementedError(  # pragma: no cover
                "Unable to handle this specific case.")
        elif hasattr(pipe, 'mapper') and pipe.mapper:
            # azureml DataTransformer
            for couple in enumerate_pipeline_models(  # pragma: no cover
                    pipe.mapper, coor + (0,)):  # pragma: no cover
                yield couple  # pragma: no cover
        elif hasattr(pipe, 'built_features'):  # pragma: no cover
            # sklearn_pandas.dataframe_mapper.DataFrameMapper
            for i, (columns, transformers, _) in enumerate(pipe.built_features):
                if isinstance(columns, str):
                    columns = (columns,)
                if transformers is None:
                    yield (coor + (i,)), None, columns
                else:
                    for couple in enumerate_pipeline_models(transformers, coor + (i,), columns):
                        yield couple
        elif isinstance(pipe, Pipeline):
            for i, (_, model) in enumerate(pipe.steps):
                for couple in enumerate_pipeline_models(model, coor + (i,)):
                    yield couple
        elif isinstance(pipe, ColumnTransformer):
            for i, (_, fitted_transformer, column) in enumerate(pipe.transformers):
                for couple in enumerate_pipeline_models(
                        fitted_transformer, coor + (i,), column):
                    yield couple
        elif isinstance(pipe, FeatureUnion):
            for i, (_, model) in enumerate(pipe.transformer_list):
                for couple in enumerate_pipeline_models(model, coor + (i,)):
                    yield couple
        elif isinstance(pipe, TransformedTargetRegressor):
            raise NotImplementedError(  # pragma: no cover
                "Not yet implemented for TransformedTargetRegressor.")
        elif isinstance(pipe, (TransformerMixin, ClassifierMixin, RegressorMixin)):
            pass
        elif isinstance(pipe, BaseEstimator):  # pragma: no cover
            pass
        else:
            raise TypeError(  # pragma: no cover
                f"pipe is not a scikit-learn object: {type(pipe)}\n{pipe}")

def pipeline2dot(pipe, data, **params):
    """
    Exports a *scikit-learn* pipeline to
    :epkg:`DOT` language. See :ref:`visualizepipelinerst`
    for an example.
    @param      pipe        *scikit-learn* pipeline
    @param      data        training data as a dataframe or a numpy array,
                            or just a list with the variable names
    @param      params      additional params to draw the graph
    @return                 string
    Default options for the graph are:
    ::
        options = {
            'orientation': 'portrait',
            'ranksep': '0.25',
            'nodesep': '0.05',
            'width': '0.5',
            'height': '0.1',
        }
    """
    raw_data = data
    data = OrderedDict()
    if isinstance(raw_data, pandas.DataFrame):
        for k, c in enumerate(raw_data.columns):
            data[c] = 'sch0:f%d' % k
    elif isinstance(raw_data, numpy.ndarray):
        if len(raw_data.shape) != 2:
            raise NotImplementedError(  # pragma: no cover
                f"Unexpected training data dimension {raw_data.shape}.")
        for i in range(raw_data.shape[1]):
            data['X%d' % i] = 'sch0:f%d' % i
    elif not isinstance(raw_data, list):
        raise TypeError(  # pragma: no cover
            f"Unexpected data type: {type(raw_data)}.")

    options = {
        'orientation': 'portrait',
        'ranksep': '0.25',
        'nodesep': '0.05',
        'width': '0.5',
        'height': '0.1',
    }
    options.update(params)

    exp = ["digraph{"]
    for opt in ['orientation', 'pad', 'nodesep', 'ranksep']:
        if opt in options:
            exp.append(f"  {opt}={options[opt]};")
    fontsize = 8
    info = [dict(schema_after=data)]
    names = OrderedDict()
    for d in data:
        names[d] = info
    info.extend(_pipeline_info(pipe, data, context=dict(n=0, names=names)))
    columns = OrderedDict()

    for i, line in enumerate(info):
        if i == 0:
            schema = line['schema_after']
            labs = []
            for c, col in enumerate(schema):
                columns[col] = f'sch0:f{c}'
                labs.append(f"<f{c}> {col}")
            node = '  sch0[label="{0}",shape=record,fontsize={1}];'.format(
                "|".join(labs), params.get('fontsize', fontsize))
            exp.append(node)
        else:
            exp.append('')
            if line['type'] == 'transform':
                node = '  node{0}[label="{1}",shape=box,style="filled' \
                    ',rounded",color=cyan,fontsize={2}];'.format(
                        i, line['name'],
                        int(params.get('fontsize', fontsize) * 1.5))
            else:
                node = '  node{0}[label="{1}",shape=box,style="filled,' \
                    'rounded",color=yellow,fontsize={2}];'.format(
                        i, line['name'],
                        int(params.get('fontsize', fontsize) * 1.5))
            exp.append(node)

            for inp in line['inputs']:
                if isinstance(inp, int):
                    raise IndexError(  # pragma: no cover
                        "Unable to guess columns {} in\n{}\n---\n{}".format(
                            inp, pprint.pformat(columns), '\n'.join(exp)))
                else:
                    nc = columns.get(inp, inp)
                edge = f'  {nc} -> node{i};'
                exp.append(edge)

            labs = []
            for c, out in enumerate(line['outputs']):
                columns[out] = f'sch{i}:f{c}'
                labs.append(f"<f{c}> {out}")
            node = '  sch{0}[label="{1}",shape=record,fontsize={2}];'.format(
                i, "|".join(labs), params.get('fontsize', fontsize))
            exp.append(node)

            for out in line['outputs']:
                nc = columns[out]
                edge = f'  node{i} -> {nc};'
                if edge not in exp:
                    exp.append(edge)

    exp.append('}')
    return "\n".join(exp)


def pipeline2str(pipe, indent=3):
    """
    Exports a *scikit-learn* pipeline to text.
    @param      pipe        *scikit-learn* pipeline
    @return                 str
    .. runpython::
        :showcode:
        from sklearn.linear_model import LogisticRegression
        from sklearn.impute import SimpleImputer
        from sklearn.preprocessing import OneHotEncoder
        from sklearn.preprocessing import StandardScaler, MinMaxScaler
        from sklearn.compose import ColumnTransformer
        from sklearn.pipeline import Pipeline
        from mlinsights.plotting import pipeline2str
        numeric_features = ['age', 'fare']
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())])
        categorical_features = ['embarked', 'sex', 'pclass']
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))])
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features),
            ])
        clf = Pipeline(steps=[('preprocessor', preprocessor),
                              ('classifier', LogisticRegression(solver='lbfgs'))])
        text = pipeline2str(clf)
        print(text)
    """
    rows = []
    for coor, model, vs in enumerate_pipeline_models(pipe):
        spaces = " " * indent * (len(coor) - 1)
        if vs is None:
            msg = f"{spaces}{model.__class__.__name__}"
        else:
            v = ','.join(map(str, vs))
            msg = f"{spaces}{model.__class__.__name__}({v})"
        rows.append(msg)
    return "\n".join(rows)