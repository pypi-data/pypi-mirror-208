"""
plot a pretty confusion matrix with seaborn
references:
  https://www.mathworks.com/help/nnet/ref/plotconfusion.html
  https://stackoverflow.com/questions/28200786/how-to-plot-scikit-learn-classification-report
  https://stackoverflow.com/questions/5821125/how-to-plot-confusion-matrix-with-string-axis-rather-than-integer-in-python
  https://www.programcreek.com/python/example/96197/seaborn.heatmap
  https://stackoverflow.com/questions/19233771/sklearn-plot-confusion-matrix-with-labels/31720054
  http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html#sphx-glr-auto-examples-model-selection-plot-confusion-matrix-py
"""

#imports
from pandas import DataFrame
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.collections import QuadMesh
import seaborn as sn


def _get_new_fig(fn, figsize=[9, 9]):
    """ Init graphics """
    fig1 = plt.figure(fn, figsize)
    ax1 = fig1.gca()   #Get Current Axis
    ax1.cla() # clear existing plot
    return fig1, ax1


def _configcell_text_and_colors(array_df, lin, col, oText, facecolors, posi, fz, show_null_values=0):
    """
      config cell text and colors
      and return text elements to add and to dell
    """
    text_add = []; text_del = []
    cell_val = array_df[lin][col]
    tot_all = array_df[-1][-2]
    per = (float(cell_val) / tot_all) * 100
    curr_column = array_df[:,col]
    ccl = len(curr_column)

    # last line and/or last column
    if (col >= (ccl - 1)) or (lin == (ccl - 1)):

        if(col == ccl):
            per_ok=cell_val*100
            per_err=0
        # tots and percents
        elif(cell_val != 0):
            if(col == ccl - 1) and (lin == ccl - 1):
                tot_rig = 0
                for i in range(array_df.shape[0] - 1):
                    tot_rig += array_df[i][i]
                per_ok = (float(tot_rig) / cell_val) * 100
            elif(col == ccl - 1):
                tot_rig = array_df[lin][lin]
                per_ok = (float(tot_rig) / cell_val) * 100
            elif(lin == ccl - 1):
                tot_rig = array_df[col][col]
                per_ok = (float(tot_rig) / cell_val) * 100
            per_err = 100 - per_ok
        else:
            per_ok = per_err = 0

        per_ok_s = ['%.2f%%'%(per_ok), '100%'] [per_ok == 100]

        # text to DEL
        text_del.append(oText)

        # text to ADD
        font_prop = fm.FontProperties(weight='bold', size=fz)
        text_kwargs = dict(color='w', ha="center", va="center", gid='sum', fontproperties=font_prop)
        if col == lin:
            lis_txt = ['%d'%(cell_val), per_ok_s, 'Accuracy']
        elif col == ccl:
            lis_txt = ['', per_ok_s, '']
        else:
           lis_txt = ['%d'%(cell_val), per_ok_s, '%.2f%%'%(per_err)]
        lis_kwa = [text_kwargs]
        dic = text_kwargs.copy(); dic['color'] = 'lime'; lis_kwa.append(dic)
        dic = text_kwargs.copy(); dic['color'] = 'salmon'; lis_kwa.append(dic)
        lis_pos = [(oText._x, oText._y - 0.3), (oText._x, oText._y), (oText._x, oText._y + 0.3)]
        for i in range(len(lis_txt)):
            newText = dict(x=lis_pos[i][0], y=lis_pos[i][1], text=lis_txt[i], kw=lis_kwa[i])
            #print 'lin: %s, col: %s, newText: %s' %(lin, col, newText)
            text_add.append(newText)
        #print '\n'

        # set background color for sum cells (last line and last column)
        carr = [0.27, 0.30, 0.27, 1.0]
        if(col >= ccl - 1) and (lin == ccl - 1):
            carr = [0.17, 0.20, 0.17, 1.0]
        facecolors[posi] = carr

    else:
        if(per > 0):
            txt = '%d\n%.2f%%' %(cell_val, per)
        else:
            if(show_null_values == 0):
                txt = ''
            elif(show_null_values == 1):
                txt = '0'
            else:
                txt = '0\n0.0%'
        oText.set_text(txt)

        # main diagonal
        if(col == lin):
            # set color of the textin the diagonal to white
            oText.set_color('w')
            # set background color in the diagonal to blue
            facecolors[posi] = [0.35, 0.8, 0.55, 1.0]
        else:
            oText.set_color('r')

    return text_add, text_del


