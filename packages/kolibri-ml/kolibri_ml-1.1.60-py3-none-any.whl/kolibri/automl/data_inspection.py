import pandas as pd
import numpy as np

data_report_file_name="data_report.md"
DISCRETE_NUM_LIMIT=20

def get_dataframe_info(df):
    """
    input
       df -> DataFrame
    output
       df_null_counts -> DataFrame Info (sorted)
    """

    df_types = pd.DataFrame(df.dtypes)
    df_nulls = len(df)-df.count()

    df_null_count = pd.concat([df_types, df_nulls], axis=1)
    df_null_count = df_null_count.reset_index()

    # Reassign column names
    col_names = ["features", "types", "null_counts"]
    df_null_count.columns = col_names

    # Add this to sort
    df_null_count = df_null_count.sort_values(by=["null_counts"], ascending=False)

    return df_null_count


def write_data_summary(data: pd.DataFrame):
    """The function data_summary() is used to provide a basic details of the
       given tabular dataset.

       data_summary(data) function contains one argument.

       data -> We need to pass the entire dataframe to this function. (type = dataframe)

       Example: data_summary(data = dataframe_name)"""

    from mdutils.mdutils import MdUtils
    data_frame_properties={}
    mdFile = MdUtils(file_name=data_report_file_name, title='Data Analysis report')


    data_frame_properties["nb-rows"]=len(data)
    data_frame_properties["nb-columns"]=len(data.columns)

    mdFile.new_header(level=1, title="General info")
    mdFile.new_line('*' * round(data.shape[1] / 2) + " "+"Column present in the data" + " "+'*' * round(data.shape[1] / 2))
    mdFile.new_line()
    mdFile.new_line('*' * round(data.shape[1] / 2) + " "+"Number of rows and columns in the data" + " "+'*' * round(data.shape[1] / 2))
    mdFile.new_line("Number of observation present in the data are {}.".format(data.shape[0]))
    mdFile.new_line("Number of columns present in the data are {}.".format(data.shape[1]))
    mdFile.new_line()

    numerical_columns=data.select_dtypes(exclude=['object', 'category', 'datetime64']).columns.values.tolist()
    mdFile.new_header(level=2, title="Numerical columns in the data")
    if len(numerical_columns) > 0:
        mdFile.new_list([str(v) for v in numerical_columns])
        mdFile.new_line("Number of numerical columns present in the data are {}.".format(len(list(data.select_dtypes(exclude=['object', 'category', 'datetime64']).columns))))
    else:
        mdFile.new_line("There are no numerical columns present in the data.")
    mdFile.new_line()

    categorical_columns=data.select_dtypes(include=['object', 'category']).columns.values.tolist()
    mdFile.new_header(level=2, title="Categorical columns in the data")
    if len(categorical_columns) > 0:
        mdFile.new_list([str(v) for v in categorical_columns])
        mdFile.new_line("Number of categorical columns present in the data are {}.".format(len(list(data.select_dtypes(include=['object', 'category']).columns))))
    else:
        mdFile.new_line("There are no categrical columns present in the data.")
    mdFile.new_line()

    date_time_columns=data.select_dtypes(include=['datetime64']).columns.values.tolist()
    mdFile.new_header(level=2, title="Date columns in the data" )
    if len(date_time_columns) > 0:
        mdFile.new_list([str(v) for v in date_time_columns])
        mdFile.new_line("Number of date and time columns present in the data are {}.".format(len(list(data.select_dtypes(include=['datetime64']).columns))))
    else:
        mdFile.new_line("There are no date and time columns present in the data.")
    mdFile.new_line()

    mdFile.new_header(level=2, title="Information about the data")
    mdFile.new_paragraph(get_dataframe_info(data).to_markdown())
    mdFile.new_line()

    mdFile.new_header(level=2, title="Numerical description in the data")
    if len(list(data.select_dtypes(exclude=['object', 'category']).columns)) > 0:
            mdFile.new_line(data.describe().to_markdown())
            mdFile.new_line()
    else:
            mdFile.new_line("No numerical column is available for description")

    mdFile.new_header(level=2, title="Categrical description in the data")

    if len(list(data.select_dtypes(include=['object', 'category']).columns)) > 0:
            mdFile.new_line(data[list(data.select_dtypes(include=['object', 'category']).columns)].describe())
            mdFile.new_line()
    else:
            mdFile.new_line("No categorical column is available for description")

    mdFile.new_header(level=2, title="Null values present in the data")
    mdFile.new_line(data.isna().sum().sort_values(ascending=False).to_markdown())
    mdFile.new_line("Total number of null values present in the given data is {}.".format(data.isna().sum().sum()))
    mdFile.new_line()

    mdFile.new_header(level=2, title="Unique values in categrical data")
    categorical_data = list(data.select_dtypes(include=['object', 'category']).columns)
    if len(categorical_data) > 0:

            for i in categorical_data:
                mdFile.new_line("The total number of unique values present in {} is {}.".format(i, data[i].nunique()))
                unique_data = list(data[i].unique())
                if np.nan in unique_data:
                    unique_data.remove(np.nan)
                mdFile.new_line("The unique values are: {}.".format(unique_data))
                print()
    else:

            mdFile.new_line("No categorical data present.")

    mdFile.create_md_file()


