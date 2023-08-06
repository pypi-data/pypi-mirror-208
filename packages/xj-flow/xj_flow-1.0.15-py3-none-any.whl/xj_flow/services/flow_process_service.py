# encoding: utf-8
"""
@project: djangoModel->1
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 流程控制系统
@created_time: 2023/5/17 13:29
"""

from django.db import transaction
from django.db.models import F

from ..models import FlowNodeActionRule, FlowNode, FlowAction, FlowNodeToAction, FlowRecord
from ..utils.custom_tool import *
from ..utils.j_valuation import JExpression


class FlowProcessService:
    # 执行记录
    process_context = []
    current_context = {}
    # 流程基础信息
    flow_node_dict = {}
    action_info_dict = {}
    flow_action_node_map = {}
    flow_constant_quantity_map = {}
    # 用户信息
    user_info = {}

    def push_run_action(self, func, result):
        """
        记录方法的执行过程
        :param result: 执行结果
        :param func: 方法指针
        :return: None
        """
        # 记录执行结果
        if not self.current_context.get("rule_action_result") or not isinstance(self.current_context["rule_action_result"], dict):
            self.current_context["rule_action_result"] = {}
        func_name = getattr(func, "__name__", str(func))
        self.current_context["rule_action_result"][func_name] = result

    def flow_constant_quantity(self, source_params=None, is_update=False):
        """
        获取流程常量映射
        :param source_params:用户自定义传输
        :param is_update: 是否在原有基础上再次更新
        :return: self.flow_constant_quantity_map
        """
        if source_params is None:
            source_params = {}
        if not self.flow_constant_quantity_map or is_update:
            self.flow_constant_quantity_map.update(self.action_info_dict)
            self.flow_constant_quantity_map.update(self.flow_node_dict)
            self.flow_constant_quantity_map.update(self.flow_action_node_map)
            if source_params and isinstance(source_params, dict):
                self.flow_constant_quantity_map.update(source_params)
        return self.flow_constant_quantity_map

    def __do_by_default_value(self, source_params, rule):
        """通过默认值进行赋值"""
        outflow_field = rule.get("outflow_field")
        default_value = rule.get("default_value")
        if not outflow_field or not default_value:
            return source_params
        # 如果是变量表达式则进行替换
        flow_constant_quantity = self.flow_constant_quantity()
        default_value, parsed_variable_map = JExpression.parse_variables(default_value, flow_constant_quantity, default_value="")
        # 如果是json字符串则json格式化
        default_value = parse_json(default_value)
        source_params.setdefault(outflow_field, default_value)
        # 进行记录流程
        self.push_run_action("set_default", {"field": outflow_field, "value": default_value})
        return source_params

    def __do_by_expression(self, source_params, rule):
        """通过表达式进行赋值"""
        outflow_field = rule.get("outflow_field", None)
        setting_expression_string = rule.get("expression_string", None)
        if outflow_field and setting_expression_string:
            # 公式字符串，变量解析替换
            expression_string, parsed_variable_map = JExpression.parse_variables(
                setting_expression_string,
                source_params
            )
            # 实例化计算器类，并且计算结果
            calculator = JExpression()
            data, err = calculator.process(expression_string)
            # 结果赋值
            data = round(data, 2) if isinstance(data, float) else data
            source_params[rule["outflow_field"]] = data
            # 收录执行日志
            self.push_run_action("parse_expression", {"field": outflow_field, "value": data})

        return source_params

    def __do_by_python_script(self, source_params, rule):
        """执行脚本方法"""
        inflow_field = rule.get("outflow_field", None)
        python_script = rule.get("python_script", None)
        if inflow_field and python_script:
            # 创建栈空间，并传入流入流程的字段和值
            params = {inflow_field: source_params[inflow_field]}
            # TODO 这个python_script 最好做成密文存取
            exec(python_script, params)
            inflow_filed_result = params.get(inflow_field, None)
            # 处理后的结果赋值
            source_params[inflow_field] = inflow_filed_result if inflow_filed_result else source_params[inflow_field]
            self.push_run_action("run_python_script", {"field": inflow_field, "value": source_params[inflow_field]})
        return source_params

    def do_once_flow_in_service(
            self,
            flow_node_id=None,
            flow_action_id=None,
            flow_node_value=None,
            flow_action_value=None,
            source_params: dict = None,
            user_info: dict = None,
            **kwargs
    ):
        """
        根据流程节点调用配置好的服务方法，也可以执行表达式，脚本，默认字。
        执行一个节点对动作的使用中的规则。
        @param flow_node_id 流程节点ID
        @param flow_action_id 希望处理的流程动作ID
        @param source_params 需要处理的原数据
        :param user_info: 用户信息
        :param flow_action_value: 动作Value
        :param flow_node_value:
        :return flow_id, msg
        """
        # ================ section 参数初始化  start ==========================
        self.source_params, is_pass = force_transform_type(variable=source_params, var_type="dict", default={})
        self.source_params = self.source_params.copy()
        self.user_info, is_pass = force_transform_type(variable=user_info, var_type="dict", default={})
        flow_node_id, is_pass = force_transform_type(variable=flow_node_id, var_type="int")
        flow_action_id, is_pass = force_transform_type(variable=flow_action_id, var_type="int")
        if flow_node_id is None and flow_node_value is None and flow_action_id is None and flow_action_value is None:
            return None, None
        # ================ section 参数初始化  end   ==========================

        # ================ section 获取节点或者动作信息，减少链表  start ==========================
        # note 获取流程信息
        flow_node_obj = FlowNode.objects.annotate(node_config=F("config"), node_id=F("id")).values(
            "node_id", "flow_id", "node_name", "node_value", "module_name", "flow_number", "status_code", "node_config"
        )
        if flow_action_id:
            self.flow_node_dict = flow_node_obj.filter(node_id=flow_node_id).first()
        else:
            self.flow_node_dict = flow_node_obj.filter(node_value=flow_node_value).first()
        if not self.flow_node_dict:
            return None, "不是有效的流程节点参数"
        flow_node_id = self.flow_node_dict.get("node_id")
        # note 获取动作信息
        flow_action_obj = FlowAction.objects.annotate(action_config=F("config"), action_id=F("id")).values(
            "action_id", "action", "name", "description", "action_config",
        )
        if flow_action_id:
            self.action_info_dict = flow_action_obj.filter(action_id=flow_action_id).first()
        else:
            self.action_info_dict = flow_action_obj.filter(action=flow_action_value).first()
        if not self.action_info_dict:
            return None, "不是有效的流程动作参数"
        flow_action_id = self.action_info_dict.get("action_id")
        # ================ section 获取节点或者动作信息，减少连表查询 end  ==========================

        # ================ section 获取流程执行规则 start ==========================
        # note 获取流程映射
        self.flow_action_node_map = FlowNodeToAction.objects.annotate(
            next_node_value=F("flow_to_node__node_value"),
            next_node_code=F("flow_to_node__status_code"),
            flow_to_node_value=F("flow_to_node__node_value"),
            flow_to_node_code=F("flow_to_node__status_code")
        ).filter(
            flow_node_id=flow_node_id, flow_action_id=flow_action_id, is_using=1
        ).values().first()
        if not self.flow_action_node_map:
            return None, "没有给流程映射"
        flow_node_to_action_id = self.flow_action_node_map.get("id")
        flow_to_node_info = {
            "flow_to_node_id": self.flow_action_node_map.get("flow_to_node_id"),
            "flow_to_node_value": self.flow_action_node_map.get("flow_to_node_value"),
            "flow_to_node_code": self.flow_action_node_map.get("flow_to_node_code")
        }
        # note 获取流程规则
        flow_rule_obj = FlowNodeActionRule.objects.order_by("rule_sort").filter(
            is_using=1, flow_node_to_action_id=flow_node_to_action_id
        ).values(
            "id", "flow_node_to_action_id", "rule_name", "rule_sort",
            "inflow_service", "inflow_module", "inflow_field", "outflow_module", "outflow_field",
            "default_value", "expression_string", "python_script",
        )
        flow_rule_list = list(flow_rule_obj)
        if not flow_rule_list:
            return {"source_params": self.source_params}, "没有找到可执行流程"
        # ================ section 获取流程执行规则 end   ==========================

        # ================ section 执行流程规则 start ==========================
        sid = transaction.savepoint()  # 开始事务
        err_msg = None
        for item in flow_rule_list:
            self.current_context = {
                "rule_name": item["rule_name"],
                "rule_id": item["id"],
                "is_run_service": False
            }
            # note 参数初始化
            self.source_params = self.__do_by_default_value(self.source_params, item)
            self.source_params = self.__do_by_expression(self.source_params, item)
            self.source_params = self.__do_by_python_script(self.source_params, item)
            # note 开始执行相关服务
            if not item.get("inflow_module", None) or not item.get("inflow_service", None):
                self.process_context.append(self.current_context)
                continue
            # 配置了模块，但是没有对外开放，直接返回预处理的数据
            model = sys.modules.get(item["inflow_module"], None)
            if not model:
                self.process_context.append(self.current_context)
                continue
            # 加载需要的服务，如果没有可执行的服务方法，返回预处理的数据
            service = getattr(model, item["inflow_service"], None)
            if service:
                self.current_context["is_run_service"] = True
                try:
                    input_params = service_params_adapter(service, source_params)
                    data, err = service(**input_params)
                    self.push_run_action("run_service", {"service": item["inflow_service"], "result": data, "err": err})
                    self.process_context.append(self.current_context)
                    if err:
                        # 执行错误，则进行回滚，返回执行记录
                        err_msg = err
                        transaction.savepoint_rollback(sid)
                        break
                except Exception as e:
                    transaction.savepoint_rollback(sid)
                    err_msg = "停止运行，原因如下：" + str(e)
                    self.push_run_action("run_service", {"service": item["inflow_service"], "err": err_msg})
                    self.process_context.append(self.current_context)
                    break
        # ================ section 执行流程规则 end   ==========================
        # 完成执行，清除所有的点
        transaction.clean_savepoints()
        return {"source_params": self.source_params, "process_context": self.process_context, "flow_to_node_info": flow_to_node_info}, err_msg

    def save_record(self, result_dict: dict = None, user_info: dict = None):
        """
        保存流程的执行记录
        :param result_dict: 接口执行的结果
        :param user_info: 用户信息
        :return: None,err
        """
        try:
            if user_info:
                self.user_info, is_pass = force_transform_type(variable=user_info, var_type="only_dict", default={})
            user_id = self.user_info.get("user_id", None)
            if not user_id:
                return None, "不存在用户信息"
            result_dict, is_pass = force_transform_type(variable=result_dict, var_type="only_dict", default={})
            result_dict.update(self.source_params)
            result_dict.update(self.user_info)
            # 记录字段
            flow_node_id = self.flow_node_dict.get("node_id")
            flow_action_id = self.action_info_dict.get("action_id")
            relate_data_key = self.flow_action_node_map.get("relate_data_key")
            relate_data_value = ""
            if isinstance(result_dict, dict):
                relate_data_value = result_dict.get(relate_data_key, None) if relate_data_key else ""

            # 判断是否保存
            if user_id and flow_node_id and flow_action_id:
                FlowRecord.objects.create(
                    user_id=user_id,
                    flow_node_id=flow_node_id,
                    flow_action_id=flow_action_id,
                    relate_data_key=relate_data_key,
                    relate_data_value=relate_data_value,
                    request_params=self.source_params,
                    process_context=self.process_context
                )
                return None, None
            return None, "并没有有效的执行流程"
        except Exception as e:
            return None, str(e)
