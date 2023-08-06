# encoding: utf-8
"""
@project: djangoModel->j_valuation
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 计价服务类
@created_time: 2022/10/13 16:58
"""
import math
import re

from .custom_tool import write_to_log


# 计算器基类
class JBaseExpression:
    """
    公式计算积累
    """
    __result = None  # 结果
    __expression = None
    fun_type = ""

    @staticmethod
    def get_child_info():
        """
        获取所有子类,返回公式类的名称与类指针的映射
        :return: {"IF":IFExpression}
        """
        try:
            return {getattr(i, "name"): i for i in JBaseExpression.__subclasses__() if not getattr(i, "name", None) is None}, None
        except AttributeError:
            return {}, "扩展类name属性不可以重复"

    # 解析变量
    @staticmethod
    def parse_variables(expression_string, input_dict, default_value="0"):
        """
        解析包含变量的计算公式字符串,
        从 input_dict 变量字典中拿到对应变量进行替换，没有则取0。
        :param default_value: 返回的默认值
        :param expression_string: 带有未处理的变量公式字符串： {{price}} * {{count}} - {{reduction}} + {{fee}}
        :param input_dict: 变量字典如： {'count': 1, 'price': 50, 'subitem__amount': '5,6,8', 'subitem__count': '100'}
        :return: "50 * 1 - 0 + 0 + 19 + sum(0)", err
        """
        try:
            if expression_string is None:
                return default_value, None

            # 在 expression_string 中提取出变量
            this_cell_value_match = re.compile("{{.*?}}").findall(str(expression_string))

            # 把提取出的变量与值进行映射, {"{{price}}":100}
            parsed_variable_map = {}
            for i in this_cell_value_match:
                parsed_variable_map.update({i: input_dict.get(i.replace("{{", "").replace("}}", ""), default_value)})

            # 根据映射对公式进行替换, {{price}}替换为 100
            for k, v in parsed_variable_map.items():
                expression_string = expression_string.replace(k, str(v) if v else default_value)

            return expression_string, None

        except Exception as e:
            write_to_log(prefix="计价解析变量异常", err_obj=e)
            return "0", str(e)

    # 解析括号，成对解析
    @staticmethod
    def parsed_brackets(expression, need_list=False):
        """
        递归解析变量中的括号，并调用计价进行计算
        :param expression: 不含有变量的公式字符串,如：50 * 1 - 0 + 0 + 19 + sum(0)
        :param need_list: 是否需要
        :return: expression中括号的索引元组如：[(start_index,end_index)]
        """
        twain_index_map = {}
        twain_index_list = []
        forward_index_list = []
        for char, index in zip(expression, range(len(expression))):
            if char == "(":
                forward_index_list.append(index)
            if char == ")":
                forward_bracket = forward_index_list.pop(-1)
                twain_index_map[forward_bracket] = (forward_bracket, index)
                twain_index_list.append((forward_bracket, index))
        return twain_index_list if need_list else twain_index_map

    # 检测是否可直接解析的公式，是否存在公式。
    def has_expression(self, expression_string):
        """
        判断expression_string中是否存在未计算的公式
        :param expression_string:
        :return: True/False
        """
        child_class, err = self.get_child_info()
        fun_patt = ""
        for name, instance in child_class.items():
            if not name:
                continue
            fun_patt = "(" + name + ")" if fun_patt == "" else fun_patt + "|" + "(" + name + ")"

        fun_patt = "(" + fun_patt + ")"  # 自定义公名称匹配：((IF)|(SUM)|(CEIL))
        return True if re.search(fun_patt, expression_string) else False

    # 解析公式 复杂度比较高 有优化的空间
    def parse_expression(self, expression_string):
        # 解析括号和函数
        # 解析函数
        replace_list = []
        child_class, err = self.get_child_info()
        for name, instance in child_class.items():
            # 基础计算公式跳过
            if not name:
                continue
            for r in re.finditer(instance.patt, expression_string):
                expression_start, expression_end = r.span()  # 找到未解析德公式
                full_fun_string = expression_string[expression_start:expression_end]
                fun_inner_string = full_fun_string.replace(name, "")
                # 内部存在公式不计算，方式无限递归
                if not self.has_expression(fun_inner_string):
                    result = instance().process(full_fun_string)
                    replace_list.append((full_fun_string, result))

        # 最内层结果替换
        for full_fun_string, result in replace_list:
            expression_string = expression_string.replace(full_fun_string, str(result))

        # 如果还有没有处理的公式，则递归解析
        if self.has_expression(expression_string):  # 递归解析
            expression_string = self.parse_expression(expression_string)
        return expression_string


# ================================= 公式封装类 start =======================================
class CalculateExpression(JBaseExpression):
    name = ""
    patt = "\([^\(]*?\)"

    def process(self, expression_string):
        try:
            return eval(expression_string)  # 加加减乘除
        except ZeroDivisionError:
            return 0  # 0/n  的情况
        except Exception as e:
            write_to_log(level="error", prefix="计价异常（SUMExpression）", err_obj=e)
            return expression_string


class IFExpression(JBaseExpression):
    """
    布尔值判断、三元运算
    """
    name = "IF"
    patt = "IF\([^\(]*?\)"

    def process(self, expression, *args, ):
        bool_expression, yes_expression, no_expression = expression.replace(IFExpression.name, "").replace("(", "").replace(")", "").split(",")
        if CalculateExpression().process(bool_expression):
            return yes_expression
        else:
            return no_expression


class SUMExpression(JBaseExpression):
    """
    求和计算、（多参数在服务中获取）
    """
    name = "SUM"
    patt = "SUM\([^\(]*?\)"  # SUM(a,b,c) == a+b+c

    def process(self, expression):
        try:
            args = expression.replace(self.name, "").replace("(", "").replace(")", "").split(",")
            result = 0
            for i in args:
                result = eval(str(result) + "+" + str(i))
            return result
        except Exception as e:
            write_to_log(level="error", prefix="计价异常（SUMExpression）", err_obj=e)
            return 0


class CEILExpression(JBaseExpression):
    """
    取整公式
    """
    name = "CEIL"
    patt = "CEIL\([^\(]*?\)"  # ROUND(num, index, step)

    def process(self, expression):
        try:
            expression = expression.replace(self.name, "").replace("(", "").replace(")", "")
            return math.ceil(eval(expression))
        except Exception as e:
            write_to_log(level="error", prefix="计价异常（SUMExpression）", err_obj=e)
            return 0


# ================================= 公式封装类 end  =======================================

# ================================= 算入口类，计算器 对外暴露的类 start =======================================

class JExpression(JBaseExpression):
    """
    计算入口类，计算器 对外暴露的类
    """

    def process(self, expression_string):
        # 公式合法性校验：expression_string
        if expression_string is None:
            return "", None
        if not len(re.findall("\(", expression_string)) == len(re.findall("\)", expression_string)):
            write_to_log(prefix="计价公式配置错误，请及时检查", content="语法错误，括号应该成对存在")
            return None, "语法错误，括号应该成对存在"
        # 公式字符串,符号预处里预处理
        expression_string = expression_string.upper().replace(" ", "").replace("=", "==").replace(">==", ">=").replace("<==", "<=")

        # 把自定义公式计算出结果进行替换，得出基础的加减乘除公式字符拆
        parsed_expression_string = self.parse_expression(expression_string)

        # 计算基础加减乘除，然后得出结果并返回
        result = CalculateExpression().process(parsed_expression_string)
        return result, None
# ================================= 算入口类，计算器 对外暴露的类 end   =======================================
