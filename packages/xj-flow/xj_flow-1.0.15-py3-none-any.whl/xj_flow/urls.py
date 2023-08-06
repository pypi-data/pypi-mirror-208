# _*_coding:utf-8_*_
from django.conf import settings
from django.conf.urls import static
from django.conf.urls import url
from django.urls import re_path

from .apis.flow_list import FlowList
from .apis.flow_node_list import FlowNodeList
from .apis.flow_node_rule_list import FlowNodeActionRuleList
from .apis.flow_process import FlowProcess
from .apis.flow_action_list import FlowActionList
from .apis.flow_node_to_action_list import FlowNodeToActionList

# 应用名称
app_name = 'xj_flow'


urlpatterns = [
    url(r'^list/?$', FlowList.as_view(), name='flow_list'),
    url(r'^node_list/?$', FlowNodeList.as_view(), name='flow_node_list'),
    url(r'^action_list/?$', FlowActionList.as_view(), name='flow_action_list'),
    url(r'^node_to_action_list/?$', FlowNodeToActionList.as_view(), name='flow_node_to_action_list'),
    url(r'^node_action_rule_list/?$', FlowNodeActionRuleList.as_view(), name='flow_node_action_rule_list'),
    url(r'^process/?$', FlowProcess.as_view(), name='flow_process'),

]
