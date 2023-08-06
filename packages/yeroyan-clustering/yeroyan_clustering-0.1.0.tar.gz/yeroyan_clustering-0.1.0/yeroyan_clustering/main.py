"""Main module."""
import warnings
import matplotlib.pyplot as plt


if __name__ == '__main__':
    from utils import visualise_feature_level,  post_analysis
    from yeroyan_clustering.modeling import SuperKmeans
    from yeroyan_clustering.processing import DataProcessor, SuperTSNE

    warnings.filterwarnings('ignore')
    data_path = 'data/telco.csv'
    data_object = DataProcessor(data_path=data_path)
    print(data_object.df.head())

    data_object.plot_heatmap()
    plt.show();

    processed_data = data_object.preprocess_data()  # standardize, encode categorical, apply pca
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
