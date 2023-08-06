import json
from Accuinsight.modeler.core.LcConst.LcConst import RUN_RESULT_PATH, RUN_MODEL_JSON_PATH
from Accuinsight.modeler.core.LcConst.LcConst import ALL_MODEL_PARAMS, SELECTED_METRICS, SELECTED_PARAMS
from Accuinsight.modeler.protos.life_cycle_pb2 import LcParam, LcMetric
from Accuinsight.modeler.core.Run.ParseRun import ParserVisualJaon, Parse_Helper

def _makeLcParam(selected_params, all_model_params):
    grpc_params = []

    for param_key in selected_params:

        param = LcParam(
            key=param_key,
            value=str(all_model_params[param_key])
        )
        grpc_params.append(param)
    return grpc_params


# parse parameters
def parse_run_parameters(json_data):
    # read ~/runs/results-XGBClassifier/model-info-json/*.json
    # return parameters

    param_data = json_data
    selected_params = param_data[SELECTED_PARAMS]
    all_model_params = param_data[ALL_MODEL_PARAMS]

    grpc_params = _makeLcParam(selected_params=selected_params, all_model_params=all_model_params)

    return grpc_params


# parse metrics
def parse_run_metrics(json_data):
    # read ~/runs/results-XGBClassifier/model-info-json/*.json
    # get "selected_metrics" field
    # return metrics

    metric_data = json_data
    grpc_metrics = []

    # selected_metrics
    selected_metrics = metric_data[SELECTED_METRICS]
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

def parse_run_result(run_info_json):
    result_dict = {'metrics': '', 'params': ''}

    grpc_params = parse_run_parameters(json_data=run_info_json)
    grpc_metrics = parse_run_metrics(json_data=run_info_json)

    grpc_visuals = ParserVisualJaon.parse_run_visual(run_mata=run_info_json)
    result_dict['params'] = grpc_params
    result_dict['metrics'] = grpc_metrics
    result_dict['visual'] = grpc_visuals

    return result_dict