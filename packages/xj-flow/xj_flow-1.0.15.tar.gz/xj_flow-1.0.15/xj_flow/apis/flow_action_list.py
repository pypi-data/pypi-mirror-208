# _*_coding:utf-8_*_

from rest_framework.views import APIView

from ..services.flow_basic_service import FlowBasicService
from ..utils.custom_response import util_response
from ..utils.request_params_wrapper import request_params_wrapper


class FlowActionList(APIView):
    def __init__(self, *args, **kwargs):
        # 初始化操作
        super().__init__(*args, **kwargs)

    @request_params_wrapper
    def get(self, request, request_params=None):
        """
        流程作业
        """
        if request_params is None:
            request_params = {}
        # 获取数据
        flow_action_list, error_text = FlowBasicService.get_flow_action_list(search_params=request_params)
        # 响应数据
        return util_response(data=flow_action_list)
