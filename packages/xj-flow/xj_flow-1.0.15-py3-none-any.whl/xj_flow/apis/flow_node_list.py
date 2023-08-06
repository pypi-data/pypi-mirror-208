# _*_coding:utf-8_*_

from rest_framework.views import APIView

from ..services.flow_basic_service import FlowBasicService
from ..utils.custom_response import util_response
from ..utils.request_params_wrapper import request_params_wrapper


class FlowNodeList(APIView):
    @request_params_wrapper
    def get(self, request, request_params=None):
        """
        流程作业
        """
        flow_list, error_text = FlowBasicService.get_flow_node_list(params=request_params)

        return util_response(data=flow_list)
