# %pip install --quiet --upgrade catboost googledrivedownloader shap altair

import logging
from typing import *

# For transformations and predictions
import pandas as pd
import shap


# For validation
from sklearn.model_selection import train_test_split as split

from litelearn.exceptions import *

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig()
shap.initjs()

UNKNOWN_CATEGORY_VALUE = "LITELEARN_UNKNOWN"
NA_CATEGORY_VALUE = "LITELEARN_NA_VALUE"


def print_version(lib):
    print(lib.__name__, lib.__version__)


def default_value(value, default, marker=None):
    return (value, default)[value == marker]


def _is_interactive():
    try:
        import ipywidgets

        return True
    except ImportError:
        return False


def display_evaluation_comparison(before, after):
    print("current performance:")
    print(before)
    print()
    print("after dropping:")
    print(after)
    print()
    print("error reduction (higher is better):")
    print(before - after)
    print()


def xy_df(df, target, train_index=None):
    X = df.copy().drop(columns=target)
    y = df[target]

    if y.isna().sum():
        raise TrainingException(
            f'unable to use "{target}" as target column since it contains null values'
        )

    return X, y


## why is this needed?
def xy_split(
    X: pd.DataFrame,
    y: pd.Series,
    train_index=None,
    test_size: Union[float, int] = None,
    random_state=None,
    stratify: Union[str, pd.Series] = None,
):
    if train_index is not None and test_size is not None:
        raise ValueError("cannot specify both train_index and test_size")
    if train_index is not None and stratify is not None:
        raise ValueError("cannot specify both train_index and stratify")

    test_size = default_value(test_size, 0.3)
    random_state = default_value(random_state, 314159)
    if stratify and isinstance(stratify, str):
        stratify = y if stratify == y.name else X[stratify]

    # print('test size: ', test_size)
    if train_index is None:
        # print('stratify', stratify)
        X_train, X_test, y_train, y_test = split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            shuffle=True,
            stratify=stratify,
        )
    else:
        X_train, X_test, y_train, y_test = (
            X.loc[train_index],
            X.drop(index=train_index),
            y[train_index],
            y.drop(train_index),
        )
    return X_train, X_test, y_train, y_test


def fill_nulls_naively(df):
    # return df
    print(f"the following cols contain null values and will be filled naively:")
    nulls = df[df.columns[df.isna().sum().astype(bool)]]

    num_nulls = nulls.select_dtypes(include="number")
    print("numerical columns:")
    print(list(num_nulls.columns))
    for col in num_nulls.columns:
        df[col].fillna(df[col].mean(), inplace=True)

    cat_nulls = nulls.select_dtypes(exclude="number")
    print("categorical columns:")
    print(list(cat_nulls.columns))
    for col in cat_nulls.columns:
        mode = df[col].mode()[0]
        print(col, "- mode:", mode)
        df[col].fillna(mode, inplace=True)

    result = df.join(nulls.isna().add_suffix("_is_missing"))
    return result


def cleanup_df(
    df,
    target,
    train_index=None,
    use_categories=None,
    use_nulls=None,
):
    use_categories = default_value(use_categories, True)
    # use_nulls=True will use the native null handling of catboost
    # use_nulls=False will fillna and add _is_missing columns
    use_nulls = default_value(use_nulls, True)  # TODO: fix issues for use_nulls=False

    X, y = xy_df(df=df, train_index=train_index, target=target)
    if y.dtype.name in ['string', 'object']:
        y = y.astype('category')

    cat_cols = X.select_dtypes(exclude=["number", "bool", "datetime"]).columns

    # allow using catboost null handling capability
    if not use_nulls:
        X = fill_nulls_naively(X)
    else:
        # add NA_CATEGORY_VALUE to categorical columns
        for col in cat_cols:
            if X[col].dtype.name == "category":
                X[col].cat.add_categories(NA_CATEGORY_VALUE, inplace=True)

        # fillna with NA_CATEGORY_VALUE
        X[cat_cols] = X[cat_cols].fillna(NA_CATEGORY_VALUE).astype("string")

    for col in cat_cols:
        if not use_categories:
            print(f"casting {col} onto category codes")
            X[col] = X[col].astype("category").cat.codes
        else:
            print(f"casting {col} onto category")
            ### Cannot convert StringArray to numpy.ndarray
            ### https://github.com/alteryx/evalml/pull/3966
            cat_col = X[col].astype("string").astype("object").astype("category")
            if UNKNOWN_CATEGORY_VALUE not in cat_col.cat.categories:
                cat_col = cat_col.cat.add_categories(UNKNOWN_CATEGORY_VALUE)
            X[col] = cat_col

    # display(X.info())
    return X, y
