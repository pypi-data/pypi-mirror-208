from collections.abc import Mapping
from csv import DictReader
import json
from Accuinsight.modeler.core.LcConst.LcConst import RUN_RESULT_PATH, RUN_MODEL_VISUAL_CSV_PATH, \
    RUN_MODEL_VISUAL_JSON_PATH, RUN_MODEL_JSON_PATH, SELECTED_METRICS, RUN_OBJ_OPT_INFO
from Accuinsight.modeler.protos.life_cycle_pb2 import LcMetric, LcParam
from Accuinsight.modeler.core.Run.ParseRun import Parse_Helper

def _append_metrics(metrics, **kwargs):
    values = []
    timestamp = []
    steps = []
    count = 0
    data = kwargs['data']
    key = kwargs['key']

    for v in data:
        values.append(str(v))
        timestamp.append(str(count))
        steps.append(str(count))
        count += 1
    metrics.append({'key': key,
                    'values': values,
                    'timestamp': timestamp,
                    'steps': steps})
    return metrics

def _parse_true_predict(metrics, run_meta):
    param_data = run_meta
    true_y = []
    predicted_y = []
    true_y_values = param_data['True_y']
    predicted_y_values = param_data['Predicted_y']

    # check if nested list
    is_nested_true = any(isinstance(elem, list) for elem in true_y_values)
    is_nested_predicted = any(isinstance(elem, list) for elem in predicted_y_values)

    if is_nested_true:
        for elem in true_y_values:
            true_y.append(elem[0])
    else:
        true_y = true_y_values

    if is_nested_predicted:
        for elem in predicted_y_values:
            predicted_y.append(elem[0])
    else:
        predicted_y = predicted_y_values

    metrics = _append_metrics(metrics, data=true_y, key='true_y')
    metrics = _append_metrics(metrics, data=predicted_y, key='predicted_y')
    return metrics


# parse metrics
def _parse_selected_metrics(run_meta):
    # read ~/runs/results-XGBClassifier/model-info-json/*.json
    # get "selected_metrics" field
    # return metrics

    grpc_metrics = []

    # selected_metrics
    selected_metrics = run_meta[SELECTED_METRICS]
    metric_keys = selected_metrics.keys()

    result_dict = {'metrics': []}

    count = 0
    timestamp = []
    steps = []
    values = []
    for key in metric_keys:
        values.append(str(selected_metrics[key]))
        timestamp.append(str(count))
        steps.append(key)
        count += 1

    result_dict['metrics'].append({
                                   'values': values,
                                   'timestamp': timestamp,
                                   'steps': steps})

    metrics = result_dict['metrics']

    for item in metrics:
        metric = LcMetric(
                key=SELECTED_METRICS,
                values=item['values'],
                timestamp=item['timestamp'],
                steps=item['steps']
            )
        grpc_metrics.append(metric)

    return grpc_metrics


def parse_metric(run_meta):
    metrics = []
    metrics = _parse_true_predict(metrics, run_meta)

    grpc_metrics = []

    for item in metrics:
        metric = LcMetric(
                key=item['key'],
                values=item['values'],
                timestamp=item['timestamp'],
                steps=item['steps']
            )
        grpc_metrics.append(metric)

    selected_metrics = _parse_selected_metrics(run_meta=run_meta)
    grpc_metrics = grpc_metrics + selected_metrics
    return grpc_metrics


def _parse_optimizer_info(param_data):
    grpc_params = []

    optimizer_info = param_data
    if isinstance(optimizer_info, Mapping):
        for k, v in optimizer_info.items():
            optimizer = LcParam(
                key='type_of_optimizer',
                value=str(k)
            )
            grpc_params.append(optimizer)
            if isinstance(v, Mapping):
                for k, v in v.items():
                    param = LcParam(
                        key=k,
                        value=str(v)
                    )
                    grpc_params.append(param)
    return grpc_params


def parse_parameter(run_meta):
    param_data = run_meta[RUN_OBJ_OPT_INFO]
    dummy_data = {
        'model_description': 'keras test',
        'logging_time': '2020-05-06 10:30:50',
        'run_id': '9FCEF776-D830-4353-8961-144491DC03CC',
        'model_type': 'keras_nn',
        'optimizer_info': {
            'RMSprop': {
                'learning_rate': 9.999999747378752e-05,
                'rho': 0.8999999761581421,
                'decay': 0.0,
                'epsilon': 1e-07
            }
        },
        'time_delta': '0:00:14.912202'
    }

    return _parse_optimizer_info(param_data)


def parse_run_result(run_info_json):
    result_dict = {'metrics': None, 'params': None, 'visual': None}

    metric_evl_data = parse_metric(run_meta=run_info_json)
    parameter_evl_data = parse_parameter(run_meta=run_info_json)

    result_dict['params'] = parameter_evl_data
    result_dict['metrics'] = metric_evl_data
    return result_dict

