from django.db.models import F

from ..models import Flow, FlowNode, FlowAction, FlowNodeToAction, FlowNodeActionRule, FlowActionToOperator
from ..utils.custom_tool import format_params_handle, filter_result_field


class FlowBasicService:

    @staticmethod
    def get_flow_list(category_id=None, flow_name=None):
        """
        获取流程列表
        @param category_id 类别ID
        @param flow_name 流程名称
        """

        flow_set = Flow.objects.all()
        if category_id:
            flow_set = flow_set.filter(category_id=category_id)
        if flow_name:
            flow_set = flow_set.filter(flow_name__contains=flow_name)
        # print("flow_set:", flow_set)

        return list(flow_set.values()), None

    @staticmethod
    def get_flow_node_list(params=None):
        """
        获取流程节点列表
        :param params: 请求参数
        """
        if params is None:
            params = {}
        sort = params.get("sort", "flow_number")
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=["flow_id|int", "node_name", "node_value", "status_code"],
            is_remove_empty=True
        )
        flow_node_set = FlowNode.objects.order_by(sort).filter(**params)
        flow_node_values = flow_node_set.values()
        return list(flow_node_values), None

    @staticmethod
    def get_flow_action_list(search_params=None):
        """
        获取流程动作列表
        :param search_params: 搜索参数
        """
        # 如果不传绑定参数则表示返回所有的动作列表
        if search_params is None:
            search_params = {}
        user_id = search_params.get("user_id", None)
        role_id = search_params.get("role_id", None)
        flow_node_id = search_params.get("flow_node_id", None)

        if user_id or role_id:
            operator_set = FlowActionToOperator.objects.all()
            if user_id:
                operator_set = operator_set.filter(user_id=user_id)
            if role_id:
                operator_set = operator_set.filter(role_id=role_id)
            operator_action_id_list = [it.flow_action_id for it in operator_set]
            # 如果没有找到操作人，就不应该也不能再往下匹配了，直接返回空列表
            if not operator_action_id_list:
                return [], None

            action_list = list(FlowAction.objects.filter(id__in=operator_action_id_list).values())
            return action_list, None
        elif flow_node_id:
            action_set = FlowNodeToAction.objects.filter(flow_node_id=flow_node_id).annotate(
                action=F("flow_action_id__action"),
                action_id=F("flow_action_id__id"),
                name=F("flow_action_id__name"),
                action_description=F("flow_action_id__description"),
                config=F("flow_action_id__config"),
                service_config=F("flow_action_id__service_config")
            ).values("action", "action_id", "name", "action_description", "config", "service_config")
            action_list = filter_result_field(
                result_list=list(action_set),
                alias_dict={"action_id": "id", "action_description": "description"}
            )
            return action_list, None
        else:
            search_params = format_params_handle(
                param_dict=search_params,
                filter_filed_list=["id", "action_id", "action", "name"],
                alias_dict={"action_id": "id"},
                is_remove_empty=True
            )
            action_set = FlowAction.objects.filter(**search_params)
            action_list = list(action_set.values())
            return action_list, None

    @staticmethod
    def get_flow_node_to_action_list(params=None, need_custom_serialize=False):
        """
        获取流程动作列表
        :param params: 搜索参数
        :param need_custom_serialize: 是否使用自定义的序列化工具，进行序列化数据。
        :return data,err
        """
        # need_custom_serialize = True
        if params is None:
            params = {}
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=[
                "flow_id|int", "flow_node_id|int", "flow_action_id|int", "is_using|int", "flow_node_value", "flow_action", 'flow_status_code_list|list_int'
            ],
            split_list=["flow_status_code_list"],
            alias_dict={"flow_status_code_list": "flow_status_code__in", "flow_action": "flow_action_value"}
        )
        result_set = FlowNodeToAction.objects.annotate(
            flow_id=F("flow_node__flow_id"),
            flow_node_value=F('flow_to_node__node_value'),
            flow_node_name=F('flow_node__node_name'),
            flow_node_config=F('flow_node__config'),
            flow_status_code=F('flow_node__status_code'),
            flow_action_value=F('flow_action__action'),
            flow_action_name=F('flow_action__name'),
            flow_action_config=F('flow_action__config'),
            flow_to_node_name=F('flow_to_node__node_name'),
        ).filter(**params)
        result_list = filter_result_field(
            result_list=list(
                result_set.values(
                    "id", "flow_id", "flow_node_id", "flow_node_name", "flow_node_value", "flow_node_config",
                    "flow_status_code", "flow_action_value", "flow_action_id", "flow_action_name",
                    "flow_action_config", "flow_to_node_id", "flow_to_node_name", "is_using", "api", "relate_data_key"
                )
            ),
            alias_dict={"flow_action_value": "flow_action"}
        )
        if need_custom_serialize:
            return FlowBasicService.custom_node_to_action_serialize(result_list)
        return result_list, None

    @staticmethod
    def custom_node_to_action_serialize(node_to_action_list=None):
        """
        对获取流程动作列表重新组合
        :param node_to_action_list get_flow_node_to_action_list的结果集
        :return: code_map
        """
        try:
            if node_to_action_list is None:
                node_to_action_list = []

            code_map = {}
            for i in node_to_action_list:
                nodel_info = {
                    "flow_node_id": i["flow_node_id"],
                    "flow_node_name": i["flow_node_name"],
                    "flow_node_value": i["flow_node_value"],
                    "flow_node_config": i["flow_node_config"],
                }
                action_info = {
                    "flow_action": i["flow_action"],
                    "flow_action_id": i["flow_action_id"],
                    "flow_action_name": i["flow_action_name"],
                    "flow_action_config": i["flow_action_config"]
                }

                if code_map.get(i["flow_status_code"]):
                    code_map[i["flow_status_code"]]["action_list"].append(action_info)
                else:
                    code_map[i["flow_status_code"]] = {
                        "node_info": nodel_info,
                        "action_list": [action_info]
                    }
            return code_map, None
        except Exception as e:
            return node_to_action_list, str(e)

    @staticmethod
    def get_flow_node_action_rule_list(flow_id=None, flow_node_id=None):
        """
        获取流程节点动作规则列表
        @param flow_id 流程ID
        @param flow_node_id 流程规则ID
        """
        result_set = FlowNodeActionRule.objects.all()
        result_set = result_set.annotate(
            flow_id=F('flow_node_to_action_id__flow_node_id__flow_id'),
            flow_node_id=F('flow_node_to_action_id__flow_node_id'),
            flow_action_id=F('flow_node_to_action_id__flow_action_id')
        ).filter(is_using=1)

        # 条件搜索
        if flow_id:
            result_set = result_set.filter(flow_id=flow_id)
        if flow_node_id:
            result_set = result_set.filter(flow_node_id=flow_node_id)

        result_list = list(result_set.values(
            "id",
            "flow_id",
            "flow_node_id",
            "flow_action_id",
            "rule_name",
            "rule_sort",
            "inflow_service",
            "inflow_module",
            "inflow_field",
            "outflow_module",
            "outflow_field",
            "default_value",
            "expression_string",
            "python_script",
            "is_using"
        ))

        return result_list, None
