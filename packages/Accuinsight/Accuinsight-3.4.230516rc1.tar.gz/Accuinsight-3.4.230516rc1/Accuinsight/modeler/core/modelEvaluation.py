from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import numpy as np

from Accuinsight.modeler.core.get_for_visual import y_pred_reshape, y_test_reshape


def calculate_regression_metrics(model, x_val, y_true):
    y_pred = model.predict(x_val)

    metrics = {
        'mae': mean_absolute_error(y_true, y_pred),
        'mse': mean_squared_error(y_true, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
        'r2score': r2_score(y_true, y_pred),
        'mape': mean_absolute_percentage_error(y_true, y_pred),
    }

    return metrics


def calculate_classification_metrics(model, x_val, y_true, average=None):
    y_pred = y_pred_reshape(model, x_val)
    y_true = y_test_reshape(y_true)

    print("y_true shape:", y_true.shape)
    print("y_pred shape:", y_pred.shape)
    result = {
        "y_true": y_true,
        "y_pred": y_pred
    }

    print(result)
    if len(np.unique(y_true)) > 2:
        # 다중 클래스 분류
        print("다중 클래스")
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average=average)
        recall = recall_score(y_true, y_pred, average=average)
        f1score = f1_score(y_true, y_pred, average=average)
    else:
        # 이진 분류
        print("이진 클래스")
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average=average, pos_label=1)
        recall = recall_score(y_true, y_pred, average=average, pos_label=1)
        f1score = f1_score(y_true, y_pred, average=average, pos_label=1)

    metrics = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1score': f1score
    }

    return metrics