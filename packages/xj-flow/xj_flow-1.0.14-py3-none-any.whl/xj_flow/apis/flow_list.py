# _*_coding:utf-8_*_

from rest_framework.views import APIView

from ..services.flow_basic_service import FlowBasicService
from ..utils.custom_response import util_response
from ..utils.custom_tool import flow_service_wrapper
from ..utils.request_params_wrapper import request_params_wrapper
from ..utils.user_wrapper import user_authentication_wrapper


class FlowList(APIView):

    @request_params_wrapper
    @user_authentication_wrapper
    @flow_service_wrapper
    def get(self, *args, request_params=None, **kwargs):
        """
        流程作业
        """
        # print("FlowList: request_params:", request_params)
        category_id = request_params.get('category_id', None)
        flow_name = request_params.get('flow_name', None)
        flow_list, error_text = FlowBasicService.get_flow_list(category_id=category_id, flow_name=flow_name)

        return util_response(data=flow_list)
