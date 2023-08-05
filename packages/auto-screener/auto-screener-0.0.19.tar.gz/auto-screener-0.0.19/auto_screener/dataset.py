# dataset.py

import os
from pathlib import Path
from typing import (
    Union, Optional, Tuple, Iterable, Any, Callable
)

import pandas as pd

from auto_screener.hints import Number

__all__ = [
    "row_to_dataset",
    "save_dataset",
    "load_dataset",
    "update_dataset",
    "split_dataset",
    "strip_dataset",
    "validate_dataset",
    "OHLCV_COLUMNS",
    "OHLC_COLUMNS",
    "OPEN",
    "CLOSE",
    "HIGH",
    "LOW",
    "VOLUME",
    "DATE_TIME",
    "BIDS",
    "ASKS",
    "find_column"
]

OPEN = "Open"
CLOSE = "Close"
HIGH = "High"
LOW = "Low"
VOLUME = "Volume"
DATE_TIME = 'DateTime'

BIDS = "Bids"
ASKS = "Asks"

OHLC_COLUMNS = (OPEN, HIGH, LOW, CLOSE)
OHLCV_COLUMNS = (*OHLC_COLUMNS, VOLUME)

def row_to_dataset(
        dataset: Union[pd.DataFrame, pd.Series],
        index: Optional[int] = None
) -> pd.DataFrame:
    """
    Creates a dataframe from the row.

    :param dataset: The base dataset from witch the row came.
    :param index: The index of the row to create a dataset for.

    :return: The dataset from the row.
    """

    if isinstance(dataset, pd.DataFrame):
        if index is None:
            raise ValueError(
                f"Index must an int when dataset "
                f"is of type {pd.DataFrame}."
            )
        # end if

        return pd.DataFrame(
            {
                column: [value] for column, value in
                dict(dataset.iloc[index]).items()
            },
            index=[dataset.index[index]]
        )

    elif isinstance(dataset, pd.Series):
        return pd.DataFrame(
            {
                column: [value] for column, value in
                dict(dataset).items()
            },
            index=[index or 0]
        )

    else:
        raise TypeError(
            f"Dataset must be either of type {pd.DataFrame}, "
            f"or {pd.Series}, not {type(dataset)}."
        )
    # end if
# end row_to_dataset

def update_dataset(base: pd.DataFrame, new: pd.DataFrame) -> None:
    """
    Updates the ba se dataframe with new columns from the new dataframe.

    :param base: The base dataframe to update.
    :param new: The new dataframe with the new columns.
    """

    if not len(base) == len(new):
        raise ValueError(
            f"DataFrames lengths must match "
            f"(got {len(base)} and {len(new)} instead)."
        )
    # end if

    for column in new.columns:
        if column not in base.columns:
            base[column] = new[column]
        # end if
    # end for
# end update_dataset

def split_dataset(
        dataset: Union[pd.DataFrame, pd.Series],
        size: Optional[Number] = None,
        length: Optional[int] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits the new_dataset into to parts at the point of the given size.

    :param dataset: The new_dataset to split.
    :param size: The size of the first part.
    :param length: The length of the split.

    :return: The two datasets.
    """

    if (size is None) and (length is None):
        raise ValueError(
            "Cannot split the dataset when neither "
            "size nor length parameters are defined."
        )
    # end if

    length = length or int(len(dataset) * size)

    return dataset[:length], dataset[length:]
# end split_dataset

def strip_dataset(dataset: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    """
    Strips the columns from the new_dataset.

    :param dataset: The new_dataset to remove features from.
    :param columns: The columns to validate.

    :return: The new new_dataset.
    """

    return dataset.drop(
        [
            column for column in columns
            if column in dataset.columns
        ], axis=1
    )
# end strip_dataset

def validate_dataset(
        dataset: pd.DataFrame,
        columns: Optional[Iterable[str]] = None,
        length: Optional[int] = None
) -> None:
    """
    Validates the new_dataset to have the columns.

    :param dataset: The new_dataset to validate.
    :param columns: The columns to validate.
    :param length: The length of the valid dataset.
    """

    if (
        (columns is not None) and
        not all(column in dataset.columns for column in columns)
    ):
        missing = [
            column for column in columns
            if column not in list(dataset.columns)
        ]

        redundant = [
            column for column in list(dataset.columns)
            if column not in columns
        ]

        raise ValueError(
            f"DataFrame must include the "
            f"columns by the names: {columns}.\n"
            f"Given columns: {', '.join(dataset.columns)}.\n"
            f"Missing columns: {missing}.\n"
            f"Redundant columns: {redundant}."
        )
    # end if

    if (length is not None) and len(dataset) != length:
        raise ValueError(
            f"Dataset must have length of {length}, "
            f"not: {len(dataset)}."
        )
    # end if
# end validate_dataset

def save_dataset(dataset: pd.DataFrame, path: Union[str, Path]) -> None:
    """
    Saves the data.

    :param dataset: The dataset to save.
    :param path: The saving path.
    """

    if os.path.split(path)[0]:
        os.makedirs(os.path.split(path)[0], exist_ok=True)
    # end if

    dataset.to_csv(path)
# end save_dataset

def load_dataset(path: Union[str, Path]) -> pd.DataFrame:
    """
    Loads the dataset from the path.

    :param path: The saving path.

    :return: The loaded dataset.
    """

    dataset = pd.read_csv(path)

    index_column = list(dataset.columns)[0]
    dataset.index = pd.DatetimeIndex(dataset[index_column])
    del dataset[index_column]
    dataset.index.name = None

    return dataset
# end load_dataset

def find_column(
        dataset: pd.DataFrame,
        columns: Iterable[Any],
        validation: Optional[Callable[[pd.Series], bool]] = None
) -> Optional[pd.Series]:
    """
    Finds the first valid column and returns it.

    :param dataset: The dataset to search.
    :param columns: The column names to search from, by order.
    :param validation: The validation function.

    :return: The valid column.
    """

    for column in columns:
        if column not in dataset:
            continue
        # end if

        if (
            (validation is None) or
            (callable(validation) and validation(dataset[column]))
        ):
            return dataset[column]
        # end if
    # end for
# end find_column