# _*_coding:utf-8_*_

from rest_framework.views import APIView

from xj_user.utils.user_wrapper import user_authentication_force_wrapper
from ..services.flow_process_service import FlowProcessService
from ..utils.custom_response import util_response
from ..utils.request_params_wrapper import request_params_wrapper


class FlowProcess(APIView):

    def __init__(self, *args, **kwargs):
        self.flow_process_service = FlowProcessService()
        super().__init__(*args, **kwargs)

    @request_params_wrapper
    @user_authentication_force_wrapper
    def post(self, request, request_params=None, *args, user_info=None, **kwargs):
        """
        流程作业
        """
        flow_node_id = request_params.pop("flow_node_id", None)
        flow_action_id = request_params.pop("flow_action_id", None)
        flow_node_value = request_params.pop("flow_node_value", None)
        flow_action_value = request_params.pop("flow_action_value", None)
        if (not flow_node_id and not flow_node_value) or (not flow_action_id and not flow_action_value):
            return util_response(err=1001, msg='flow_node_id 必填')
        # 抵用流程
        data, error_text = self.flow_process_service.do_once_flow_in_service(
            flow_node_id=flow_node_id,
            flow_action_id=flow_action_id,
            flow_node_value=flow_node_value,
            flow_action_value=flow_action_value,
            source_params=request_params
        )

        # 保存记录,执行请求返回结果解析出来
        run_flow_record_params = {

        }

        # 记录流程的操作
        record_data, record_err = self.flow_process_service.save_record(result_dict=run_flow_record_params, user_info=user_info)
        if record_err:
            return util_response(err=1000, msg=error_text)
        if error_text:
            return util_response(err=1001, msg=error_text)
        return util_response(data=data)