def _insert_totals(df_cm, pred_val_axis):
    """ insert total column and line (the last ones) """
    if(pred_val_axis in ('col', 'x')):
        xlbl = 'Recall'
        ylbl = 'Precision'
    else:
        xlbl = 'Precision'
        ylbl = 'Recall'

    sum_col = []
    for c in df_cm.columns:
        sum_col.append(df_cm[c].sum())
    sum_lin = []
    for item_line in df_cm.iterrows():
        sum_lin.append(item_line[1].sum())
    p = []
    r = []
    f1 = []
    for i in range(0, len(df_cm.index)):
        _p = df_cm.iat[i, i]  /sum_col[i]
        _q = df_cm.iat[i, i] / sum_lin[i]
        _f1 = 2 * (_p * _q) / (_p + _q)
        f1.append(0 if _f1 != _f1 else _f1)

    df_cm[xlbl] = sum_lin
    df_cm['F1-Score'] = f1

    sum_col.append(np.sum(sum_lin))
    sum_col.append(np.average(f1))
    df_cm.loc[ylbl] = sum_col


def plot_confusion_matrix_from_matrix(df_cm, annot=True, cmap="OrRd", fz=11,
                                      lw=0.5, cbar=False, figsize=[7, 7], show_null_values=0, pred_val_axis='y'):
    """
      print conf matrix with default layout (like matlab)
      params:
        df_cm          dataframe (pandas) without totals
        annot          print text in each cell
        cmap           Oranges,Oranges_r,YlGnBu,Blues,RdBu, ... see:
        fz             fontsize
        lw             linewidth
        pred_val_axis  where to show the prediction values (x or y axis)
                        'col' or 'x': show predicted values in columns (x axis) instead lines
                        'lin' or 'y': show predicted values in lines   (y axis)
    """
    if(pred_val_axis in ('col', 'x')):
        xlbl = 'Predicted'
        ylbl = 'Actual'
    else:
        xlbl = 'Actual'
        ylbl = 'Predicted'
        df_cm = df_cm.T

    # create "Total" column
    _insert_totals(df_cm, pred_val_axis)

    # this is for print allways in the same window
    fig, ax1 = _get_new_fig('Conf matrix default', figsize)
    fig.patch.set_facecolor('white')

    # thanks for seaborn
    ax = sn.heatmap(df_cm, annot=annot, annot_kws={"size": fz}, linewidths=lw, ax=ax1,
                    cbar=cbar, cmap=cmap, linecolor='w', fmt='.2f')

    # set ticklabels rotation
    ax.set_xticklabels(ax.get_xticklabels(), rotation=-30, fontsize=10, ha='left')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=25, fontsize=10)

    # axis settings: avoiding cutting off edges
    bottom, top = ax.get_ylim()
    ax.set_ylim(bottom + 0.5, top - 0.5)

    # turn off all the ticks
    for t in ax.xaxis.get_major_ticks():
        t.tick1line.set_visible(False)
        t.tick2line.set_visible(False)
    for t in ax.yaxis.get_major_ticks():
        t.tick1line.set_visible(False)
        t.tick1line.set_visible(False)

    # face colors list
    quadmesh = ax.findobj(QuadMesh)[0]
    facecolors = quadmesh.get_facecolors()

    # iter in text elements
    array_df = np.array( df_cm.to_records(index=False).tolist() )
    text_add = []; text_del = []
    posi = -1 #from left to right, bottom to top.
    for t in ax.collections[0].axes.texts: #ax.texts:
        pos = np.array(t.get_position()) - [0.5, 0.5]
        lin = int(pos[1]); col = int(pos[0])
        posi += 1
        #print ('>>> pos: %s, posi: %s, val: %s, txt: %s' %(pos, posi, array_df[lin][col], t.get_text()))

        # set text
        txt_res = _configcell_text_and_colors(array_df, lin, col, t, facecolors, posi, fz, show_null_values)

        text_add.extend(txt_res[0])
        text_del.extend(txt_res[1])

    # remove the old ones
    for item in text_del:
        item.remove()
    # append the new ones
    for item in text_add:
        ax.text(item['x'], item['y'], item['text'], **item['kw'])

    # titles and legends
    ax.set_title('Confusion matrix')
    ax.set_xlabel(xlbl)
    ax.set_ylabel(ylbl)
    plt.tight_layout()  #set layout slim
    fig = plt.gcf()
    return plt


