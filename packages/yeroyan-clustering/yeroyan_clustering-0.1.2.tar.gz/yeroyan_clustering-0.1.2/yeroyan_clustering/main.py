"""Main module."""
import warnings
import matplotlib.pyplot as plt

from yeroyan_clustering.utils import visualise_feature_level,  post_analysis
from yeroyan_clustering.modeling import SuperKmeans
from yeroyan_clustering.processing import DataProcessor, SuperTSNE


def get_data_object(data_path: str):
    """DataProcessor preparation running function (to then use in tests)

    Parameters
    ----------
    data_path: str :
        path to raw .csv

    Returns
    -------
    data_object_: DataProcessor
        DataProcessor instance
    """
    data_object_ = DataProcessor(data_path=data_path)
    return data_object_


def get_preprocessed_data(data_object_: DataProcessor):
    """DataProcessor pipeline running function (to then use in tests)

    Parameters
    ----------
    data_object_: DataProcessor :
        DataProcessor instance that has run its .preprocess() method

    Returns
    -------
    processed_: dataframe
        the final (post-PCA) dataframe
    """
    processed_ = data_object.preprocess_data()
    return processed_


if __name__ == '__main__':

    warnings.filterwarnings('ignore')
    data_path = 'data/telco.csv'
    data_object = get_data_object(data_path)
    print(data_object.df.shape, data_object.df.columns.tolist())
    print(data_object.df.head())

    data_object.plot_heatmap()
    plt.show();

    processed_data = get_preprocessed_data(data_object)  # standardize, encode categorical, apply pca
    encoded_scaled = data_object.untransformed_data  # # prior to pca
    print(encoded_scaled.head())

    visualiser = SuperTSNE()
    visualise_feature_level(data_object, processed_data, visualiser, 'internet', 3)

    clf = SuperKmeans()
    clf.choose_k(processed_data);

    clf.fit(processed_data, 3)
    pred_labels = clf.predict(processed_data)
    visualise_feature_level(data_object, processed_data, visualiser, pred_labels, 2)

    full_data, num, cat = post_analysis(data_object, pred_labels, stats='mean')
    full_data.head(4)
