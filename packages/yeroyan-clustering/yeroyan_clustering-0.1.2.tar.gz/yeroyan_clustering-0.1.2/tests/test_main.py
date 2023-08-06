#!/usr/bin/env python

"""Tests for `yeroyan_clustering` package."""

import pytest


from yeroyan_clustering.main import get_data_object, get_preprocessed_data


def test_get_data_object():
    """Test DataProcessor Preparation"""
    obj = get_data_object('yeroyan_clustering/data/telco.csv')
    assert obj.df.shape == (1000, 15)
    assert obj.df.columns.tolist() == ['ID', 'region', 'tenure', 'age', 'marital', 'address', 'income',
                                       'ed', 'retire', 'gender', 'voice', 'internet', 'forward',
                                       'custcat', 'churn']


def test_get_preprocessed_data():
    """Test DataProcessor Processing"""
    obj = get_data_object('yeroyan_clustering/data/telco.csv')
    processed = obj.preprocess_data()
    # inplace calculations
    assert obj.num_cols.__len__() == 5
    assert obj.cat_cols.__len__() == 10
    # return validation
    assert processed.shape == (1000, 13)
