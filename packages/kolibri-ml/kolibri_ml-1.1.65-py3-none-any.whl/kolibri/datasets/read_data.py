import tabulate
#from kolibri.data.text.resources import resources
from pathlib import Path
from kolibri.data import find
def get_data(
    dataset="index",
    profile_data=False
):

    """
    This function loads sample datasets from git repository. List of available
    datasets can be checked using ``get_data('index')``.
    Example
    -------




    dataset: str, default = 'index'
        Index value of dataset.


    profile_data: bool, default = False
        When set to true, an interactive EDA report is displayed.

    Returns:
        pandas.DataFrame


    Warnings
    --------
    - ``get_data`` needs an internet connection.

    """

    import pandas as pd
    import os.path
    try:
        from IPython.display import display
    except:
        pass

    from kolibri.data.downloader import download
    filename=None
    try:
        filename = find('datasets/' + dataset + '.csv')
    except:
        try:
            filename=find('datasets/' + dataset)
        except:
            if download is not None:
                download('datasets/'+dataset)
            else:
                pass

    data =None
    if filename is not None:
        if os.path.isfile(filename):
            try:
                data = pd.read_csv(filename, parse_dates=True)
            except UnicodeDecodeError:
                print('Unicode Error')
                data = pd.read_csv(filename, encoding='latin-1', parse_dates=True)

    if dataset == "index" and data is None:
        display(data)

    if profile_data:
        import pandas_profiling

        pf = pandas_profiling.ProfileReport(data)
        print(tabulate.tabulate(pf))

    return data



if __name__=="__main__":
    d=get_data('iris')
    print(d)