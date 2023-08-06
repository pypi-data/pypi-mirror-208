import inspect
import json
import logging
import warnings
from collections import OrderedDict

import gorilla
import numpy as np
import tensorflow
from tensorflow.keras.callbacks import CSVLogger
from Accuinsight.modeler.core import func, path, get
from Accuinsight.modeler.core.func import get_time
from Accuinsight.modeler.core.LcConst import LcConst
from Accuinsight.modeler.core.LcConst.LcConst import RUN_NAME_TENSORFLOW, RUN_OBJ_NAME, RUN_MODEL_JSON_PATH, \
    RUN_MODEL_VISUAL_JSON_PATH,RUN_MODEL_EVL_JSON_PATH, RUN_MODEL_VISUAL_CSV_PATH, SELECTED_METRICS, USER_ID
from Accuinsight.modeler.core.Run.RunInfo.RunInfo import set_current_runs, clear_runs, set_model_json_path, \
    set_visual_csv_path, set_visual_json_path, set_best_model_json_path, set_best_model_h5_path, \
    set_python_dependencies, set_run_name, set_model_file_path, set_prefix_path, set_shap_json_path, set_evl_json_path, \
    set_optimizer_info_path, set_selected_metrics_path, set_model_type, set_true_y, set_predict_y
from Accuinsight.modeler.core.get_for_visual import roc_pr_curve, get_true_y, get_visual_info_regressor
from Accuinsight.modeler.clients.modeler_api import LifecycleRestApi
from Accuinsight.modeler.utils.dependency.dependencies import gather_sources_and_dependencies
from Accuinsight.modeler.utils.dl_utils import delete_files_except_best, get_best_model_path
from Accuinsight.modeler.utils.os_getenv import is_in_ipython, get_os_env
from Accuinsight.modeler.core.feature_contribution import shap_value
from Accuinsight.Lifecycle.common import Common
from Accuinsight.modeler.core import lossFuncInfo
from Accuinsight.modeler.core import modelEvaluation


logging.basicConfig(level=logging.INFO,
                    format='%(message)s')

warnings.filterwarnings("ignore")