def plot_confusion_matrix_from_data(y_true, y_pred, columns=None, annot=True, cmap="OrRd",
      fz=11, lw=0.5, cbar=False, figsize=[7, 7], show_null_values=0, pred_val_axis='lin'):
    """
        plot confusion matrix function with y_true (actual values) and y_pred (predictions),
        whitout a confusion matrix yet
    """
    from sklearn.metrics import confusion_matrix

    #data
    if columns is None:
        #labels axis integer:
        ##columns = range(1, len(np.unique(y_true))+1)
        #labels axis string:
        from string import ascii_uppercase
        columns = np.unique(y_true)

    confm = confusion_matrix(y_true, y_pred)
    df_cm = DataFrame(confm, index=columns, columns=columns)
    return plot_confusion_matrix_from_matrix(
        df_cm, annot=annot, cmap=cmap, fz=fz, cbar=cbar, figsize=figsize,
        show_null_values=show_null_values, pred_val_axis=pred_val_axis
    )


def test_from_data():
        """ test function y_true (actual values) and y_pred (predictions) """
        #data
        y_true = np.array([1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5])
        y_pred = np.array([1,2,4,3,5, 1,2,4,3,5, 1,2,3,4,4, 1,4,3,4,5, 1,2,4,4,5, 1,2,4,4,5, 1,2,4,4,5, 1,2,4,4,5, 1,2,3,3,5, 1,2,3,3,5, 1,2,3,4,4, 1,2,3,4,1, 1,2,3,4,1, 1,2,3,4,1, 1,2,4,4,5, 1,2,4,4,5, 1,2,4,4,5, 1,2,4,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5])
        """
        Examples to validate output (confusion matrix plot)
            actual: 5 and prediction 1   >>  3
            actual: 2 and prediction 4   >>  1
            actual: 3 and prediction 4   >>  10
        """
        columns = None
        annot = True
        cmap = 'OrRd'
        lw = 0.5
        cbar = False
        show_null_values = 1
        pred_val_axis = 'y'
        fz = 12
        figsize = [7, 7]
        if(len(np.unique(y_true)) > 10):
            fz = 9; figsize = [14, 14]
        plot_confusion_matrix_from_data(y_true, y_pred, columns,
        annot, cmap, fz, lw, cbar, figsize, show_null_values, pred_val_axis)

def test_from_matrix():
        #test function with confusion matrix done
        array = np.array(
            [[13,  0,  1,  0,  2,  0],
             [ 0, 50,  2,  0, 10,  0],
             [ 0, 13, 16,  0,  0,  3],
             [ 0,  0,  0, 13,  1,  0],
             [ 0, 40,  0,  1, 15,  0],
             [ 0,  0,  0,  0,  0, 20]]
        )
        #get pandas dataframe
        df_cm = DataFrame(array, index=range(1, 7), columns=range(1, 7))
        #colormap: see this and choose your more dear
        cmap = 'PuRd'
        show_null_values = 0
        figsize = [7, 7]
        if(len(array) > 10):
            fz = 9; figsize = [14, 14]
        plot_confusion_matrix_from_matrix(
            df_cm, cmap=cmap, figsize=figsize, show_null_values=show_null_values
        )

if __name__=="__main__":
    test_from_data()