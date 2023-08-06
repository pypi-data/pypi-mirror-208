import matplotlib.pyplot as plt
import pandas
from numpy import newaxis, arange, argmin, unique, concatenate, zeros_like, argmax, linspace
from scipy import interp
from kolibri.utils.cm import plot_confusion_matrix_from_matrix
from sklearn.preprocessing import label_binarize
from sklearn.metrics import confusion_matrix, precision_recall_curve, auc, roc_curve, average_precision_score, classification_report
import itertools
from itertools import product, cycle
import random
from statistics import mean
import seaborn as sns
from kolibri.logger import get_logger
from sklearn.manifold import TSNE
from dtreeviz.trees import *
import seaborn as sns

logger=get_logger(__name__)
import pandas as pd
import numpy as np



class ClassificationPlots:
    """
    Initialize class.
    Parameters
    ----------
    y_true : array, list, shape = [n_sample]
        True binary labels.
    y_pred : array, list, shape = [n_sample]
        Target scores, can either be probability estimates of the positive
        class, confidence values, or non-thresholded measure of decisions
        (as returned by "decision_function" on some classifiers).
    labels : array, list, shape = [n_class]
        String or int of to define targeted classes.
    threshold : float [0-1], default=0.5,
        Classification threshold (or decision threshold).
        More information about threshold :
        - https://developers.google.com/machine-learning/crash-course/classification/thresholding
        - https://en.wikipedia.org/wiki/Threshold_model
    seaborn_style : string, default='darkgrid'
        Set the style of seaborn library, preset available with
        seaborn : darkgrid, whitegrid, dark, white, and ticks.
        See https://seaborn.pydata.org/tutorial/aesthetics.html#seaborn-figure-styles for more info.
    matplotlib_style : string, default=None
        Set the style of matplotlib. Find all preset here : https://matplotlib.org/3.1.0/gallery/style_sheets/style_sheets_reference.html
        Or with the following code :
    .. code:: python
        import matplotlib.style as style
        style.available
    """

    ### Parameters definition ###
    __param_precision_recall_curve = {'threshold': None,
                                      'plot_threshold': True,
                                      'beta': 1,
                                      'linewidth': 2,
                                      'fscore_iso': [0.2, 0.4, 0.6, 0.8],
                                      'iso_alpha': 0.7,
                                      'y_text_margin': 0.03,
                                      'x_text_margin': 0.2,
                                      'c_pr_curve': 'black',
                                      'c_mean_prec': 'red',
                                      'c_thresh': 'black',
                                      'c_f1_iso': 'grey',
                                      'c_thresh_point': 'red',
                                      'ls_pr_curve': '-',
                                      'ls_mean_prec': '--',
                                      'ls_thresh': ':',
                                      'ls_fscore_iso': ':',
                                      'marker_pr_curve': None}

    __param_confusion_matrix = {'threshold': None,
                                'normalize': False,
                                'title': 'Confusion matrix',
                                'cmap': plt.cm.Reds,
                                'colorbar': True,
                                'label_rotation': 45}

    __param_roc_curve = {'threshold': None,
                         'plot_threshold': True,
                         'linewidth': 2,
                         'y_text_margin': 0.05,
                         'x_text_margin': 0.2,
                         'c_roc_curve': 'black',
                         'c_random_guess': 'red',
                         'c_thresh_lines': 'black',
                         'ls_roc_curve': '-',
                         'ls_thresh_lines': ':',
                         'ls_random_guess': '--',
                         'title': 'Receiver Operating Characteristic',
                         'loc_legend': 'lower right'}

    __param_class_distribution = {'threshold': None,
                                  'display_prediction': True,
                                  'alpha': .5,
                                  'jitter': .3,
                                  'pal_colors': None,
                                  'display_violin': True,
                                  'c_violin': 'white',
                                  'strip_marker_size': 4,
                                  'strip_lw_edge': None,
                                  'strip_c_edge': None,
                                  'ls_thresh_line': ':',
                                  'c_thresh_line': 'red',
                                  'lw_thresh_line': 2,
                                  'title': None}

    __param_threshold = {'threshold': None,
                         'beta': 1,
                         'title': None,
                         'annotation': True,
                         'bbox_dict': None,
                         'bbox': True,
                         'arrow_dict': None,
                         'arrow': True,
                         'plot_fscore': True,
                         'plot_recall': True,
                         'plot_prec': True,
                         'plot_fscore_max': True,
                         'c_recall_line': 'green',
                         'lw_recall_line': 2,
                         'ls_recall_line': '-',
                         'label_recall': 'Recall',
                         'marker_recall': '',
                         'c_prec_line ': 'blue',
                         'lw_prec_line': 2,
                         'ls_prec_line': '-',
                         'label_prec': 'Precision',
                         'marker_prec': '',
                         'c_fscr_line ': 'red',
                         'lw_fscr_line': 2,
                         'ls_fscr_line': '-',
                         'label_fscr': None,
                         'marker_fscr': '',
                         'marker_fscore_max': 'o',
                         'c_fscore_max': 'red',
                         'markersize_fscore_max': 5,
                         'plot_threshold': True,
                         'c_thresh_line': 'black',
                         'lw_thresh_line': 2,
                         'ls_thresh_line': '--',
                         'plot_best_threshold': True,
                         'c_bestthresh_line': 'black',
                         'lw_bestthresh_line': 1,
                         'ls_bestthresh_line': ':'}

    def __init__(self, y_true, y_pred, labels_dict, X=None, y=None, threshold=0.5, target_name=None, features_names=[], seaborn_style='darkgrid', classifier=None, max_depth=4):
        self.y_true = y_true

        if y_pred.shape[1]==2:
            self.y_pred = y_pred[:,1]
        else:
            self.y_pred=y_pred
        if labels_dict is None:
            self.labels_names=list(set(y_true))
        else:
            self.labels_names = labels_dict
        self.n_classes = len(self.labels_names)
        self._threshold_ = threshold
        sns.set_style(seaborn_style)

        if classifier is None:
            self.classifier = tree.DecisionTreeClassifier(max_depth=max_depth)
        else:
            self.classifier=classifier
        self.target_name=target_name
        self.X=X
        self.y=y
        self.labels_names=labels_dict
        self.n_classes=len(self.labels_names)
        self.features_names=features_names

    def __to_hex(self, scale):
        ''' converts scale of rgb or hsl strings to list of tuples with rgb integer values. ie,
            [ "rgb(255, 255, 255)", "rgb(255, 255, 255)", "rgb(255, 255, 255)" ] -->
            [ (255, 255, 255), (255, 255, 255), (255, 255, 255) ] '''
        numeric_scale = []
        for s in scale:
            s = s[s.find("(") + 1:s.find(")")].replace(' ', '').split(',')
            numeric_scale.append((float(s[0]), float(s[1]), float(s[2])))

        return ['#%02x%02x%02x' % tuple(map(int, s)) for s in numeric_scale]

    def _get_function_parameters(self, function, as_df=False):
        """
        Function to get all available parameters for a given function.
        Parameters
        ----------
        function : func
            Function parameter's wanted.
        as_df : boolean, default=False
            Set to True to return a dataframe with parameters instead of dictionnary.
        Returns
        -------
        param_dict : dict
            Dictionnary containing parameters for the given function and their default value.
        """

        if function.__name__ is "plot_precision_recall_curve":
            param_dict = self.__param_precision_recall_curve
        elif function.__name__ is "plot_confusion_matrix":
            param_dict = self.__param_confusion_matrix
        elif function.__name__ is "plot_roc_curve":
            param_dict = self.__param_roc_curve
        elif function.__name__ is "plot_class_distribution":
            param_dict = self.__param_class_distribution
        elif function.__name__ is "plot_threshold":
            param_dict = self.__param_threshold
        else:
            print("Wrong function given, following functions are available : ")
            for func in filter(lambda x: callable(x), ClassificationPlots.__dict__.values()):
                print(func.__name__)
            return [func() for func in filter(lambda x: callable(x), ClassificationPlots.__dict__.values())]

        if as_df:
            return pd.DataFrame.from_dict(param_dict, orient='index')
        else:
            return param_dict

    def confusion_matrix(self, threshold=None, normalize=False, title='Confusion matrix', cmap=plt.cm.Reds,
                              colorbar=True, label_rotation=45):
        """
        Plots the confusion matrix.
        Parameters
        ----------
        threshold : float, default=0.5
            Threshold to determnine the rate between positive and negative values of the classification.
        normalize : bool, default=False
            Set to True to normalize matrix and make matrix coefficient between 0 and 1.
        title : string, default="Confusion matrix",
            Set title of the plot.
        cmap : colormap, default=plt.cm.Reds
            Colormap of the matrix. See https://matplotlib.org/examples/color/colormaps_reference.html to find all
            available colormap.
        colorbar : bool, default=True
            Display color bar beside matrix.
        label_rotation : int, default=45
            Degree of rotation for x_axis labels.
        Returns
        -------
        cm : array, shape=[n_classes, n_classes]
            Return confusion_matrix computed by sklearn.metrics.confusion_matrix
        """
        if threshold is None:
            t = self._threshold_
        else:
            t = threshold

        # Convert prediction probility into class
        #
        if len(self.y_pred.shape)==1:
            y_pred_class = [1 if y_i > t else 0 for y_i in self.y_pred]
        else:
            y_pred_class = [l for l in argmax(self.y_pred, axis=1)]
        # Define the confusion matrix
        cm = pd.DataFrame(confusion_matrix(self.y_true, y_pred_class, labels=list(self.labels_names.keys())))
        cm.columns=list(self.labels_names.values())
        cm.index=list(self.labels_names.values())

        plt.clf()
        cmap = 'PuRd'
        show_null_values = True
        figsize = [7, 7]
        if(len(cm.columns) > 10):
            fz = 9
            figsize = [14, 14]
        return plot_confusion_matrix_from_matrix(
            cm, cmap=cmap, figsize=figsize, show_null_values=show_null_values
        )

        # # Normalize matrix if choosen
        # if normalize:
        #     cm = cm.astype('float') / cm.sum(axis=1)[:, newaxis]
        #     title = title + ' normalized'
        #
        # # Compute plot
        # plt.imshow(cm, interpolation='nearest', cmap=cmap)
        # plt.title(title)
        # if colorbar:
        #     plt.colorbar()
        # tick_marks = arange(len(list(self.labels_names.values())))
        # plt.xticks(tick_marks, list(self.labels_names.values()), rotation=label_rotation)
        # plt.yticks(tick_marks, list(self.labels_names.values()))
        #
        # # Display text into matrix
        # fmt = '.2f' if normalize else 'd'
        # thresh = cm.max() / 2.
        # for i, j in product(range(cm.shape[0]), range(cm.shape[1])):
        #     plt.text(j, i, format(cm[i, j], fmt),
        #              horizontalalignment="center",
        #              color="white" if cm[i, j] > thresh else "black")
        #
        # plt.tight_layout()
        # plt.ylabel('True label')
        # plt.xlabel('Predicted label')

        # return fig


    def roc(self, threshold=None, plot_threshold=True, linewidth=2, y_text_margin=0.05, x_text_margin=0.2,
                       c_roc_curve='black', c_random_guess='red', c_thresh_lines='black', ls_roc_curve='-',
                       ls_thresh_lines=':', ls_random_guess='--', title='Receiver Operating Characteristic',
                       loc_legend='lower right'):
        plt.clf()
        if self.n_classes==2:
            return self._plot_roc_curve_binary(threshold, plot_threshold, linewidth, y_text_margin, x_text_margin,
                       c_roc_curve, c_random_guess, c_thresh_lines, ls_roc_curve,
                       ls_thresh_lines, ls_random_guess, title,
                       loc_legend)
        elif self.n_classes>2:
            return self._plot_roc_curve_multi_class(threshold, linewidth, plot_threshold)

        else:
            raise Exception("Number of distinct classes cannot be 1")

    def _plot_roc_curve_multi_class(self, threshold=None, linewidth=2, show_threshold=False):
        from sklearn.metrics import roc_curve, auc
        from sklearn.preprocessing import label_binarize

        if threshold is None:
            t = self._threshold_
        else:
            t = threshold


        # Binarize the output
        y = label_binarize(self.y_true, classes=list(self.labels_names.keys()))

        # Compute ROC curve and ROC area for each class
        fpr, tpr = dict(), dict()
        roc_auc = dict()
        idx_thresh, idy_thresh = dict(), dict()
        for i in range(self.n_classes):
            fpr[i], tpr[i], thresh = roc_curve(y[:, i], self.y_pred[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])

            # Compute the y & x axis to trace the threshold
            idx_thresh[i], idy_thresh[i] = fpr[i][argmin(abs(thresh - t))], tpr[i][argmin(abs(thresh - t))]

        # Compute micro-average ROC curve and ROC area
        fpr["micro"], tpr["micro"], thresh = roc_curve(y.ravel(), self.y_pred.ravel())
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
        idx_thresh["micro"] = fpr["micro"][argmin(abs(thresh - t))]
        idy_thresh["micro"] = tpr["micro"][argmin(abs(thresh - t))]

        # Aggregate all false positive rates
        all_fpr = unique(concatenate([fpr[i] for i in range(self.n_classes)]))

        # Then interpolate all ROC curves at this points
        mean_tpr = zeros_like(all_fpr)
        for i in range(self.n_classes):
            mean_tpr += interp(all_fpr, fpr[i], tpr[i])

        # Average it and compute AUC
        mean_tpr /= self.n_classes

        fpr["macro"] = all_fpr
        tpr["macro"] = mean_tpr
        roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])
        plt.gcf().set_size_inches(10, 10)
        # Plot all ROC curves
        plt.plot(fpr["micro"], tpr["micro"],
                 label='micro-average ROC curve (area = {0:0.2f})'
                       ''.format(roc_auc["micro"]),
                 color='deeppink', linestyle=':', linewidth=linewidth)

        plt.plot(fpr["macro"], tpr["macro"],
                 label='macro-average ROC curve (area = {0:0.2f})'
                       ''.format(roc_auc["macro"]),
                 color='navy', linestyle=':', linewidth=linewidth)

        random.seed(124)
        colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33']
        random.shuffle(colors)
        for i, color in zip(range(self.n_classes), cycle(colors)):
            plt.plot(fpr[i], tpr[i], color=color, lw=linewidth, alpha=.5,
                     label='ROC curve of class {0} (area = {1:0.2f})'
                           ''.format(list(self.labels_names.values())[i], roc_auc[i]))

        if show_threshold:
            plt.plot(idx_thresh.values(), idy_thresh.values(), 'ro')

        plt.plot([0, 1], [0, 1], 'k--', lw=linewidth)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver operating characteristic for multi-class (One-Vs-All')
        plt.legend(loc="lower right")

        return plt

    def _plot_roc_curve_binary(self, threshold=None, plot_threshold=True, linewidth=2, y_text_margin=0.05, x_text_margin=0.2,
                       c_roc_curve='black', c_random_guess='red', c_thresh_lines='black', ls_roc_curve='-',
                       ls_thresh_lines=':', ls_random_guess='--', title='Receiver Operating Characteristic',
                       loc_legend='lower right'):
        """
        Compute and plot the ROC (Receiver Operating Characteristics) curve but also AUC (Area Under The Curve).
        Note : for more information about ROC curve and AUC look at the reference given.
        Moreover, this implementation is restricted to binary classification only.
        See MultiClassClassification for multi-classes implementation.
        Parameters
        ----------
        threshold : float, default=0.5
        plot_threshold : boolean, default=True
            Plot or not ROC lines for the given threshold.
        linewidth : float, default=2
        y_text_margin : float, default=0.03
            Margin (y) of text threshold.
        x_text_margin : float, default=0.2
            Margin (x) of text threshold.
        c_roc_curve : string, default='black'
            Define the color of ROC curve.
        c_random_guess : string, default='red'
            Define the color of random guess line.
        c_thresh_lines : string, default='black'
            Define the color of threshold lines.
        ls_roc_curve : string, default='-'
            Define the linestyle of ROC curve.
        ls_thresh_lines : string, default=':'
            Define the linestyle of threshold lines.
        ls_random_guess : string, default='--'
            Define the linestyle of random guess line.
        title : string, default='Receiver Operating Characteristic'
            Set title of the figure.
        loc_legend : string, default='loc_legend'
            Localisation of legend. Available string are the following :
            ================    ================
            Location String	    Location Code
            ================    ================
            'best'	            0
            'upper right'	    1
            'upper left'	    2
            'lower left'	    3
            'lower right'	    4
            'right'         	5
            'center left'	    6
            'center right'	    7
            'lower center'	    8
            'upper center'	    9
            'center'	        10
            ================    ================
        Returns
        -------
        fpr : array, shape = [>2]
            Increasing false positive rates such that element i is the false
            positive rate of predictions with score >= thresholds[i].
        tpr : array, shape = [>2]
            Increasing true positive rates such that element i is the true
            positive rate of predictions with score >= thresholds[i].
        thresh : array, shape = [n_thresholds]
            Decreasing thresholds on the decision function used to compute
            fpr and tpr. `thresholds[0]` represents no instances being predicted
            and is arbitrarily set to `max(y_score) + 1`.
        auc : float
        References
        -------
        .. [1] `Understanding AUC - ROC Curve (article by Sarang Narkhede)
            <https://towardsdatascience.com/understanding-auc-roc-curve-68b2303cc9c5>`_
        .. [2] `Wikipedia entry for the Receiver operating characteristic
            <https://en.wikipedia.org/wiki/Receiver_operating_characteristic>`_
        .. [3] `sklearn documentation about roc_curve and auc functions
            <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html>`_
        """
        if threshold is None:
            t = self._threshold_
        else:
            t = threshold

        # Compute ROC Curve
        fpr, tpr, thresh = roc_curve(self.y_true, self.y_pred)
        # Compute AUC
        roc_auc = auc(fpr, tpr)

        # Compute the y & x axis to trace the threshold
        idx_thresh, idy_thresh = fpr[argmin(abs(thresh - t))], tpr[argmin(abs(thresh - t))]

        # Plot roc curve
        plt.plot(fpr, tpr, color=c_roc_curve,
                 lw=linewidth, label='ROC curve (area = %0.2f)' % roc_auc, linestyle=ls_roc_curve)

        # Plot reference line
        plt.plot([0, 1], [0, 1], color=c_random_guess, lw=linewidth, linestyle=ls_random_guess, label="Random guess")
        # Plot threshold
        if plot_threshold:
            # Plot vertical and horizontal line
            plt.axhline(y=idy_thresh, color=c_thresh_lines, linestyle=ls_thresh_lines, lw=linewidth)
            plt.axvline(x=idx_thresh, color=c_thresh_lines, linestyle=ls_thresh_lines, lw=linewidth)

            # Plot text threshold
            if idx_thresh > 0.5 and idy_thresh > 0.5:
                plt.text(x=idx_thresh - x_text_margin, y=idy_thresh - y_text_margin,
                         s='Threshold : {:.2f}'.format(t))
            elif idx_thresh <= 0.5 and idy_thresh <= 0.5:
                plt.text(x=idx_thresh + x_text_margin, y=idy_thresh + y_text_margin,
                         s='Threshold : {:.2f}'.format(t))
            elif idx_thresh <= 0.5 < idy_thresh:
                plt.text(x=idx_thresh + x_text_margin, y=idy_thresh - y_text_margin,
                         s='Threshold : {:.2f}'.format(t))
            elif idx_thresh > 0.5 >= idy_thresh:
                plt.text(x=idx_thresh - x_text_margin, y=idy_thresh + y_text_margin,
                         s='Threshold : {:.2f}'.format(t))

            # Plot redpoint of threshold on the ROC curve
            plt.plot(idx_thresh, idy_thresh, 'ro')

        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(title)
        plt.legend(loc=loc_legend)


        return plt

    def pr(self, threshold=None, plot_threshold=True, beta=1, linewidth=2,
                                    fscore_iso=[0.2, 0.4, 0.6, 0.8], iso_alpha=0.7, y_text_margin=0.03,
                                    x_text_margin=0.2, c_pr_curve='black', c_mean_prec='red', c_thresh_lines='black',
                                    c_f1_iso='grey', c_thresh_point='red', ls_pr_curve='-', ls_mean_prec='--',
                                    ls_thresh=':', ls_fscore_iso=':', marker_pr_curve=None,
                                    title='Precision and Recall Curve'):
        """
        Compute and plot the precision-recall curve.
        Note : this implementation is restricted to binary classification only.
        See MultiClassClassification for multi-classes implementation.
        F1-iso are curve where a given f1-score is constant.
        We also consider the use of F_beta-score, change the parameter beta to use an other f-score.
        "Two other commonly used F measures are the F_2 measure, which weighs recall higher than
        precision (by placing more emphasis on false negatives), and the F_0.5 measure, which weighs
        recall lower than precision (by attenuating the influence of false negatives). (Wiki)"
        Parameters
        ----------
        threshold : float, default=0.5
            Threshold to determnine the rate between positive and negative values of the classification.

        plot_threshold : boolean, default=True
            Plot or not precision and recall lines for the given threshold.

        beta : float, default=1,
            Set beta to another float to use a different f_beta score. See definition of f_beta-score
            for more information : https://en.wikipedia.org/wiki/F1_score

        linewidth : float, default=2

        fscore_iso : array, list, default=[0.2, 0.4, 0.6, 0.8]
            List of float f1-score. Set to None or empty list to remove plotting of iso.

        iso_alpha : float, default=0.7
            Transparency of iso-f1.

        y_text_margin : float, default=0.03
            Margin (y) of text threshold.
        x_text_margin : float, default=0.2
            Margin (x) of text threshold.

        c_pr_curve : string, default='black'
            Define the color of precision-recall curve.

        c_mean_prec : string, default='red'
            Define the color of mean precision line.

        c_thresh : string, default='black'
            Define the color of threshold lines.

        c_f1_iso : string, default='grey'
            Define the color of iso-f1 curve.

        c_thresh_point : string, default='red'
            Define the color of threshold point.

        ls_pr_curve : string, default='-'
            Define the linestyle of precision-recall curve.

        ls_mean_prec : string, default='--'
            Define the linestyle of mean precision line.

        ls_thresh : string, default=':'
            Define the linestyle of threshold lines.

        ls_fscore_iso : string, default=':'
            Define the linestyle of iso-f1 curve.

        marker_pr_curve : string, default=None
            Define the marker of precision-recall curve.

        title : string, default="Precision and Recall Curve"
            Set title of the figure.
        Returns
        -------
        prec : array, shape = [n_thresholds + 1]
            Precision values such that element i is the precision of
            predictions with score >= thresholds[i] and the last element is 1.

        recall : array, shape = [n_thresholds + 1]
            Decreasing recall values such that element i is the recall of
            predictions with score >= thresholds[i] and the last element is 0.

        thresh : array, shape = [n_thresholds <= len(np.unique(y_pred))]
            Increasing thresholds on the decision function used to compute
            precision and recall.
        """

        # Set f1-iso and threshold parameters
        if fscore_iso is None:
            fscore_iso = []
        if threshold is None:
            t = self._threshold_
        else:
            t = threshold

        # List for legends
        lines, labels = [], []
        plt.clf()
        if self.n_classes > 2:
            y = label_binarize(self.y_true, classes=list(self.labels_names.keys()))
            # Compute precision and recall
            prec, recall, thresh = precision_recall_curve(y.ravel(), self.y_pred.ravel())
            # Compute area
            pr_auc = average_precision_score(y.ravel(), self.y_pred.ravel())
        else:
            # Compute precision and recall
            prec, recall, thresh = precision_recall_curve(self.y_true, self.y_pred)
            # Compute area
            pr_auc = average_precision_score(self.y_true, self.y_pred)
        # Compute the y & x axis to trace the threshold
        idx_thresh, idy_thresh = recall[argmin(abs(thresh - t))], prec[argmin(abs(thresh - t))]

        # Plot PR curve
        l, = plt.plot(recall, prec, color=c_pr_curve, lw=linewidth, linestyle=ls_pr_curve, marker=marker_pr_curve)
        lines.append(l)
        labels.append('PR curve (area = {})'.format(round(pr_auc, 2)))

        # Plot mean precision
        l, = plt.plot([0, 1], [mean(prec), mean(prec)], color=c_mean_prec,
                      lw=linewidth, linestyle=ls_mean_prec)
        lines.append(l)
        labels.append('Mean precision = {}'.format(round(mean(prec), 2)))

        # Fscore-iso
        if len(fscore_iso) > 0:  # Check to plot or not the fscore-iso
            for f_score in fscore_iso:
                x = linspace(0.005, 1, 100)  # Set x range
                y = f_score * x / (beta ** 2 * x + x - beta ** 2 * f_score)  # Compute fscore-iso using f-score formula
                l, = plt.plot(x[y >= 0], y[y >= 0], color=c_f1_iso, linestyle=ls_fscore_iso,
                              alpha=iso_alpha)
                plt.text(s='f{:s}={:0.1f}'.format(str(beta), f_score), x=0.9, y=y[-10] + 0.02, alpha=iso_alpha)
            lines.append(l)
            labels.append('iso-f{:s} curves'.format(str(beta)))

            # Set ylim to see entire iso and to avoid a max ylim really high
            plt.ylim([0.0, 1.05])

        # Plot threshold
        if plot_threshold:
            # Plot vertical and horizontal line
            plt.axhline(y=idy_thresh, color=c_thresh_lines, linestyle=ls_thresh, lw=linewidth)
            plt.axvline(x=idx_thresh, color=c_thresh_lines, linestyle=ls_thresh, lw=linewidth)

            # Plot text threshold
            if idx_thresh > 0.5 and idy_thresh > 0.5:
                plt.text(x=idx_thresh - x_text_margin, y=idy_thresh - y_text_margin,
                         s='Threshold : {:.2f}'.format(t))
            elif idx_thresh <= 0.5 and idy_thresh <= 0.5:
                plt.text(x=idx_thresh + x_text_margin, y=idy_thresh + y_text_margin,
                         s='Threshold : {:.2f}'.format(t))
            elif idx_thresh <= 0.5 < idy_thresh:
                plt.text(x=idx_thresh + x_text_margin, y=idy_thresh - y_text_margin,
                         s='Threshold : {:.2f}'.format(t))
            elif idx_thresh > 0.5 >= idy_thresh:
                plt.text(x=idx_thresh - x_text_margin, y=idy_thresh + y_text_margin,
                         s='Threshold : {:.2f}'.format(t))

            # Plot redpoint of threshold on the ROC curve
            plt.plot(idx_thresh, idy_thresh, marker='o', color=c_thresh_point)

        # Axis and legends
        plt.xlim([0.0, 1.0])
        plt.legend(lines, labels)
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        if plot_threshold:
            plt.title('{} (Threshold = {})'.format(title, round(t, 2)))
        else:
            plt.title(title)
        return plt

    def class_distribution(self, threshold=None, display_prediction=True, alpha=.5, jitter=.3, pal_colors=None,
                                display_violin=True, c_violin='white', strip_marker_size=4, strip_lw_edge=None,
                                strip_c_edge=None, ls_thresh_line=':', c_thresh_line='red', lw_thresh_line=2,
                                title=None):
        """
        Plot distribution of the predictions for each classes.
        Note : Threshold here is importante because it define colors for True Positive,
        False Negative, True Nagative and False Positive.
        Parameters
        ----------
        threshold : float, default=0.5
            Threshold to determnine the rate between positive and negative values of the classification.
        display_prediction : bool, default=True
            Display the point representing each predictions.
        alpha : float, default=0.5
            Transparency of each predicted point.
        jitter : float, default=0.3
                Amount of jitter (only along the categorical axis) to apply. This can be useful when you have many
                points and they overlap, so that it is easier to see the distribution. You can specify the amount
                of jitter (half the width of the uniform random variable support), or just use True for a good default.
                See : https://seaborn.pydata.org/generated/seaborn.stripplot.html
        pal_colors : palette name, list, or dict, optional, default=["#00C853", "#FF8A80", "#C5E1A5", "#D50000"]
            Colors to use for the different levels of the hue variable. Should be something that can be interpreted
            by color_palette(), or a dictionary mapping hue levels to matplotlib colors.
            See : https://seaborn.pydata.org/generated/seaborn.stripplot.html
        display_violin : bool, default=True
            Display violin plot.
        c_violin : string, default='white'
            Color of the violinplot.
        strip_marker_size : int, default='4'
            Size of marker representing predictions.
        strip_lw_edge : float, default=None
            Size of the linewidth for the edge of point prediction.
        strip_c_edge : string, default=None
            Color of the linewidth for the edge of point prediction.
        ls_thresh_line : string, default=':'
            Linestyle for the threshold line.
        c_thresh_line : string, default='red'
            Color for the threshold line.
        lw_thresh_line : float, default=2
            Line width of the threshold line.
        title : string, default=None
            String for the title of the graphic.
        Returns
        -------
        DataFrame with the following column :
        - True Class
        - Predicted Proba
        - Predicted Type
        - Predicted Class
        """
        if pal_colors is None:
            pal_colors = ["#00C853", "#FF8A80", "#C5E1A5", "#D50000"]
        if threshold is None:
            t = self._threshold_
        else:
            t = threshold
        plt.clf()
        def __compute_thresh(row, _threshold):
            if (row['pred'] >= _threshold) & (row['class'] == 1):
                return "TP"
            elif (row['pred'] >= _threshold) & (row['class'] == 0):
                return 'FP'
            elif (row['pred'] < _threshold) & (row['class'] == 1):
                return 'FN'
            elif (row['pred'] < _threshold) & (row['class'] == 0):
                return 'TN'

        if self.n_classes>2:
            pred_df = pd.DataFrame({'class': label_binarize(self.y_true, classes=list(self.labels_names.keys())).ravel(),
                                    'pred': self.y_pred.ravel()})

        else:
            pred_df = pd.DataFrame({'class': self.y_true,
                                'pred': self.y_pred})

        pred_df['type'] = pred_df['pred']
        pred_df['type'] = pred_df.apply(lambda x: __compute_thresh(x, t), axis=1)

        pred_df_plot = pred_df.copy(deep=True)
        pred_df_plot["class"] = pred_df_plot["class"].apply(lambda x: list(self.labels_names.values())[x])

        # Plot violin pred distribution
        if display_violin:
            sns.violinplot(x='class', y='pred', data=pred_df_plot, inner=None, color=c_violin, cut=0)

        # Plot prediction distribution
        if display_prediction:
            sns.stripplot(x='class', y='pred', hue='type', data=pred_df_plot,
                          jitter=jitter, alpha=alpha,
                          size=strip_marker_size, palette=sns.color_palette(pal_colors),
                          linewidth=strip_lw_edge, edgecolor=strip_c_edge)

        # Plot threshold
        plt.axhline(y=t, color=c_thresh_line, linewidth=lw_thresh_line, linestyle=ls_thresh_line)
        if title is None:
            plt.title('Threshold at {:.2f}'.format(t))
        else:
            plt.title(title)

#        pred_df['Predicted Class'] = pred_df['pred'].apply(lambda x: self.labels_names[1] if x >= t else self.labels_names[0])
#        pred_df.columns = ['True Class', 'Predicted Proba', 'Predicted Type', 'Predicted Class']
#        plt.close(fig)
        return plt

    def score_distribution(self, threshold=None, plot_hist_TN=True, kde_ksw_TN={'shade': True},
                                label_TN='True Negative', c_TN_curve='green'):
        if threshold is None:
            t = self._threshold_
        else:
            t = threshold
        if self.n_classes>2:
            df = pd.DataFrame({'y_true': label_binarize(self.y_true, classes=list(self.labels_names.keys())).ravel(), 'y_pred': self.y_pred.ravel()})
        else:
            df = pd.DataFrame({'y_true': self.y_true, 'y_pred': self.y_pred})

        plt.clf()

        TN_pred = list(df[df['y_true'] == 0]['y_pred'])
        TP_pred = list(df[df['y_true'] == 1]['y_pred'])

        # Plot True Negative predictions
        TN_pred=[round(tn, 4) for tn in TN_pred]
        ax = sns.histplot(TN_pred, kde=True,  label=label_TN,
                          color=c_TN_curve)
        # Plot False Positive predictions using hatch
        kde_x, kde_y = ax.lines[0].get_data()
        ax.fill_between(kde_x, kde_y, where=(kde_x >= t),
                        interpolate=True, facecolor="none",
                        hatch="////", edgecolor="black",
                        label='False Positive')

        # Plot True Positive predictions
        TP_pred=[round(tn, 4) for tn in TP_pred]
        ax = sns.histplot(TP_pred, color="r", kde=True, label='True Positive')
        # Plot False Negative predictions using hatch
        kde_x, kde_y = ax.lines[1].get_data()
        ax.fill_between(kde_x, kde_y, where=(kde_x <= t),
                        interpolate=True, facecolor="none",
                        hatch="\\\\\\\\", edgecolor="black",
                        label='False Negative')

        # Plot the threshold
        plt.axvline(t, label='Threshold {:.2f}'.format(t),
                    color='black',
                    linestyle=':')

        # Show legend
        plt.legend(loc='best')
        # Set axis and title
        plt.xlabel('Predictions probability')
        plt.xlabel('Predicted observations')
        plt.title('Distribution of predicted probability')
        plt.xlim(0, 1)

        return plt

    def threshold(self, threshold=None, beta=1, title=None,
                       annotation=True, bbox_dict=None, bbox=True, arrow_dict=None, arrow=True,
                       plot_fscore=True, plot_recall=True, plot_prec=True, plot_fscore_max=True,
                       c_recall_line='green', lw_recall_line=2, ls_recall_line='-', label_recall='Recall',
                       marker_recall='',
                       c_prec_line='blue', lw_prec_line=2, ls_prec_line='-', label_prec='Precision', marker_prec='',
                       c_fscr_line='red', lw_fscr_line=2, ls_fscr_line='-', label_fscr=None, marker_fscr='',
                       marker_fscore_max='o', c_fscore_max='red', markersize_fscore_max=5,
                       plot_threshold=True, c_thresh_line='black', lw_thresh_line=2, ls_thresh_line='--',
                       plot_best_threshold=True, c_bestthresh_line='black', lw_bestthresh_line=1,
                       ls_bestthresh_line=':'):
        """
        Plot precision - threshold, recall - threshold and fbeta-score - threshold curves.
        Also plot threshold line for a given threshold and threshold line for the best ratio between precision
        and recall.
        Parameters
        ----------
        threshold : float, default=0.5
            Threshold to determnine the rate between positive and negative values of the classification.
        beta : float, default=1,
            Set beta to another float to use a different f_beta score. See definition of f_beta-score
            for more information : https://en.wikipedia.org/wiki/F1_score
        title : string, default=None
            String for the title of the graphic.
        annotation : bool, default=True
            Boolean to display annotation box with theshold, precision and recall score.
        bbox_dict : dict, default={'facecolor': 'none',
                                'edgecolor': 'black',
                                'boxstyle': 'round',
                                'alpha': 0.4,
                                'pad': 0.3}
            Set the parameters of the bbox annotation. See matplotlib documentation_ for more information.
        bbox : bool, default=True
            Boolean to display the bbox around annotation.
        arrow_dict : dict, default={'arrowstyle': "->", 'color': 'black'}
            Set the parameters of the bbox annotation. See matplotlib documentation_ for more information.
        arrow : bool, default=True
            Boolean to display the array for the annotation.
        plot_fscore : bool, default=True
            Boolean to plot the FBeta-Score curve.
        plot_recall : bool, default=True
            Boolean to plot the recall curve.
        plot_prec : bool, default=True
            Boolean to plot the precision curve.
        plot_fscore_max : bool, default=True
            Boolean to plot the point showing fbeta-score max.
        c_recall_line : string, default='green'
            Color of the recall curve.
        lw_recall_line : float, default=2
            Linewidth of the recall curve.
        ls_recall_line : string, default='-'
            Linestyle of the recall curve.
        label_recall : string, default='Recall'
            Label of the recall curve.
        marker_recall : string, default=''
            Marker of the recall curve.
        c_prec_line : string, default='green'
            Color of the prec curve.
        lw_prec_line : float, default=2
            Linewidth of the prec curve.
        ls_prec_line : string, default='-'
            Linestyle of the prec curve.
        label_prec : string, default='prec'
            Label of the prec curve.
        marker_prec : string, default=''
            Marker of the prec curve.
        c_fscr_line : string, default='green'
            Color of the fscr curve.
        lw_fscr_line : float, default=2
            Linewidth of the fscr curve.
        ls_fscr_line : string, default='-'
            Linestyle of the fscr curve.
        label_fscr : string, default='fscr'
            Label of the fscr curve.
        marker_fscr : string, default=''
            Marker of the fscr curve.
        marker_fscore_max : string, default='o'
            Marker for the fscore max point.
        c_fscore_max : string, default='red'
            Color for the fscore max point.
        markersize_fscore_max : float, default=5
            Marker size for the fscore max point.
        plot_threshold : bool, default=True
            Plot a line at the given threshold.
        c_thresh_line : string, default='black'
            Color for the threshold line.
        lw_thresh_line : float, default=2
            Linewidth for the threshold line.
        ls_thresh_line : string, default='--'
            Linestyle for the threshold line.
        plot_best_threshold : bool, default=True
            Plot a line at the best threshold (best ratio precision-recall).
        c_bestthresh_line : string, default='black'
            Color for the best threshold line.
        lw_bestthresh_line : float, default=2
            Linewidth for the best threshold line.
        ls_bestthresh_line : string, default='--'
            Linestyle for the best threshold line.
        Returns
        -------
        References
        ----------
        .. _documentation: https://matplotlib.org/users/annotations.html#annotating-with-text-with-box
        """
        if threshold is None:
            t = self._threshold_
        else:
            t = threshold

        plt.clf()
        if self.n_classes>2:

            precision, recall, _ = precision_recall_curve(label_binarize(self.y_true, classes=list(self.labels_names.keys())).ravel(), self.y_pred.ravel())
        else:
            precision, recall, _ = precision_recall_curve(self.y_true, self.y_pred, pos_label=list(self.labels_names.keys())[-1])
        fscore = (1 + beta ** 2) * (precision * recall) / ((beta ** 2 * precision) + recall)

        thresh = linspace(0, 1, len(recall))
        y_max_fscore, x_max_fscore = max(fscore), thresh[argmax(fscore)]

        opti_thresh = 0
        opti_recall = 0
        for i, t_ in enumerate(thresh):
            if abs(precision[i] - recall[i]) < 0.01:
                opti_thresh = t_
                opti_preci = precision[i]
                opti_recall = recall[i]
                break

        # Plot recall
        if plot_recall:
            plt.plot(thresh, recall, label=label_recall,
                     color=c_recall_line, lw=lw_recall_line,
                     linestyle=ls_recall_line, marker=marker_recall)

        # Plot precision
        if plot_prec:
            plt.plot(thresh, precision, label=label_prec,
                     color=c_prec_line, lw=lw_prec_line,
                     linestyle=ls_prec_line, marker=marker_prec)

        # Plot fbeta-score
        if plot_fscore:
            if label_fscr is None:
                label_fscr = 'F{:s}-score (max={:.03f})'.format(str(beta), y_max_fscore)
            plt.plot(thresh, fscore, label=label_fscr,
                     color=c_fscr_line, lw=lw_fscr_line,
                     linestyle=ls_fscr_line, marker=marker_fscr)

        # Plot max fbeta-score
        if plot_fscore_max:
            plt.plot(x_max_fscore, y_max_fscore, marker=marker_fscore_max,
                     markersize=markersize_fscore_max, color=c_fscore_max)

        # Plot threshold
        if plot_threshold:
            plt.axvline(t, linestyle=ls_thresh_line, color=c_thresh_line, lw=lw_thresh_line)
        if plot_best_threshold:
            plt.axvline(opti_thresh, linestyle=ls_bestthresh_line, color=c_bestthresh_line, lw=lw_bestthresh_line)
            plt.plot(opti_thresh, opti_recall, color=c_bestthresh_line, marker='o', markersize=4)
        # Plot best rate between prec/recall
        if annotation:
            ## Annotation dict :
            if bbox is True and bbox_dict is None:
                bbox_dict = dict(
                    facecolor='none',
                    edgecolor='black',
                    boxstyle='round',
                    alpha=0.4,
                    pad=0.3)
            if arrow is True and arrow_dict is None:
                arrow_dict = dict(
                    arrowstyle="->",
                    color='black')
            plt.annotate(text='Thresh = {:0.2f}\nRecall=Prec={:0.2f}'.format(opti_thresh, opti_recall),
                         xy=(opti_thresh, opti_recall),
                         xytext=(opti_thresh + 0.02, opti_recall - 0.2),
                         bbox=bbox_dict,
                         arrowprops=arrow_dict
                         )

        # Limit
        plt.xlim(0, 1)
        plt.ylim(0, 1)

        # Plot text
        if title is None:
            plt.title('Precision/Recall/F{:s}-score - Threshold Curve'.format(str(beta)))
        else:
            plt.title(title)
        plt.xlabel('Threshold')
        plt.legend()
        plt.xticks(arange(0, 1, 0.1))
        plt.ylabel('Scores')


        return plt

    def _class_report(self, threshold=.5, output_dict=True):

        if threshold is None:
            t = self._threshold_
        else:
            t = threshold
        if self.n_classes>2:
            y_pred_class = [l for l in argmax(self.y_pred, axis=1)]
        else:
            y_pred_class = [1 if y_i > t else 0 for y_i in self.y_pred]

        return classification_report(self.y_true, y_pred_class, labels=list(self.labels_names.keys()), output_dict=output_dict, target_names=list(self.labels_names.values()))



    def class_report(self, title='Classification report', cmap='RdBu', threshold=.5):

        plt.clf()
        plt.gcf().set_size_inches(10, 10)

        classificationReport=self._class_report(threshold, output_dict=True)

        plot=sns.heatmap(pd.DataFrame(classificationReport).iloc[:-1, :].T, annot=True)

        return plot.get_figure()

    def errors(self, threshold=0.5):

        if threshold is None:
            t = self._threshold_
        else:
            t = threshold

        # Convert prediction probility into class
        #
        if len(self.y_pred.shape)==1:
            y_pred_class = [1 if y_i > t else 0 for y_i in self.y_pred]
        else:
            y_pred_class = [l for l in argmax(self.y_pred, axis=1)]

        data = np.array(confusion_matrix(self.y_true, y_pred_class))

#        list =['red','blue', 'yellow','pink']# ["class_"+str(l) for l in self.labels]

        # For loop for creating stacked bar chart
        plt.clf()
        X = list(self.labels_names.values())
        fig, ax=plt.subplots(figsize=(10, 10))
        for i in range(data.shape[0]):
            plt.bar(X, data[i], bottom=np.sum(data[:i], axis=0), label=X[i])
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")
        plt.title("Prediction errors per Class", fontsize=20)
        # Display
        ax.legend()
        return plt
        # Define the confusion matrix


    def plot_tree(self, X=None, y=None):

        if X is None or y is None:
            X=self.X
            y=self.y
        self.classifier.fit(X, y)
        return dtreeviz(self.classifier, X, y,
                        target_name='variety',
                        feature_names=self.features_names,
                        class_names=self.labels_names)



    def tsne(self, X=None, y=None):

        if X is None or y is None:
            X=self.X.toarray()
            y=self.y


#        from sklearn.manifold import TSNE
        plt.clf()
        logger.info("Fitting TSNE()")
        X_embedded = TSNE(n_components=2,
                              perplexity=30,
#                              initialization="pca",
                              metric="cosine"
                              ).fit_transform(X)

        X = pd.DataFrame(X_embedded)

        logger.info("Rendering Visual")
#        import plotly.express as px

        df = X
        df['target']=y
        df['target'] =df['target'].astype(str)


        sns.scatterplot(0, 1, data=df, hue='target')
        plt.gca().update(dict(title="TSNE Projection of {} Documents".format(len(y))))


        logger.info("Visual Rendered Successfully")

        return plt

    def umap(self, X=None, y=None):

        import umap
        if X is None or y is None:
            X=self.X.toarray()
            y=self.y

        reducer = umap.UMAP(n_components=2, n_jobs=1)
        logger.info("Fitting UMAP()")
        embedding = reducer.fit_transform(X)
        X = pd.DataFrame(embedding)


        df = X
        df['target']=[str(i) for i in y]
        df.columns=['CP1', 'CP2', 'target']




        sns.scatterplot('CP1', 'CP2', data=df, hue='target')
        plt.gca().update(dict(title="UMAP Projection of {} Documents".format(len(y))))


        logger.info("Visual Rendered Successfully")
        return plt


    def calibration_(self):
        from sklearn.calibration import calibration_curve

        plt.figure(figsize=(7, 6), dpi=300)
        ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)

        ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
        logger.info("Scoring test/hold-out set")
        prob_pos = self.classifier._predict_proba(self.X)[:, 1]
        prob_pos = (prob_pos - prob_pos.min()) / (
                prob_pos.max() - prob_pos.min()
        )
        (
            fraction_of_positives,
            mean_predicted_value,
        ) = calibration_curve(self.y, prob_pos, n_bins=10)
        ax1.plot(
            mean_predicted_value,
            fraction_of_positives,
            "s-",
            label=f"{str(self.classifier)}",
        )

        ax1.set_ylabel("Fraction of positives")
        ax1.set_ylim([0, 1])
        ax1.set_xlim([0, 1])
        ax1.legend(loc="lower right")
        ax1.set_title("Calibration plots (reliability curve)")
        ax1.set_facecolor("white")
        ax1.grid(b=True, color="grey", linewidth=0.5, linestyle="-")
        plt.tight_layout()

        return plt


    def calibration(self):

        from sklearn.preprocessing import label_binarize
        from sklearn.calibration import calibration_curve

        plt.figure(figsize=(7, 6), dpi=300)
        ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)

        ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
        logger.info("Scoring test/hold-out set")
        y = label_binarize(self.y, classes=list(self.labels_names.keys()))
        for i in range(self.n_classes):
            prob_pos = self.classifier.predict_proba(self.X)[:, i]
            prob_pos = (prob_pos - prob_pos.min()) / (
                    prob_pos.max() - prob_pos.min()
            )
            (
                fraction_of_positives,
                mean_predicted_value,
             ) = calibration_curve(y[:,i], prob_pos, n_bins=20)
            plt.plot(
                mean_predicted_value,
                fraction_of_positives,
                "s-",
                label=f"{self.labels_names[i]}",
            )

        ax1.set_ylabel("Fraction of positives")
        ax1.set_ylim([0, 1])
        ax1.set_xlim([0, 1])
        ax1.legend(loc="lower right")
        ax1.set_title("Calibration plots (reliability curve)")
        ax1.set_facecolor("white")
        ax1.grid(b=True, color="grey", linewidth=0.5, linestyle="-")
        plt.tight_layout()

        return plt