class accuinsight(Common):
    def __init__(self):
        super().__init__()

    def get_file(self, storage_json_file_name=None):
        super().get_file(storage_json_file_name)

    @staticmethod
    def get_current_run_meta():
        global run_meta
        try:
            return run_meta
        except NameError:
            return None

    def get_current_run_id(self):
        try:
            return self.get_current_run_meta()[RUN_OBJ_NAME]
        except TypeError or KeyError:
            return None

    def model_evaluation(self, run_nickname_input=None, loaded_model=None, loaded_model_json=None, x_validation=None, y_validation=None, f1_average_in='weighted', recall_average_in='weighted'):
        start_evl = get_time.now()

        # get_file_path 실행 시 experiment 생성 시 필요한 폴더들이 다 만들어짐.
        # modeler backend 호출 시 파라미터로 경로 내 json 파일 내용을 protobuf 통해서 변환 후 gRPC로 전송을 위해 사용.
        self.dict_path = path.get_file_path(loaded_model, usedFramework='tensorflow')

        # dependencies를 가져오기 위한 작업
        if is_in_ipython():
            var_model_file_path = self.notebook_info
            _caller_globals = inspect.stack()[1][0].f_globals
            (
                mainfile,
                sources,
                dependencies
            ) = gather_sources_and_dependencies(
                globs=_caller_globals,
                save_git_info=False
            )
        else:
            _caller_globals = inspect.stack()[1][0].f_globals
            (
                mainfile,
                sources,
                dependencies
            ) = gather_sources_and_dependencies(
                globs=_caller_globals,
                save_git_info=True
            )
            var_model_file_path = mainfile['filename']

        if run_nickname_input is None:
            run_nick_name = self.default_run_nick_name
        else:
            run_nick_name = run_nickname_input


        if loaded_model is None or x_validation is None or y_validation is None or loaded_model_json is None:
            raise ValueError("Please set parameter -> model or validation data. ")
        x_val = x_validation
        y_val = y_validation

        # set current run
        set_current_runs(RUN_NAME_TENSORFLOW)

        # path for for-evl-json
        # visualCallback 참고 해서 actual data로 성능평가
        path_for_setting_evl_json = self.dict_path['evl_json']
        evl_json_full_path = self.dict_path[RUN_MODEL_EVL_JSON_PATH]
        set_evl_json_path(path_for_setting_evl_json)

        loaded_model_json_dict = json.loads(loaded_model_json)
        loss_function = loaded_model_json_dict['loss_function']
        run_id = loaded_model_json_dict['run_id']

        '''
        RunInfo.py 내 아래 데이터에 set
        global _runData
        run_obj = _runData[0]
        '''
        set_optimizer_info_path(loaded_model_json_dict['optimizer_info'])
        set_model_file_path(loaded_model_json_dict['path'])
        set_python_dependencies(py_depenpency=loaded_model_json_dict['model_dependencies'])
        set_prefix_path(self.dict_path[LcConst.RUN_PREFIX_PATH])
        set_run_name('tf.keras', run_id, run_nick_name)

        set_best_model_json_path(loaded_model_json_dict['best_model_json'])
        set_best_model_h5_path(loaded_model_json_dict['best_model_h5'])


        # 모델 라이브러리 확인 (tf or keras)
        if isinstance(loaded_model, tensorflow.keras.Model): #Sequential은 Model에서 상속 받아 같음.

            # print(loss_function)
            # print(self.dict_path[RUN_MODEL_EVL_JSON_PATH])

            # classification
            if loss_function in lossFuncInfo.CLASSIFICATION:
                print("DL_CLASSIFICATION in model_evaluation method")
                visual_classification_json = roc_pr_curve(loaded_model, x_val, y_val, f1_average=f1_average_in,
                                                          recall_average=recall_average_in)
                with open(evl_json_full_path, 'w', encoding='utf-8') as save_file:
                    json.dump(visual_classification_json, save_file, indent="\t")

                selected_metrics = modelEvaluation.calculate_classification_metrics(loaded_model, x_val, y_val, average=f1_average_in)
                set_model_type("DL_CLASSIFICATION")
            # regression
            elif loss_function in lossFuncInfo.REGRESSION:
                print("DL_REGRESSION in model_evaluation method")
                visual_regression_json = OrderedDict()
                visual_regression_json['True_y'] = get_true_y(y_val)
                visual_regression_json['Predicted_y'] = get_visual_info_regressor(loaded_model, x_val)

                set_true_y(visual_regression_json['True_y'])
                set_predict_y(visual_regression_json['Predicted_y'])

                with open(evl_json_full_path, 'w', encoding='utf-8') as save_file:
                    json.dump(visual_regression_json, save_file, indent="\t")

                selected_metrics = modelEvaluation.calculate_regression_metrics(loaded_model, x_val, y_val)
                set_model_type("DL_REGRESSION")

            else:
                raise ValueError('현재 설정한 모델은 지원되지 않습니다. 관리자에게 문의하십시오.')
        else: # keras 만을 사용한 경우 없음. 추후 pytorch 대응용
            pass
        loaded_model_json_dict[SELECTED_METRICS] = selected_metrics
        set_selected_metrics_path(loaded_model_json_dict[SELECTED_METRICS])

        end_evl = get_time.now()

        start_ts = int(start_evl.timestamp())
        end_ts = int(end_evl.timestamp())
        delta_ts = end_ts - start_ts

        run_meta = clear_runs(start_ts, end_ts, delta_ts, isEvaluation="true")

        env_value = get_os_env('ENV')
        modeler_rest = LifecycleRestApi(env_value[LcConst.BACK_END_API_URL],
                                        env_value[LcConst.BACK_END_API_PORT],
                                        env_value[LcConst.BACK_END_API_URI])
        modeler_rest.lc_create_run(run_meta)

    def autolog(self, run_nickname_input=None, tag=None, best_weights=False, model_monitor=False, runtime=False, f1_average_in='weighted', recall_average_in='weighted'):
        global description, endpoint, var_model_file_path, message, thresholds, best_weights_on, run_id, alarm, alarm_api, shap_on, feature_name, run_meta, run_nick_name
        description = tag
        endpoint = self.endpoint
        message = self.message # common.py send_message 호출을 통해 생성
        thresholds = self.thresholds
        alarm = self.workspace_alarm
        alarm_api = self.workspace_alarm_api
        user_id = self.user_id

        if f1_average_in not in ['micro', 'macro', 'weighted']:
            raise ValueError("f1_average_in set micro|macro|weighted")
        if recall_average_in not in ['micro', 'macro', 'weighted']:
            raise ValueError("recall_average_in set micro|macro|weighted")

        if run_nickname_input is None:
            run_nick_name = self.default_run_nick_name
        else:
            run_nick_name = run_nickname_input

        if best_weights:
            best_weights_on = True
        else:
            best_weights_on = False

        if model_monitor:
            shap_on = True
            if self.feature_name is None:
                try:
                    if self.data is not None:
                        feature_name = get.feature_name(self.save_path, self.StorageInfo, self.target_name,
                                                        data=self.data)
                        self.data = None
                    else:
                        feature_name = get.feature_name(self.save_path, self.StorageInfo, self.target_name)

                except:
                    pass      # when user did not use <get_file> or <set_feature> function
            else:
                feature_name = self.feature_name
        else:
            shap_on = False
        run_id = None
        run_meta = None

        if is_in_ipython():
            var_model_file_path = self.notebook_info
            _caller_globals = inspect.stack()[1][0].f_globals
            (
                mainfile,
                sources,
                dependencies
            ) = gather_sources_and_dependencies(
                globs=_caller_globals,
                save_git_info=False
            )
        else:
            _caller_globals = inspect.stack()[1][0].f_globals
            (
                mainfile,
                sources,
                dependencies
            ) = gather_sources_and_dependencies(
                globs=_caller_globals,
                save_git_info=True
            )
            var_model_file_path = mainfile['filename']

        class TrainHistoryCallbacks(tensorflow.keras.callbacks.Callback):
            def __init__(self, verbose=1, mode='auto'):
                super(TrainHistoryCallbacks, self).__init__()
                self.verbose = verbose
                self.best_epochs = 0
                self.epochs_since_last_save = 0
                self.mode = mode
                self.model_summary = OrderedDict()

            def on_train_begin(self, logs={}):
                logging.info('Using autolog(best_weights={}, model_monitor={}'
                             .format(str(best_weights_on), str(shap_on)))

                global start
                start = get_time.now()
                opt = self.model.optimizer.get_config()
                opt_key = list(opt.keys())[1:]
                opt_result = {k: np.float64(opt[k]) for k in opt_key}

                self.model_summary['data_version'] = endpoint
                self.model_summary['model_description'] = description
                self.model_summary['logging_time'] = get_time.logging_time()
                self.model_summary['run_id'] = func.get_run_id()
                self.model_summary['model_type'] = get.model_type(self.model)
                self.model_summary['run_nick_name'] = run_nick_name

                if user_id is not None:
                    self.model_summary[USER_ID] = user_id

                if hasattr(self.model.loss, 'get_config'):
                    self.model_summary['loss_function'] = self.model.loss.get_config()['name']
                else:
                    self.model_summary['loss_function'] = self.model.loss

                self.model_summary['optimizer_info'] = {opt['name']: opt_result}

                '''[get best model] on_train_begin '''
                self.best_weights = self.model.get_weights()

                self.dict_path = path.get_file_path(self.model, usedFramework='tensorflow')

                set_prefix_path(self.dict_path[LcConst.RUN_PREFIX_PATH])

                set_run_name(self.model_summary['model_type'], self.model_summary['run_id'], self.model_summary['run_nick_name'])
                set_python_dependencies(py_depenpency=dependencies)

            '''[get best model] on_epoch_end '''
            def on_epoch_end(self, epoch, logs=None):
                logs = logs or {}
                if epoch == 0:
                    if len(self.model.metrics_names) == 1 and 'loss' in self.model.metrics_names:
                        self.monitor = 'val_loss'
                    elif len(self.model.metrics_names) >= 2:
                        self.monitor = 'val_' + self.model.metrics_names[1]
                    # set monitoring option
                    if self.mode not in ['auto', 'min', 'max']:
                        warnings.warn('GetBest mode %s is unknown, '
                                      'fallback to auto mode.' % (self.mode), RuntimeWarning)
                        self.mode = 'auto'
                    if self.mode == 'min':
                        self.monitor_op = np.less
                        self.best = np.Inf
                    elif self.mode == 'max':
                        self.monitor_op = np.greater
                        self.best = -np.Inf
                    else:
                        if 'acc' in self.monitor or 'f1' in self.monitor:
                            self.monitor_op = np.greater
                            self.best = -np.Inf
                        else:
                            self.monitor_op = np.less
                            self.best = np.Inf
                else:
                    pass
                
                # Using best_weights
                if best_weights_on:

                    # update best_weights
                    self.epochs_since_last_save += 1
                    if self.epochs_since_last_save >= 1:
                        self.epochs_since_last_save = 0
                        current = logs.get(self.monitor)
                        if current is None:
                            warnings.warn('Can pick best model only with %s available, '
                                      'skipping.' % (self.monitor), RuntimeWarning)
                        else:
                            if self.monitor_op(current, self.best):
                                self.best = current
                                self.best_epochs = epoch + 1
                                self.best_weights = self.model.get_weights()
                            else:
                                pass

                    self.current_value = current

                # Not using best_weights
                else:
                    self.last_epoch_metric = logs.get(self.monitor)
                    self.best_epochs = epoch + 1
                    current = logs.get(self.monitor)
                    self.current_value = current

                # model save path
                run_id = self.model_summary['model_type'] + '-' + self.model_summary['run_id']
                common_path = self.dict_path['save_model_path'] + run_id + '-epoch-' + str(epoch + 1).zfill(5) + '-' + self.monitor + '-' + str(current).zfill(5)
                save_model_path = common_path + '.json'
                save_weights_path = common_path + '.h5'

                # model evaluation path(in jupyter lab browser path - 상대경로 의미...)
                browser_common_path = self.dict_path['save_model_dir'] + '/' + run_id + '-epoch-' + str(epoch + 1).zfill(
                    5) + '-' + self.monitor + '-' + str(current).zfill(5)
                save_model_path_browser = browser_common_path + '.json'
                save_weights_path_browser = browser_common_path + '.h5'

                # model to JSON
                model_json = self.model.to_json()

                # model 정보에 loss 추가
                model_dict = json.loads(model_json)
                model_dict['loss_function'] = self.model_summary['loss_function']
                model_dict['run_id'] = self.model_summary['run_id']
                model_dict['path'] = var_model_file_path
                model_dict['model_dependencies'] = dependencies
                model_dict['best_model_h5'] = save_weights_path_browser
                model_dict['best_model_json'] = save_model_path_browser
                model_dict['optimizer_info'] = self.model_summary['optimizer_info']
                if best_weights_on:
                    model_dict[SELECTED_METRICS] = {self.monitor: np.float64(self.best)}
                else:
                    model_dict[SELECTED_METRICS] = {self.monitor: np.float64(self.last_epoch_metric)}

                updated_model_json = json.dumps(model_dict)

                with open(save_model_path, "w") as json_file:
                    json_file.write(updated_model_json)

                # weights to H5
                # self.model.save_weights(save_weights_path)
                self.model.save(save_weights_path)

            def on_train_end(self, logs={}):
                '''[get best model] on_train_end '''
                if best_weights_on:
                    if self.verbose > 0:
                        print('\nUsing epoch %05d with %s: %0.5f' % (self.best_epochs, self.monitor, self.best))
                    self.model.set_weights(self.best_weights)  # set best model's weights
                    
                    self.model_summary[SELECTED_METRICS] = {self.monitor: np.float64(self.best)}
                else:
                    self.model_summary[SELECTED_METRICS] = {self.monitor: np.float64(self.last_epoch_metric)}
    
          #      print('model_summary: ', self.model_summary)   ##############################
                end = get_time.now()
                self.model_summary['time_delta'] = str(end - start)

                # path for model_info.json
                self.path_for_setting_model_json = self.dict_path['model_json']
                set_model_json_path(self.path_for_setting_model_json)

                model_json_full_path = self.dict_path[RUN_MODEL_JSON_PATH]

                with open(model_json_full_path, 'w', encoding='utf-8') as save_file:
                    json.dump(self.model_summary, save_file, indent="\t")

                delete_files_except_best(run_id=self.model_summary['run_id'], epochs=str(self.best_epochs),
                                         path=self.dict_path)

                path_for_setting_model_json = self.dict_path['save_model_dir'] + \
                                              get_best_model_path(run_id=self.model_summary['run_id'],
                                                                  path=self.dict_path)['json']
                path_for_setting_model_h5 = self.dict_path['save_model_dir'] + \
                                            get_best_model_path(run_id=self.model_summary['run_id'],
                                                                path=self.dict_path)['h5']
                set_best_model_json_path(path_for_setting_model_json)
                set_best_model_h5_path(path_for_setting_model_h5)

                start_ts = int(start.timestamp())
                end_ts = int(end.timestamp())
                delta_ts = end_ts - start_ts

                global run_meta
                run_meta = clear_runs(start_ts, end_ts, delta_ts)
                accuinsight._send_message(metric=self.monitor,
                                          current_value=self.current_value,
                                          message=message,
                                          alarm_object=alarm,
                                          alarm_api=alarm_api)
                env_value = get_os_env('ENV')
                modeler_rest = LifecycleRestApi(env_value[LcConst.BACK_END_API_URL],
                                                env_value[LcConst.BACK_END_API_PORT],
                                                env_value[LcConst.BACK_END_API_URI])
                modeler_rest.lc_create_run(run_meta)
                if runtime:
                    accuinsight.set_runtime_model('tensorflow')
                accuinsight._off_autolog()

        class visualCallbacks(tensorflow.keras.callbacks.Callback):
            def __init__(self, x_validation=None, y_validation=None):
                super(visualCallbacks, self).__init__()
                self.x_val = x_validation
                self.y_val = y_validation

            def on_train_end(self, logs={}):
                self.dict_path = path.get_file_path(self.model, usedFramework='tensorflow')
                # path for visual.json
                path_for_setting_visual_json = self.dict_path['visual_json']
                visual_json_full_path = self.dict_path[RUN_MODEL_VISUAL_JSON_PATH]
                set_visual_json_path(path_for_setting_visual_json)

                # classification
                if get.is_classification(self.model):
                    visual_classification_json = roc_pr_curve(self.model, self.x_val, self.y_val, f1_average=f1_average_in, recall_average=recall_average_in)

                    with open(visual_json_full_path, 'w', encoding='utf-8') as save_file:
                        json.dump(visual_classification_json, save_file, indent="\t")

                # regression
                else:
                    visual_regression_json = OrderedDict()
                    visual_regression_json['True_y'] = get_true_y(self.y_val)
                    visual_regression_json['Predicted_y'] = get_visual_info_regressor(self.model, self.x_val)

                    with open(visual_json_full_path, 'w', encoding='utf-8') as save_file:
                        json.dump(visual_regression_json, save_file, indent="\t")

        class shapCallbacks(tensorflow.keras.callbacks.Callback):
            def __init__(self, trainX, feature_name, run_id, trigger=shap_on):
                super(shapCallbacks, self).__init__()
                self.trainX = trainX
                self.trigger = trigger
                self.run_id = run_id
                self.feature_name_in_shap = feature_name

            def on_train_end(self, logs={}):
                if self.trigger:
                    self.shap_value = shap_value(self.model, self.trainX, self.feature_name_in_shap)
                    