def get_column_info(data, col_name):

    if col_name not in data.columns:
        raise Exception("the provided dataframe does not contain column "+col_name)
    dtype=data[col_name].dtype
    col_info= {"name": col_name, "type": None, "description": None, "unique-values": None, "min-value": None,
               "max-value": None, "nb-null-values": len(data) - data.count(), "dtype": dtype}

    if dtype not in ['object', 'string','category', 'datetime64']:
        col_info["type"]="numerical"
        col_info["description"]=data[col_name].describe().to_dict()
        col_info['min-value']=min(data[col_name])
        col_info['max-value']=max(data[col_name])
        col_info['is-discrete']=dtype == 'int64' and len(data[col_name].unique())<=DISCRETE_NUM_LIMIT

    if dtype in ['object', 'string', 'category']:
        col_info["type"]="categorical"
        col_info['unique-values']=data[col_name].value_counts().to_dict()

    if dtype in ['datetime64']:
        col_info["type"] = "datetime"
        col_info['unique-values'] = data[col_name].value_counts().to_dict()
        col_info['min-value']=min(data[col_name])
        col_info['max-value']=max(data[col_name])

    return col_info


def get_data_info(data:pd.DataFrame):

    dat_frame_info={
        "numerical_columns":[],
        "categorical_columns":[],
        "datetime_columns":[]
    }
    for i, col in enumerate(data.columns):
        col_info=get_column_info(data, col)
        col_info["id"]=i

        if col_info["type"]=="numerical":
            dat_frame_info["numerical_columns"].append(col_info)
        elif col_info["type"]=="categorical":
            dat_frame_info["categorical_columns"].append(col_info)
        elif col_info["type"]=="datetime":
            dat_frame_info["datetime_columns"].append(col_info)

    return dat_frame_info

