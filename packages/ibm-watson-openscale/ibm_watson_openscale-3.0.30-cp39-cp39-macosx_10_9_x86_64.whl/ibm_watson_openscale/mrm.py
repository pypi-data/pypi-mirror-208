# coding: utf-8

# Copyright 2022 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ibm_watson_openscale.base_classes.watson_open_scale_v2 import ModelRiskManagement as BaseModelRiskManagement, IntegratedSystemMetricsArray, IntegratedMetric
from ibm_cloud_sdk_core import BaseService
from .utils import *
from typing import TextIO

if TYPE_CHECKING:
    from .client import WatsonOpenScaleV2Adapter
    from ibm_watson_openscale.base_classes.watson_open_scale_v2 import DetailedResponse

class ModelRiskManagement(BaseModelRiskManagement):
    """Manage model risk management monitoring for asset."""

    def __init__(self, ai_client: 'WatsonOpenScaleV2Adapter') -> None:
        validate_type(ai_client, 'ai_client', BaseService, True)
        self._ai_client = ai_client
        super().__init__(watson_open_scale=self._ai_client)

    def evaluate_risk(self,
        monitor_instance_id: str,
        test_data_set_name: str = None,
        feedback_data_path: str = None,
        publish_metrics: str = None,
        publish_lineage: str = None,
        publish_fact: str = None,
        includes_model_output: str = None,
        evaluation_tests: str = None,
        **kwargs
        ) -> 'DetailedResponse':

        validate_type(monitor_instance_id, 'monitor_instance_id', str, True)

        feedback_data_content = None
        if feedback_data_path:
            feedback_data_content = open(feedback_data_path, 'rb')

        content_type = "text/csv"
        response = self.mrm_risk_evaluations(
        monitor_instance_id = monitor_instance_id,
        unknown_base_type =  feedback_data_content,
        content_type = content_type,
        test_data_set_name =  test_data_set_name,
        publish_metrics = publish_metrics,
        publish_lineage = publish_lineage,
        publish_fact = publish_fact,
        includes_model_output = includes_model_output,
        evaluation_tests = evaluation_tests,
        **kwargs)

        return response

    def get_risk_evaluation(self,
        monitor_instance_id: str,
        **kwargs) -> 'DetailedResponse':

        validate_type(monitor_instance_id, 'monitor_instance_id', str, True)

        response = self.mrm_get_risk_evaluation(
        monitor_instance_id = monitor_instance_id,
        **kwargs)

        return response

    def cancel_risk_evaluation(self,
        monitor_instance_id: str,
        cancel_run: str = None,
        **kwargs
        ) -> 'DetailedResponse':

        validate_type(monitor_instance_id, 'monitor_instance_id', str, True)

        response = self.mrm_put_risk_evaluation(
        monitor_instance_id = monitor_instance_id,
        cancel_run = cancel_run,
        **kwargs)

        return response

    def update_notification_preferences(self,
        monitor_instance_id: str,
        notification_enabled: bool,
        notification_frequency: str,
        notification_emails: List[str],
        **kwargs) -> 'DetailedResponse':

        validate_type(monitor_instance_id, 'monitor_instance_id', str, True)

        response = self.mrm_update_notification_preferences(monitor_instance_id = monitor_instance_id,
        notification_enabled = notification_enabled,
        notification_frequency = notification_frequency,
        notification_emails = notification_emails,
        **kwargs)

        return response

    def get_notification_preferences(self,
         monitor_instance_id: str,
        **kwargs) -> 'DetailedResponse':

        validate_type(monitor_instance_id, 'monitor_instance_id', str, True)

        response = self.mrm_get_notification_preferences(monitor_instance_id = monitor_instance_id,
        **kwargs)

        return response

    def publish_metrics(self,
        monitor_instance_id: str,
        monitoring_run_id: str,
        metrics_info: dict = None,
        **kwargs
    ) -> 'DetailedResponse':

        validate_type(monitor_instance_id, 'monitor_instance_id', str, True)
        validate_type(monitoring_run_id, 'monitoring_run_id', str, True)

        metrics_array = []
        send_report = get(metrics_info, "send_report")
        metrics_list = get(metrics_info, "metrics")
        for metrics in metrics_list:
            type = get(metrics, "type")
            measures = get(metrics, "measures")
            integrated_metrics_list = []
            integrated_metrics = get(metrics, "integrated_metrics")
            if integrated_metrics != None:
                for integrated_metric in integrated_metrics:
                    integrated_system_type = get(integrated_metric, "integrated_system_type")
                    mapped_metrics = get(integrated_metric, "mapped_metrics")
                    integrated_metric_obj = IntegratedMetric(
                        integrated_system_type = integrated_system_type,
                        mapped_metrics = mapped_metrics
                    )
                    integrated_metrics_list.append(integrated_metric_obj)

            metrics_array_object = IntegratedSystemMetricsArray(
                type = type,
                measures = measures,
                integrated_metrics = integrated_metrics_list
            )
        metrics_array.append(metrics_array_object)

        response = self.mrm_publish_metrics(
        monitor_instance_id = monitor_instance_id,
        monitoring_run_id = monitoring_run_id,
        metrics = metrics_array,
        send_report = send_report,
        **kwargs
        )

        return response

    def get_risk_evaluation_status(self,
        data_mart_id: str = None,
        **kwargs
    ) -> 'DetailedResponse':

        response = self.mrm_get_risk_evaluation_status(
            data_mart_id = data_mart_id,
            **kwargs
        )

        return response

    def update_risk_evaluation_status(self,
        subscription_id: str,
        state: str = None,
        **kwargs
    ) -> 'DetailedResponse':

        validate_type(subscription_id, 'subscription_id', str, True)
    
        response = self.mrm_update_risk_evaluation_status(
            subscription_id = subscription_id,
            state = state,
            **kwargs
        )

        return response

    def mrm_download_pdf_report(self,
        monitor_instance_id: str,
        monitoring_run_id: str,
        file_name: str = None,
        **kwargs
    ) -> 'None':

        validate_type(monitor_instance_id, 'monitor_instance_id', str, True)
        validate_type(monitoring_run_id, 'monitoring_run_id', str, True)

        if file_name == None:
            file_name = "mrm_evaluation_report.pdf"

        response = self.mrm_download_report(
            monitor_instance_id = monitor_instance_id,
            monitoring_run_id = monitoring_run_id,
            **kwargs
        )

        if response.status_code != 200:
            print("Failed downloading report - Status : " + str(response.status_code))
        else:
            try:
                with open(file_name, "xb") as file:
                    file.write(response.result.content)
                    print("MRM evaluation report " + file_name + " download successfully !")
            except IOError as e:
                print("Could not create file:" + file_name, ". Please specify another file name and try again..")
                print("I/O error({0}): {1}".format(e.errno, e.strerror))