#                     func.insertDB(self.shap_value, 2)  # 수정: 2 -> self.run_id
                    
                    self.dict_path = path.get_file_path(self.model, usedFramework='tensorflow')

                    # path for shap.json
                    shap_json_full_path = self.dict_path['shap_json_full']
                    set_shap_json_path(self.dict_path['shap_json'])

                    with open(shap_json_full_path, 'w', encoding='utf-8') as save_file:
                        json.dump(self.shap_value, save_file, indent='\t')

                else:
                    pass

        def run_and_log_function(self, original, x, y, kwargs):
            dict_path = path.get_file_path(self, usedFramework='tensorflow')
            path_for_setting_visual_csv = dict_path['visual_csv']
            visual_csv_full_path = dict_path[RUN_MODEL_VISUAL_CSV_PATH]

            # set current run
            set_current_runs(RUN_NAME_TENSORFLOW)
            set_model_file_path(var_model_file_path)
            set_visual_csv_path(path_for_setting_visual_csv)

            csv_logger = CSVLogger(visual_csv_full_path, append=True, separator=';')

            # get train data(x) for computing shap value
            if 'x':
                x_train = x
            if shap_on:
                get_shap = shapCallbacks(x_train, feature_name, run_id, trigger=shap_on)
            else:
                pass

            ''' save json for visualization '''
            # using validation_data argument
            if 'validation_data' in kwargs:
                validation_set = kwargs['validation_data']

                try:
                    x_val = validation_set[0]
                    y_val = validation_set[1]

                except:
                    iterator = iter(validation_set)
                    valid_set = next(iterator)
                    x_val = valid_set[0].numpy()
                    y_val = valid_set[1].numpy()

                get_visual = visualCallbacks(x_validation=x_val, y_validation=y_val)

            else:
                raise ValueError('"validation_data" does not exist.')

            if 'callbacks' in kwargs:
                kwargs['callbacks'] += [csv_logger]
            else:
                kwargs['callbacks'] = [csv_logger]

            kwargs['callbacks'] += [get_visual]
            if shap_on:
                kwargs['callbacks'] += [get_shap]
            else:
                pass
            kwargs['callbacks'] += [TrainHistoryCallbacks()]

            return original(self, x, y, **kwargs)

        @gorilla.patch(tensorflow.keras.Model)
        def fit(self, x, y, **kwargs):
            original = gorilla.get_original_attribute(tensorflow.keras.Model, 'fit')
            unlogged_params = ['self', 'callbacks', 'validation_data', 'verbose']
            return run_and_log_function(self, original, x, y, kwargs)

        settings = gorilla.Settings(allow_hit=True, store_hit=True)
        gorilla.apply(gorilla.Patch(tensorflow.keras.Model, 'fit', fit, settings=settings))

    def _off_autolog():
        def stop_log(self, original, args, kwargs, unlogged_params):
            return original(self, *args, **kwargs)

        @gorilla.patch(tensorflow.keras.Model)
        def fit(self, *args, **kwargs):
            original = gorilla.get_original_attribute(tensorflow.keras.Model, 'fit')
            unlogged_params = ['self', 'x', 'y', 'callbacks', 'validation_data', 'verbose']
            return stop_log(self, original, args, kwargs, unlogged_params)

        settings = gorilla.Settings(allow_hit=True, store_hit=True)
        gorilla.apply(gorilla.Patch(tensorflow.keras.Model, 'fit', fit, settings=settings))
