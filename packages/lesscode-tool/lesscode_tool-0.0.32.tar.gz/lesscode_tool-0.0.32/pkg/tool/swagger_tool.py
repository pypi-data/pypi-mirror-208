# -*- coding: utf-8 -*-
import json
import re
from itertools import groupby
from operator import itemgetter

import yaml


def doc2dict(doc):
    param_dict = dict()
    response_dict = dict()
    example = ""

    param_pattern = r":param (\w+): (.+)"
    param_matches = re.findall(param_pattern, doc)
    for param_name, param_desc in param_matches:
        param_dict[param_name] = param_desc

    return_pattern = r":return (\w+): (.+)"
    return_match = re.findall(return_pattern, doc)
    for return_name, return_desc in return_match:
        response_dict[return_name] = return_desc

    example_pattern = r":example (.+)"
    example_match = re.search(example_pattern, doc, flags=re.S)
    if example_match:
        example = example_match.groups()[0]

    result = {
        "param_dict": param_dict,
        "response_dict": response_dict,
        "example": example
    }
    return result


def gen_md_table(headers: list, data: list):
    trs = ''.join([f"<tr>{''.join([f'<td>{td}</td>' for td in tr])}</tr>" for tr in data])
    table_str = f"<table border=\"1\">" \
                f"<tr>{''.join([f'<th>{th}</th>' for th in headers])}</tr>" \
                f"{trs}" \
                f"</table>  \n"
    return table_str


def data2md_str(data, field="tag", base_url="http://127.0.0.1"):
    data.sort(key=itemgetter(field))
    api_class_str = ""
    index = 1
    for key, items in groupby(data, key=itemgetter(field)):
        api_class_str += f"\n## **{index}.{key}**  \n"
        for i, api in enumerate(items):
            description = api.get('description') if api.get('description') and isinstance(api.get('description'),
                                                                                          str) else ""
            description_info = doc2dict(description)
            url = f"{base_url}{api.get('url')}"
            header_arr = []
            param_arr = []
            body_arr = []
            for param in api.get("parameters", []):
                if param.get("in") == "query":
                    param_name = param.get('name')
                    param_desc = description_info.get("param_dict", {}).get(param_name) if description_info.get(
                        "param_dict", {}).get(param_name) else ""
                    param_default = param.get('default') if param.get('default') is not None else "null"
                    param_required = 'true' if param.get('required') else 'false'
                    param_type = param.get('type')
                    param_arr.append([param_name, param_required, param_type, param_default, param_desc])
                elif param.get("in") == "header":
                    header_name = param.get('name')
                    header_desc = description_info.get(header_name) if description_info.get(header_name) else ""
                    header_required = 'true' if param.get('required') else 'false'
                    header_type = param.get('type')
                    header_default = param.get('default') if param.get('default') is not None else "null"
                    header_arr.append([header_name, header_required, header_type, header_default, header_desc])
                elif param.get("in") == "body":
                    schema = param.get('schema', {})
                    if schema:
                        for property_name, property_info in schema.get("properties", {}).items():
                            property_desc = description_info.get("param_dict", {}).get(
                                property_name) if description_info.get("param_dict", {}).get(
                                property_name) else ""
                            property_default = property_info.get('default') if property_info.get(
                                'default') is not None else "null"
                            property_required = 'true' if property_info.get('required') else 'false'
                            property_type = property_info.get('type')
                            param_arr.append(
                                [property_name, property_required, property_type, property_default, property_desc])
            api_class_str += f"\n### {index}.{i + 1} {api.get('summary')}  \n###### 请求地址  \n> <{url}>  \n\n" \
                             f"###### 支持格式  \n> JSON  \n\n###### HTTP请求方式  \n" \
                             f"> {api.get('method').upper()}  \n\n"
            header_arr.append(["Content-Type", "true", "string", "", "application/json"])
            if header_arr:
                header_table_headers = ['参数', '必选', '类型', '默认值', '说明']
                header_str = f'###### 请求头  \n{gen_md_table(header_table_headers, header_arr)}'
                api_class_str = f"{api_class_str}  \n{header_str}  \n"
            if param_arr:
                param_table_headers = ['参数', '必选', '类型', '默认值', '说明']
                param_str = f'###### 请求参数  \n{gen_md_table(param_table_headers, param_arr)}'
                api_class_str = f"{api_class_str}  \n{param_str}  \n"
            if body_arr:
                body_table_headers = ['参数', '必选', '类型', '默认值', '说明']
                body_str = f'###### 请求参数  \n{gen_md_table(body_table_headers, body_arr)}'
                api_class_str = f"{api_class_str}  \n{body_str}  \n"
            response_dict = description_info.get("response_dict", {})
            if response_dict:
                response_table_headers = ['参数', '说明']
                response_arr = [[k, v] for k, v in response_dict.items()]
                api_class_str += f"###### 返回字段  \n{gen_md_table(response_table_headers, response_arr)}  \n"
            example = description_info.get("example")
            if example:
                api_class_str += f"\n###### 响应示例  \n```json\n{example}\n```"
            api_class_str += "\n\n"
        index += 1
    return api_class_str


class IndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)


def swagger_json2yaml(data):
    data_str = json.dumps(data)
    data_yaml = yaml.load(data_str, Loader=yaml.FullLoader)
    return yaml.dump(data_yaml, Dumper=IndentDumper, indent=2, default_flow_style=False,
                     explicit_start=True, allow_unicode=True, encoding="utf-8").decode(encoding="utf-8")


def swagger_json2markdown(data, base_url):
    route_str = data2md_str(data.get("paths"), "tag", base_url)
    title = ""
    info = data.get('info')
    if info and isinstance(info, dict):
        title = info.get("title")
    result_str = f"# 项目名称:{title}  \n" + route_str
    return result_str


def remove_null(data):
    if isinstance(data, dict):
        new_data = dict()
        for key, value in data.items():
            if key and value:
                if isinstance(value, dict) or isinstance(value, list):
                    value = remove_null(value)
                new_data.update({key: value})
    elif isinstance(data, list):
        new_data = list()
        for item in data:
            if item:
                if isinstance(item, dict) or isinstance(item, list):
                    item = remove_null(item)
                new_data.append(remove_null(item))
    else:
        new_data = data
    return new_data


def dict_update(origin: dict, key, value):
    if key and value:
        origin.update({key: value})


def swagger_pre_handle(data: dict):
    new_data = dict()
    keys = ["swagger", "info", "definitions", "servers", "host"]
    for key in keys:
        value = remove_null(data.get(key))
        dict_update(new_data, key, value)
    paths = data.get("paths", {})
    new_paths = list()
    for url, info in paths.items():
        for method, method_info in info.items():
            method_tags = method_info.get("tags")
            if method_tags:
                for tag in method_tags:
                    new_info = {
                        "url": url
                    }
                    new_info.update({"method": method,
                                     "tag": tag if tag else '',
                                     "summary": method_info.get("summary"),
                                     "parameters": method_info.get("parameters"),
                                     "description": method_info.get("description"),
                                     "responses": method_info.get("responses")})
                    new_paths.append(new_info)
    new_data.update({"paths": new_paths})
    return new_data


def swagger_convert(json_data, out_type, file_path=None, base_url="http://127.0.0.1"):
    json_data = swagger_pre_handle(json_data)
    if out_type in ["yaml", "yml"]:
        result_data = swagger_json2yaml(json_data)
    elif out_type in ["md", "markdown"]:
        result_data = swagger_json2markdown(json_data, base_url)
    else:
        print(f"暂不支持输出类型{out_type}")
        return
    if file_path:
        with open(file_path, "w+") as f:
            f.write(result_data)
    else:
        print(result_data)