def data_eda(data:pd.DataFrame, target_column_name, regression):

    """The function data_eda() is used to provide a basic exploratory data analysis of the
       given tabular dataset using matplotlib and seaborn library.

       data_eda(data, target_column_name, ml_type) function contains three argument.

       data -> We need to pass the entire dataframe to this function. (type = dataframe)
       target_column_name -> We need to pass the column name of the target variable (y). (type = string)
       regression -> We need to pass the supervised learning type based on the target_column_name. (type = bool)
                   True -> target_column is numerical.
                   False -> target_column is discrete or categorical.

       Example: data_eda(data = dataframe_name, target_column_name = column_name, regression = True)
                data_eda(data = dataframe_name, target_column_name = column_name, regression = False)"""

    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns

    if type(data) == pd.core.frame.DataFrame:
        data_numerical = list(data.select_dtypes(exclude=['object', 'category', 'datetime64']).columns)
        numerical_data = []
        discrete_data = []
        categorical_data = list(data.select_dtypes(include=['object', 'category']).columns)
        for i in data_numerical:
            if data[i].nunique() > 20:
                numerical_data.append(i)
        for i in data_numerical:
            if i not in numerical_data:
                discrete_data.append(i)

        print('*' * round(data.shape[1] / 2) + " "+"Univariate Analysis" + " "+'*' * round(data.shape[1] / 2))
        if len(numerical_data) > 0:
            print('*' * round(data.shape[1] / 2) + " "+"Univariate Analysis on numerical data using histogram" + " "+'*' * round(data.shape[1] / 2))
            for i in numerical_data:
                plt.figure(figsize=(12, 8))
                plt.title("Histogram for {}.".format(i))
                sns.histplot(data[i])
                plt.show()
            print()

            print('*' * round(data.shape[1] / 2) + " "+"Univariate Analysis on numerical data using boxplot" + " "+'*' * round(data.shape[1] / 2))
            for i in numerical_data:
                plt.figure(figsize=(12, 8))
                plt.title("Boxplot for {}.".format(i))
                sns.boxplot(data[i])
                plt.show()
            print()
        else:
            print("There are no numerical data present in the given data.")
            print()

        if len(discrete_data) > 0:
            print('*' * round(data.shape[1] / 2) + " "+"Univariate Analysis on discrete data using countplot" + " "+'*' * round(data.shape[1] / 2))
            for i in discrete_data:
                plt.figure(figsize=(12, 8))
                plt.title("Countplot for {}.".format(i))
                sns.countplot(data[i])
                plt.show()
            print()
        else:
            print("There are no discrete data present in the given data.")
            print()

        if len(categorical_data) > 0:
            print('*' * round(data.shape[1] / 2) + " "+"Univariate Analysis on categorical data using countplot" + " "+'*' * round(data.shape[1] / 2))
            for i in categorical_data:
                plt.figure(figsize=(12, 8))
                plt.title("Countplot for {}.".format(i))
                sns.countplot(data[i])
                plt.show()
            print()
        else:
            print("There are no categorical data present in the given data.")
            print()

        print('*' * round(data.shape[1] / 2) + " "+"Bivariate Analysis" + " "+'*' * round(data.shape[1] / 2))
        if regression == True and type(target_column_name) == str and target_column_name in numerical_data:
            print('*' * round(data.shape[1] / 2) + " "+"Bivariate Analysis on numerical data" + " "+'*' * round(data.shape[1] / 2))
            if len(numerical_data) > 0:
                for i in numerical_data:
                    if i != target_column_name and len(numerical_data) > 2:
                        plt.figure(figsize=(12, 8))
                        plt.title("Scatterplot between {} and {}.".format(i, target_column_name))
                        sns.scatterplot(x=i, y=target_column_name, data=data)
                        plt.show()
                print()
            else:
                print("There are no numerical data present in the given data.")
                print()

            print('*' * round(data.shape[1] / 2) + " "+"Bivariate Analysis on discrete data" + " "+'*' * round(data.shape[1] / 2))
            if len(discrete_data) > 0:
                for i in discrete_data:
                    if i != target_column_name:
                        plt.figure(figsize=(12, 8))
                        plt.title("Boxplot between {} and {}.".format(i, target_column_name))
                        sns.boxplot(x=i, y=target_column_name, data=data)
                        plt.show()
                print()
            else:
                print("There are no discrete data present in the given data.")
                print()

            print('*' * round(data.shape[1] / 2) + " "+"Bivariate Analysis on categorical data" + " "+'*' * round(data.shape[1] / 2))
            if len(categorical_data) > 0:
                for i in categorical_data:
                    if i != target_column_name:
                        plt.figure(figsize=(12, 8))
                        plt.title("Boxplot between {} and {}.".format(i, target_column_name))
                        sns.boxplot(x=i, y=target_column_name, data=data)
                        plt.show()
                print()
            else:
                print("There are no categorical data present in the given data.")
                print()
        elif regression == False and type(target_column_name) == str and (target_column_name in discrete_data or target_column_name in categorical_data):
            print('*' * round(data.shape[1] / 2) + " "+"Bivariate Analysis on numerical data" + " "+'*' * round(data.shape[1] / 2))
            if len(numerical_data) > 0:
                for i in numerical_data:
                    if i != target_column_name:
                        plt.figure(figsize=(12, 8))
                        plt.title("Boxplot between {} and {}.".format(i, target_column_name))
                        sns.boxplot(x=target_column_name, y=i, data=data)
                        plt.show()
                print()
            else:
                print("There are no numerical data present in the given data.")
                print()

            print('*' * round(data.shape[1] / 2) + " "+"Bivariate Analysis on discrete data" + " "+'*' * round(data.shape[1] / 2))
            if len(discrete_data) > 0:
                for i in discrete_data:
                    if i != target_column_name:
                        print("Cross tabulation between {} and {}.".format(i, target_column_name))
                        print(pd.crosstab(data[i], data[target_column_name]))
                        print()
                print()
            else:
                print("There are no discrete data present in the given data.")
                print()

            print('*' * round(data.shape[1] / 2) + " "+"Bivariate Analysis on categorical data" + " "+'*' * round(data.shape[1] / 2))
            if len(categorical_data) > 0:
                for i in categorical_data:
                    if i != target_column_name:
                        print("Cross tabulation between {} and {}.".format(i, target_column_name))
                        print(pd.crosstab(data[i], data[target_column_name]))
                        print()
                print()
            else:
                print("There are no categorical data present in the given data.")
                print()
        else:
            print("There may be an wrong input given in target_column_name or regression parameter. Please check and try again.")
            print()
    else:

        print("The given data is not a dataframe.")

