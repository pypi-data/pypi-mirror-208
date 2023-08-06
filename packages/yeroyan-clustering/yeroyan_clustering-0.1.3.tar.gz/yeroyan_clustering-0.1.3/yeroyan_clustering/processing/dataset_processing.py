"""
A module for Processing raw datasets
"""

from typing import List, Dict, Union, Literal

import attr
import numpy as np
import pandas as pd
import seaborn as sns
from loguru import logger
import numpy.typing as npt
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import OrdinalEncoder, StandardScaler

vector = npt.NDArray[np.float64]
numerical_features = npt.NDArray[vector]
label_type_alias = npt.NDArray[np.int64]
data_type_alias = List[Union[vector, numerical_features]]


@attr.s(slots=True)
class DataProcessor:
    use_pca: bool = attr.ib(default=True)
    cols: List[str] = attr.field(init=False)
    df: pd.DataFrame = attr.field(init=False)
    labels: pd.Series = attr.field(init=False)
    target_column: str = attr.ib(default=None)
    cat_cols: List[str] = attr.field(init=False)
    num_cols: List[str] = attr.field(init=False)
    fit_categorical: bool = attr.ib(default=True)
    transformer: PCA = attr.ib(default=PCA(0.98))
    untransformed_data: pd.DataFrame = attr.ib(default=None)
    scaler: StandardScaler = attr.ib(default=StandardScaler())
    features: Union[List[str], Literal['all']] = attr.ib(default=['all'])
    categorical_encoder: OrdinalEncoder = attr.ib(default=OrdinalEncoder())
    data_path: str = attr.ib(default=None, validator=attr.validators.instance_of(str))

    def __attrs_post_init__(self):
        """Load, Clean and Prepare the Dataset

        Final Stage of the __init__ is done via multiple stages:

            1. Load the Data
            2. Drop duplicates (row-wise)
            3. Handle the labels (if given such dataset)
                - Drop the target_column (specified during __init__)
                - Store it in self.labels to further compare with predicted ones
            4. Extract stats and Prepare for Preprocessing with self.extract_stats()

        Returns
        -------
        None
        """

        self.df = pd.read_csv(self.data_path)
        self.df.drop_duplicates(inplace=True)
        self.df.dropna(inplace=True)
        if self.target_column:
            self.labels = self.df[self.target_column]
            self.df.drop(self.target_column, axis=1, inplace=True)
        if self.features != ['all']:
            self.df = self.df[self.features]
        self.extract_stats()
        print('Finished Building Data Processor')

    @data_path.validator
    def data_exists(self, attribute, value):
        """Validate the existence of the data itself (csv file's path)"""
        try:
            pd.read_csv(value, nrows=10)
        except FileNotFoundError:
            raise ValueError(
                f'Error in |{attribute.name}| validation: File: {value} Not Found. Provide a valid data path')

    @features.validator
    def valid_features(self, attribute, value):
        """Validate the existence of all columns in subset of features"""
        if value != ['all']:
            df = pd.read_csv(self.data_path, nrows=10)
            cols = df.columns.tolist()
            for col in value:
                if col not in cols:
                    raise ValueError(f'Error in |{attribute.name}| validation: Feature {col} is invalid/unknown')

    def extract_stats(self) -> None:
        """Extract Stats and Prepare for Preprocessing

        Preparation is done via multiple stages:

            1. Initialise important attributes
                - self.num_cols: list[str]
                    A list containing the names of the numerical columns
                - self.cat_cols: list[str]
                    A list containing the names of the categorical columns
            2. Handle Categorical Features by either
                - Fit Categorical Encoder (mapping should be calculated over the whole data) or
                - Just drop all the categorical columns (if self.fit_categorical is not True)
        Returns
        -------
        None
        """

        self.cols = self.df.columns
        self.num_cols = self.df._get_numeric_data().columns
        self.cat_cols = list(set(self.cols) - set(self.num_cols))
        if self.fit_categorical:
            logger.info(f'Found the following Categorical Features: {self.cat_cols}')
            self.categorical_encoder.fit(self.df[self.cat_cols])
        else:
            self.df.drop(self.cat_cols, axis=1)

    def preprocess_data(self) -> pd.DataFrame:
        """Preprocess the raw data

        Preprocessing is done via multiple stages:

            1. Encode Categorical Features (Ordinal Encoding)
            2. Scale Numerical Data (Standard Normalization)
            3. Combine these two datasets (Concatenation)
            4. Apply PCA
                - retaining 99% variance explained
                - storing under self.untransformed_data

        Returns
        ---------
        pca_dataset: pd.Dataframe
            the final (post-PCA) dataframe
        """

        cat_features = pd.DataFrame(self.categorical_encoder.transform(self.df[self.cat_cols]), columns=self.cat_cols)
        num_features = pd.DataFrame(self.scaler.fit_transform(self.df.drop(self.cat_cols, axis=1).values), columns=self.num_cols)
        logger.info(f'{cat_features.shape}, {num_features.shape}')
        full_dataset = pd.concat([cat_features, num_features], axis=1)
        self.untransformed_data = full_dataset
        logger.debug(full_dataset.head(3))
        pca_dataset = self.transformer.fit_transform(full_dataset)
        logger.info(f'Initial Features where {self.df.shape[1]}. After PCA: {pca_dataset.shape[1]}')
        # pickle.dump(self.transformer, open("pca.pkl", "wb"))
        return pca_dataset

    def __call__(self) -> pd.DataFrame:
        """Make the Class as callable running the preprocessing"""
        return self.preprocess_data()

    def plot_heatmap(self) -> None:
        """Plot heatmap of Numerical Features (initial) correlation matrix"""

        corr = self.df.corr()
        plt.figure(figsize=(10, 10))

        sns.heatmap(corr, xticklabels=corr.columns.values, center=0,
                    yticklabels=corr.columns.values, mask=np.eye(len(corr)), square=True,
                    linewidths=.5, annot=True, cbar_kws={"shrink": .82}, cmap='Blues', fmt=".2%")

        plt.title('Heatmap of Correlation Matrix');

    def preprocess_inference(self, x_test: pd.DataFrame, categorical_mapping: Dict[str, Dict[str, int]],
                              numerical_mapping: Dict[str, Dict[str, float]], verbose=False) -> pd.DataFrame:
        """Pipeline for running during inference (test data)

        Inference Preprocessing is done via multiple stages:

            1. Hard copy the test data into X_test
            2. Validate feature consistency of X_test with fitted data
            3. Reuse stored categorical mappings to transform the categorical columns
            4. Reuse the statistics of the standard scaler to scale the numerical columns
            5. Apply learned PCA transformation to encoded_scaled dataset

        Parameters
        ----------
        x_test: pd.DataFrame
            the test dataset (or just any new data)
        categorical_mapping: dict
            keys are categorical feature names, values are
            dict[unique_value, encoded_integer] dictionaries
        numerical_mapping: dict
            keys are the numerical feature names, values are
            {'mean': float, 'std': float} Scaler's statistics
        verbose: bool
            indicator of prints as logs

        Returns
        -------
        X_test: pd.DataFrame
            the encoded, scaled and PCA applied (transformed) test dataset
        """

        X_test = x_test.copy()
        columns = x_test.columns
        logger.debug(f'Numerical Features: {set(numerical_mapping.keys())}')
        logger.debug(f'Categorical Features: {set(categorical_mapping.keys())}')
        given_features = set(categorical_mapping.keys()).union(set(numerical_mapping.keys()))
        if set(columns) != given_features:
            logger.error(f'Test Columns: {set(columns)} vs Trained on: {given_features}')
            raise ValueError('Inference and Train Data Mismatch (Columns)')

        for cat_column, mapping in categorical_mapping.items():
            x_test[cat_column] = x_test[cat_column].map(mapping)

        if verbose:
            print('Successfully Encoded Categorical Features')

        for num_column, stats in numerical_mapping.items():
            mean = float(stats['mean'])
            std = float(stats['std'])
            x_test[num_column] = (x_test[num_column] - mean) / std

        if verbose:
            print('Successfully Normalized Numerical Features')

        X_test = self.transformer.transform(X_test)
        return X_test

    def cat_encoder_to_dict(self) -> Dict[str, Dict[str, int]]:
        """Save Categorical Mapping into Dictionaries"""
        categorical_mapping = {}
        try:
            features = self.categorical_encoder.feature_names_in_
            categories = self.categorical_encoder.categories_
            for i, feature in enumerate(features):
                uniques = categories[i]
                mappings = list(range(len(uniques)))
                f_map = {uniques[j]: mappings[j] for j in range(len(uniques))}
                categorical_mapping[feature] = f_map
        except (AttributeError, KeyError) as encoder_was_not_used:
            logger.warning(f'Cannot save the Categorical Encoder (probably because not fitted! {encoder_was_not_used}')
        return categorical_mapping

    def num_encoder_to_dict(self) -> Dict[str, Dict[str, float]]:
        """Save Numerical Statistics into Dictionaries"""
        numerical_mapping = {}
        try:
            means = self.scaler.mean_
            stds = self.scaler.scale_
            for i, feature in enumerate(self.num_cols):
                std = stds[i]
                mean = means[i]
                f_map = {'mean': mean, 'std': std}
                numerical_mapping[feature] = f_map
        except (AttributeError, KeyError) as scaler_was_not_used:
            logger.warning(f'Cannot save the Numerical Scaler (probably because not fitted! {scaler_was_not_used}')
        return numerical_mapping

    @classmethod
    def from_request(cls, payload_dict: dict):
        """Class-method for comfortable initialisation (many __init__ params)"""
        data_proc_keys = set(DataProcessor.__dict__['__annotations__'].keys())
        keys_to_pass = data_proc_keys & set(payload_dict.keys())
        dict_to_feed = {i: j for i, j in payload_dict.items() if i in keys_to_pass}
        return cls(**dict_to_feed)
