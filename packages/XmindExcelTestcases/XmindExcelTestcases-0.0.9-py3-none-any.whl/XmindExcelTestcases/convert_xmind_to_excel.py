import pandas as pd
import os, sys
from xmindparser import xmind_to_dict
import pandas.io.formats.excel

pandas.io.formats.excel.header_style = None


class ConvertXmindToExcel:
    def __init__(self):
        self.markdown_dict = dict()
        self.feature_layer = '用例目录'
        self.case_feature_id = '需求ID'
        self.case_title = '用例名称'
        self.case_description = '用例描述'
        self.case_pre_condition = '前置条件'
        self.case_steps = '用例步骤'
        self.result = '预期结果'
        self.case_type = '用例类型'
        self.case_state = '用例状态'
        self.case_level = '用例等级'
        self.case_founder = '创建人'
        # self.case_isauto = '是否实现自动化'
        # self.case_isput = '是否上架'
        # self.autocase_type = '自动化测试类型'
        # self.autocase_platform = '自动化测试平台'

        self.markdown_dict[self.feature_layer] = []
        self.markdown_dict[self.case_feature_id] = []
        self.markdown_dict[self.case_title] = []
        self.markdown_dict[self.case_description] = []
        self.markdown_dict[self.case_pre_condition] = []
        self.markdown_dict[self.case_steps] = []
        self.markdown_dict[self.result] = []
        self.markdown_dict[self.case_type] = []
        self.markdown_dict[self.case_state] = []
        self.markdown_dict[self.case_level] = []
        self.markdown_dict[self.case_founder] = []
        # self.markdown_dict[self.case_isauto] = []
        # self.markdown_dict[self.case_isput] = []
        # self.markdown_dict[self.autocase_type] = []
        # self.markdown_dict[self.autocase_platform] = []

        self.index = 0
        self.ignore_layer_number = 1

    def convert(self, xmind_path, excel_path, ignore_layer_number='1'):
        if os.path.isfile(xmind_path):
            # 如果传递单个xmind文件，则直接转换
            self.convert_single_file(xmind_path, excel_path, ignore_layer_number)
        # 如果传递xmind文件夹的路径，则遍历文件夹中的xmind文件进行转换，放到指定的目录下面 或者 汇合到同一个Excel文件中
        elif os.path.isdir(xmind_path):
            # 如果Excel_path是指定的文件，则进行汇总
            if excel_path.endswith('.xlsx'):
                self.convert_multiple_file(xmind_path, excel_path, ignore_layer_number)
                return
            # 否则放到指定的目录下面
            if not os.path.exists(excel_path):
                os.makedirs(excel_path)
            xmind_dir = os.walk(xmind_path)
            for path, dir_list, file_list in xmind_dir:
                for file_name in file_list:
                    if not file_name.endswith('.xmind'):
                        continue
                    self.convert_single_file(os.path.join(path, file_name),
                                             os.path.join(excel_path, file_name.replace('.xmind', '.xlsx')),
                                             ignore_layer_number)

    # 将多个xmind转换为单个excel文件
    def convert_multiple_file(self, xmind_path, excel_file_path, ignore_layer_number):
        xmind_dir = os.walk(xmind_path)
        for path, dir_list, file_list in xmind_dir:
            for file_name in file_list:
                if not file_name.endswith('.xmind'):
                    continue
                self.ignore_layer_number = int(ignore_layer_number)
                self.parseXmindToDict(os.path.join(path, file_name))
                self.index = 0
            df = pd.DataFrame(self.markdown_dict)
            writer = pd.ExcelWriter(excel_file_path, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='case_data', startrow=1, index=False, header=False)

            workbook = writer.book
            worksheet = writer.sheets['case_data']
            fmt = workbook.add_format({'font_name': u'微软雅黑', 'font_size': 10, 'text_wrap': True})
            worksheet.set_column('A:Z', None, fmt)
            worksheet.set_row(0, None, fmt)
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, fmt)

            for idx, col in enumerate(df):
                series = df[col]
                max_len = max(series.astype(str).map(len).max(), len(str(series.name))) + 4
                worksheet.set_column(idx, idx, max_len)
            try:
                writer.save()
            except:
                writer.close()

    # 将单个xmind转换为单个excel文件
    def convert_single_file(self, xmind_path, excel_path, ignore_layer_number):
        try:
            self.ignore_layer_number = int(ignore_layer_number)
            self.parseXmindToDict(xmind_path)
            df = pd.DataFrame(self.markdown_dict)
            writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='case_data', startrow=1, index=False, header=False)

            workbook = writer.book
            worksheet = writer.sheets['case_data']
            fmt = workbook.add_format({'font_name': u'微软雅黑', 'font_size': 10, 'text_wrap': True})
            worksheet.set_column('A:Z', None, fmt)
            worksheet.set_row(0, None, fmt)
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, fmt)

            for idx, col in enumerate(df):
                series = df[col]
                max_len = max(series.astype(str).map(len).max(), len(str(series.name))) + 4
                worksheet.set_column(idx, idx, max_len)

            try:
                writer.save()
            except:
                writer.close()

        finally:
            self.markdown_dict = dict()
            self.feature_layer = '用例目录'
            self.case_feature_id = '需求ID'
            self.case_title = '用例名称'
            self.case_description = '用例描述'
            self.case_pre_condition = '前置条件'
            self.case_steps = '用例步骤'
            self.result = '预期结果'
            self.case_type = '用例类型'
            self.case_state = '用例状态'
            self.case_level = '用例等级'
            self.case_founder = '创建人'
            # self.case_isauto = '是否实现自动化'
            # self.case_isput = '是否上架'
            # self.autocase_type = '自动化测试类型'
            # self.autocase_platform = '自动化测试平台'

            self.markdown_dict[self.feature_layer] = []
            self.markdown_dict[self.case_feature_id] = []
            self.markdown_dict[self.case_title] = []
            self.markdown_dict[self.case_description] = []
            self.markdown_dict[self.case_pre_condition] = []
            self.markdown_dict[self.case_steps] = []
            self.markdown_dict[self.result] = []
            self.markdown_dict[self.case_type] = []
            self.markdown_dict[self.case_state] = []
            self.markdown_dict[self.case_level] = []
            self.markdown_dict[self.case_founder] = []
            # self.markdown_dict[self.case_isauto] = []
            # self.markdown_dict[self.case_isput] = []
            # self.markdown_dict[self.autocase_type] = []
            # self.markdown_dict[self.autocase_platform] = []
            self.index = 0
            self.ignore_layer_number = 0

    def parseXmindToDict(self, xmind_file_path):
        content_dict = xmind_to_dict(xmind_file_path)
        object = content_dict[0]['topic']
        content_array = []
        for i in range(100):
            content_array.append(i)
        self.analyze(content_array, object)

    def analyze(self, content_array, topic_object):
        content_array[self.index] = topic_object['title']
        if 'topics' not in topic_object.keys() or len(topic_object['topics']) == 0:
            self.generate(content_array)
            return
        self.index = self.index + 1
        for topic in topic_object['topics']:
            self.analyze(content_array, topic)
        self.index = self.index - 1

    def generate(self, content_array):
        title = ''

        flag_dict = {self.feature_layer: False, self.case_feature_id: False, self.case_description: False,
                     self.case_pre_condition: False, self.case_steps: False, self.result: False,
                     self.case_level: False, self.case_founder: False}

        for i in range(self.index + 1):
            content = content_array[i]
            content = content.replace('\b', '')
            if self.check_in_column(content):
                # 如果content以 "列名："的样式开开头，则进入对应的列名解析
                column_name, column_value = self.analyse_column(content)
                self.markdown_dict[column_name].append(column_value.strip())
                flag_dict[column_name] = True
            else:
                # 否则则将其作为标题层级进行解析
                if i < self.ignore_layer_number:
                    continue
                title += '_' + content.strip()
        self.markdown_dict[self.case_title].append(title[1:].replace('\n', ''))

        case_type = '功能测试'
        case_state = '正常'
        self.markdown_dict[self.case_type].append(case_type)
        self.markdown_dict[self.case_state].append(case_state)

        # 将剩余没有被赋值的列，赋值为空字符串
        for key in flag_dict:
            if not flag_dict[key]:
                self.markdown_dict[key].append('')

    def check_in_column(self, content):
        content = content.lstrip()
        if content.startswith(self.feature_layer + ':') or content.startswith(self.feature_layer + '：'):
            return True
        elif content.startswith(self.case_feature_id + ':') or content.startswith(self.case_feature_id + '：'):
            return True
        elif content.startswith(self.case_description + ':') or content.startswith(self.case_description + '：'):
            return True
        elif content.startswith(self.case_pre_condition + ':') or content.startswith(self.case_pre_condition + '：'):
            return True
        elif content.startswith(self.case_steps + ':') or content.startswith(self.case_steps + '：'):
            return True
        elif content.startswith(self.result + ':') or content.startswith(self.result + '：'):
            return True
        elif content.startswith(self.case_type + ':') or content.startswith(self.case_type + '：'):
            return True
        elif content.startswith(self.case_state + ':') or content.startswith(self.case_state + '：'):
            return True
        elif content.startswith(self.case_level + ':') or content.startswith(self.case_level + '：'):
            return True
        elif content.startswith(self.case_founder + ':') or content.startswith(self.case_founder + '：'):
            return True
        # elif content.startswith(self.case_isauto + ':') or content.startswith(self.case_isauto + '：'):
        #     return True
        # elif content.startswith(self.case_isput + ':') or content.startswith(self.case_isput + '：'):
        #     return True
        # elif content.startswith(self.autocase_type + ':') or content.startswith(self.autocase_type + '：'):
        #     return True
        # elif content.startswith(self.autocase_platform + ':') or content.startswith(self.autocase_platform + '：'):
        #     return True
        else:
            return False

    def analyse_column(self, content):
        content = content.lstrip().replace('\b', '')
        if content.startswith(self.feature_layer + ':') or content.startswith(self.feature_layer + '：'):
            return self.feature_layer, content.lstrip().replace(self.feature_layer + ':', '').replace(
                self.feature_layer + '：', '')
        elif content.startswith(self.case_feature_id + ':') or content.startswith(self.case_feature_id + '：'):
            return self.case_feature_id, content.lstrip().replace(self.case_feature_id + ':', '').replace(
                self.case_feature_id + '：', '')
        elif content.startswith(self.case_description + ':') or content.startswith(self.case_description + '：'):
            return self.case_description, content.lstrip().replace(self.case_description + ':', '').replace(
                self.case_description + '：', '')
        elif content.startswith(self.case_pre_condition + ':') or content.startswith(self.case_pre_condition + '：'):
            return self.case_pre_condition, content.lstrip().replace(self.case_pre_condition + ':', '').replace(
                self.case_pre_condition + '：', '')
        elif content.startswith(self.case_steps + ':') or content.startswith(self.case_steps + '：'):
            return self.case_steps, content.lstrip().replace(self.case_steps + ':', '').replace(
                self.case_steps + '：', '')
        elif content.startswith(self.result + ':') or content.startswith(self.result + '：'):
            return self.result, content.lstrip().replace(self.result + ':', '').replace(
                self.result + '：', '')
        elif content.startswith(self.case_type + ':') or content.startswith(self.case_type + '：'):
            return self.case_type, content.lstrip().replace(self.case_type + ':', '').replace(
                self.case_type + '：', '')
        elif content.startswith(self.case_state + ':') or content.startswith(self.case_state + '：'):
            return self.case_state, content.lstrip().replace(self.case_state + ':', '').replace(
                self.case_state + '：', '')
        elif content.startswith(self.case_level + ':') or content.startswith(self.case_level + '：'):
            return self.case_level, content.lstrip().replace(self.case_level + ':', '').replace(
                self.case_level + '：', '')

        elif content.startswith(self.case_founder + ':') or content.startswith(self.case_founder + '：'):
            return self.case_founder, content.lstrip().replace(self.case_founder + ':', '').replace(
                self.case_founder + '：', '')
        # elif content.startswith(self.case_isauto + ':') or content.startswith(self.case_isauto + '：'):
        #     return self.case_isauto, content.lstrip().replace(self.case_isauto + ':', '').replace(
        #         self.case_type + '：', '')
        # elif content.startswith(self.case_isput + ':') or content.startswith(self.case_isput + '：'):
        #     return self.case_isput, content.lstrip().replace(self.case_isput + ':', '').replace(
        #         self.case_isput + '：', '')
        # elif content.startswith(self.autocase_type + ':') or content.startswith(self.autocase_type + '：'):
        #     return self.autocase_type, content.lstrip().replace(self.autocase_type + ':', '').replace(
        #         self.autocase_type + '：', '')
        # elif content.startswith(self.autocase_platform + ':') or content.startswith(self.autocase_platform + '：'):
        #     return self.autocase_platform, content.lstrip().replace(self.autocase_platform + ':', '').replace(
        #         self.autocase_platform + '：', '')
