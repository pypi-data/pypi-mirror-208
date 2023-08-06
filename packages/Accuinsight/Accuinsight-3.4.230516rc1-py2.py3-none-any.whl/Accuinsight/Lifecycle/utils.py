import logging
import re
import os
import json

logging.basicConfig(level=logging.DEBUG)


class AbcNotifier:
    def completed_message(self, **kwargs):
        pass


def load_model(run_name):
    best_model_path_dict = dict()

    model_type = run_name.split('-')[0]
    t = run_name.split('-')[1].split('_')[0]
    filename = model_type + '-' + t[0:8] + '-' + t[8:12] + '-' + t[12:16] + '-' + t[16:20] + '-' +  t[20:]
    regex = re.compile(filename)

    common_path = '/home/work/runs/best-model'

    for subdir, dirs, files in os.walk(common_path):
        dirs[:] = []  # 하위 디렉토리를 탐색하지 않도록 dirs 리스트를 비움
        for filename in files:
            if regex.search(filename):
                if filename.endswith(".joblib"):
                    best_model_path_dict['joblib'] = os.path.join(common_path, filename)
                elif filename.endswith(".json"):
                    best_model_path_dict['json'] = os.path.join(common_path, filename)
                elif filename.endswith(".h5"):
                    best_model_path_dict['h5'] = os.path.join(common_path, filename)

    # load model trained using keras
    if model_type == 'keras':
        from keras.models import model_from_json
        # load json and create model
        json_file = open(best_model_path_dict['json'], 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)

        # load weights into new model
        # loaded_model.load_weights(best_model_path_dict['h5'])
        loaded_model.load_model(best_model_path_dict['h5'])

    # load model trained using tensorflow
    elif model_type == 'tf.keras':
        from tensorflow.keras.models import model_from_json
        # load json and create model
        json_file = open(best_model_path_dict['json'], 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)

        # load weights into new model
        loaded_model.load_weights(best_model_path_dict['h5'])
        # loaded_model.load_model(best_model_path_dict['h5'])

    else:
        import joblib
        json_file = open(best_model_path_dict['json'], 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = joblib.load(best_model_path_dict['joblib'])

    # 파라미터 추가
    # 실제로 experiment 모델을 생성하는 것이 아니라 평가해서 모델러 백엔드로 동일 모델에 대한 평가를 식별하기 위해 추가.
    loaded_model_dict = json.loads(loaded_model_json)

    loaded_model_dict["run_name"] = run_name
    update_loaded_model_json = json.dumps(loaded_model_dict)

    return loaded_model, update_loaded_model_json
