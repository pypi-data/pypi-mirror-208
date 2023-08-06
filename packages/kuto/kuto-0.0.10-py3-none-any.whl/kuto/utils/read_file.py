import json
import yaml

from kuto.utils.excel import Excel, CSV


def read_json(file_path, key=None):
    """
    读取json文件中的指定key
    @return
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    if isinstance(json_data, list):
        return json_data
    else:
        if key:
            return json_data[key]
        raise ValueError('key不能为空')


def read_yaml(file_path, key=None):
    """
    读取yaml文件中的指定key
    @param file_path:
    @param key:
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        yaml_data = yaml.load(f, Loader=yaml.FullLoader)
    if isinstance(yaml_data, list):
        return yaml_data
    else:
        if key:
            return yaml_data[key]
        raise ValueError('key不能为空')


def read_csv(file_path, row=None):
    """
    读取csv文件中的指定行
    @param file_path: 文件名
    @param row: 行数，从1开始
    """
    csv_file = CSV(file_path)
    if row:
        csv_data = [csv_file.read_row_index(row)]
    else:
        csv_data = csv_file.read_all()
    return csv_data


def read_excel(file_path, row=None):
    """
    读取excel文件中的指定行，暂时只支持读取第一个sheet
    @param file_path: 文件名
    @param row: 行数，从1开始
    """
    excel_file = Excel(file_path)
    if row:
        excel_data = [excel_file.read_row_index(row)]
    else:
        excel_data = excel_file.read_all()
    return excel_data


if __name__ == '__main__':
    print(read_json('data.json', key='names'))
    print(read_yaml('data.yml', key='names'))
    print(read_csv('data.csv', row=1))
    print(read_excel('data.xlsx', row=1))



