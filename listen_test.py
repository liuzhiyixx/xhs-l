import time
import datetime
import pandas as pd
import json  # 导入json模块
from DrissionPage import WebPage
from DrissionPage.common import Actions
import os  # 导入os模块
import csv  # 导入csv模块
import argparse

# 创建 ArgumentParser 对象
parser = argparse.ArgumentParser(description='Search for titles on Xiaohongshu')

# 添加命令行参数
parser.add_argument('--query', type=str, default='麻婆豆腐怎么做', help='全局搜索词')
parser.add_argument('--max-title', type=int, default=10, help='最大搜索的title数量')
parser.add_argument('--step', type=int, default=1200, help='在一个title中搜索每页滚动的步长')
parser.add_argument('--time-in-title', type=int, default=120, help='在一个title中搜索的最大时间')
parser.add_argument('--excel-name', type=str, default='comments.xlsx', help='自己指定excel文件名')
parser.add_argument('--csv-name', type=str, default='comments.csv', help='自己指定csv文件名')

# 解析命令行参数
args = parser.parse_args()

# 使用解析后的参数
search_query = args.query
search_max_num_of_title = args.max_title
if search_max_num_of_title <= 0:
    search_max_num_of_title = 1

search_step_in_one_title = args.step
search_time_in_one_title = args.time_in_title

# 开启浏览器窗口
wp = WebPage()
ac = Actions(wp)
info = []
page_num = 0

# 定义CSV文件路径
csv_file_path = args.csv_name

# 指定表头
headers = [
    "全局搜索词", 
    "Title用户名", 
    "Title主题", 
    "Title描述", 
    "Title IP地址", 
    "Title时间", 
    "Title评论数", 
    "一级评论用户", 
    "一级评论用户头像", 
    "一级评论内容", 
    "一级评论时间", 
    "一级评论的回复数", 
    "二级评论用户", 
    "二级评论用户头像", 
    "二级评论内容", 
    "二级评论时间", 
    "二级评论回应的用户名"
]

# 创建并写入CSV文件
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # 写入表头
    writer.writerow(headers)

# 监听指定API路径
print("Starting listener...")

listen_feed = 'api/sns/web/v1/feed' # 主题界面 含有题主信息
listen_first_comment = 'api/sns/web/v2/comment/page'# 评论
listen_sub_comment = 'api/sns/web/v2/comment/sub/page' # 展开的评论 

wp.listen.start([
    listen_feed,
    listen_first_comment, 
    listen_sub_comment,
])

# 定位搜索框并输入内容
search_input = wp.ele('xpath://div[@class="input-box"]/input[@id="search-input"]')
search_input.clear()# 清空搜索框
search_input.input(search_query)
wp.ele('xpath://div[@class="search-icon"]').click()

# 等待页面加载完成
time.sleep(3)

# 模拟用户交互以触发API请求
print("Simulating user interaction...")


data_list = []

# 打开文件以追加模式
with open('output.txt', 'w', encoding='utf-8-sig') as file:
    def print_and_log(message):
        print(message)
        file.write(message + '\n')

    def handle_packet(packet):
        global page_num  # 声明page_num为全局变量
        if packet:
            message = f"Response body: {packet.response.body}"
            # print_and_log(message)

            page_num += 1
            print_and_log(f"****************截取的包次: {page_num}************")

            # 解析 JSON 响应
            try:
                response_body = packet.response.body
                if isinstance(response_body, bytes):
                    response_body = response_body.decode('utf-8')  # 将字节流解码为字符串
                elif isinstance(response_body, dict):
                    response_json = response_body  # 如果已经是字典，直接使用
                else:
                    response_json = json.loads(response_body)  # 否则解析为字典
            
                if listen_feed in packet.request.url:
                    print_and_log("主题页面")
                    item = response_json['data']['items'][0]

                    try:
                        user_nickname = item['note_card']['user']['nickname']
                    except KeyError:
                        user_nickname = 'Unknown Nickname'

                    try:
                        note_card_title = item['note_card']['title']
                    except KeyError:
                        note_card_title = 'Unknown Title'

                    try:
                        note_card_desc = item['note_card']['desc']
                    except KeyError:
                        note_card_desc = 'No description'

                    try:
                        ip_location = item['note_card']['ip_location']
                    except KeyError:
                        ip_location = 'Unknown IP'

                    try:
                        last_update_time = item['note_card']['last_update_time']
                        last_update_time_dt = datetime.datetime.fromtimestamp(last_update_time / 1000.0)
                        last_update_time_formatted = last_update_time_dt.strftime('%Y-%m-%d %H:%M:%S')
                    except KeyError:
                        last_update_time_formatted = 'Unknown Time'
                    except TypeError:
                        last_update_time_formatted = 'Invalid Time Format'

                    try:
                        interact_info_liked_count = item['note_card']['interact_info']['liked_count']
                    except KeyError:
                        interact_info_liked_count = '0'

                    try:
                        interact_info_comment_count = item['note_card']['interact_info']['comment_count']
                    except KeyError:
                        interact_info_comment_count = '0'
                

                    print_and_log(f"Title 用户名: {user_nickname}")
                    print_and_log(f"Title 主题: {note_card_title}")
                    print_and_log(f"Title 描述: {note_card_desc}")
                    print_and_log(f"Title IP地址: {ip_location}")
                    print_and_log(f"Title 时间: {last_update_time_formatted}")
                    print_and_log(f"Title 点赞数: {interact_info_liked_count}")
                    print_and_log(f"Title 评论数: {interact_info_comment_count}")

                    data_list.append({
                        '全局搜索词': search_query,
                        'Title用户名': user_nickname,
                        'Title主题': note_card_title,
                        'Title描述': note_card_desc,
                        'Title IP地址': ip_location,
                        'Title时间': last_update_time_formatted,
                        'Title评论数': interact_info_comment_count,
                    })
                    df = pd.DataFrame(data_list)
                    #追加到csv文件的前七列
                    df.to_csv(csv_file_path, mode='a', index=False, encoding='utf-8-sig', header=False)
                    data_list.clear()  # 清空data_list

                elif listen_first_comment in packet.request.url:
                    data_comments = response_json['data']['comments']
                    for comment in data_comments:
                        cm_user_info_nickname = comment['user_info']['nickname']
                        cm_user_info_image_url = comment['user_info']['image']
                        cm_content = comment['content']
                        cm_create_time = comment['create_time']
                        cm_create_time_dt = datetime.datetime.fromtimestamp(cm_create_time / 1000.0)
                        cm_create_time = cm_create_time_dt.strftime('%Y-%m-%d %H:%M:%S')

                        cm_sub_comment_count = comment['sub_comment_count']
                        print_and_log(f"一级评论 用户名: {cm_user_info_nickname}")
                        print_and_log(f"一级评论 头像: {cm_user_info_image_url}")
                        print_and_log(f"一级评论 内容: {cm_content}")
                        print_and_log(f"一级评论 时间: {cm_create_time}")
                        print_and_log(f"一级评论 回复数: {cm_sub_comment_count}")

                        data_list.append({
                            '全局搜索词': '',
                            'Title用户名': '',
                            'Title主题': '',
                            'Title描述': '',
                            'Title IP地址': '',
                            'Title时间': '',
                            'Title评论数': '',
                            '一级评论用户': cm_user_info_nickname,
                            '一级评论头像': cm_user_info_image_url,
                            '一级评论内容': cm_content,
                            '一级评论时间': cm_create_time,
                            '一级评论的回复数': cm_sub_comment_count,
                        })
                        df = pd.DataFrame(data_list)
                        df.to_csv(csv_file_path, mode='a', index=False, encoding='utf-8-sig', header=False)
                        data_list.clear()  # 清空data_list

                        if comment['sub_comments']:
                            for sub_comment in comment['sub_comments']:
                                cm_sub_info_nickname = sub_comment['user_info']['nickname']
                                cm_sub_info_image_url = sub_comment['user_info']['image']
                                cm_sub_content = sub_comment['content']
                                cm_sub_create_time = sub_comment['create_time']
                                cm_sub_create_time_dt = datetime.datetime.fromtimestamp(cm_sub_create_time / 1000.0)
                                cm_sub_create_time = cm_sub_create_time_dt.strftime('%Y-%m-%d %H:%M:%S')
                                cm_sub_target_comment_nickname = sub_comment['target_comment']['user_info']['nickname']
                                print_and_log(f"二级评论 用户名: {cm_sub_info_nickname}")
                                print_and_log(f"二级评论 头像: {cm_sub_info_image_url}")
                                print_and_log(f"二级评论 内容: {cm_sub_content}")
                                print_and_log(f"二级评论 时间: {cm_sub_create_time}")
                                print_and_log(f"二级评论 回应的用户名: {cm_sub_target_comment_nickname}")

                                data_list.append({
                                    '全局搜索词': '',
                                    'Title用户名': '',
                                    'Title主题': '',
                                    'Title描述': '',
                                    'Title IP地址': '',
                                    'Title时间': '',
                                    'Title评论数': '',
                                    '一级评论用户': '',
                                    '一级评论头像': '',
                                    '一级评论内容': '',
                                    '一级评论时间': '',
                                    '一级评论的回复数': '',
                                    '二级评论用户': cm_sub_info_nickname,
                                    '二级评论头像': cm_sub_info_image_url,
                                    '二级评论内容': cm_sub_content,
                                    '二级评论时间': cm_sub_create_time,
                                    '二级评论回应的用户名': cm_sub_target_comment_nickname,
                                })
                                df = pd.DataFrame(data_list)
                                df.to_csv(csv_file_path, mode='a', index=False, encoding='utf-8-sig', header=False)
                                data_list.clear()  # 清空data_list

                elif listen_sub_comment in packet.request.url:
                    ex_sub_comments = response_json['data']['comments']
                    for ex_sub_comment in ex_sub_comments:
                        ex_sub_user_info_nickname = ex_sub_comment['user_info']['nickname']
                        ex_sub_user_info_image_url = ex_sub_comment['user_info']['image']
                        ex_sub_content = ex_sub_comment['content']
                        ex_sub_create_time = ex_sub_comment['create_time']
                        ex_sub_create_time_dt = datetime.datetime.fromtimestamp(ex_sub_create_time / 1000.0)
                        ex_sub_create_time = ex_sub_create_time_dt.strftime('%Y-%m-%d %H:%M:%S')
                        ex_sub_target_comment_nickname = ex_sub_comment['target_comment']['user_info']['nickname']
                        print_and_log(f"二级评论 用户名: {ex_sub_user_info_nickname}")
                        print_and_log(f"二级评论 头像: {ex_sub_user_info_image_url}")
                        print_and_log(f"二级评论 内容: {ex_sub_content}")
                        print_and_log(f"二级评论 时间: {ex_sub_create_time}")
                        print_and_log(f"二级评论 回应的用户名: {ex_sub_target_comment_nickname}")

                        data_list.append({
                            '全局搜索词': '',
                            'Title用户名': '',
                            'Title主题': '',
                            'Title描述': '',
                            'Title IP地址': '',
                            'Title时间': '',
                            'Title评论数': '',
                            '一级评论用户': '',
                            '一级评论头像': '',
                            '一级评论内容': '',
                            '一级评论时间': '',
                            '一级评论的回复数': '',
                            '二级评论用户': ex_sub_user_info_nickname,
                            '二级评论头像': ex_sub_user_info_image_url,
                            '二级评论内容': ex_sub_content,
                            '二级评论时间': ex_sub_create_time,
                            '二级评论回应的用户名': ex_sub_target_comment_nickname,
                        })
                        df = pd.DataFrame(data_list)
                        df.to_csv(csv_file_path, mode='a', index=False, encoding='utf-8-sig', header=False)
                        data_list.clear()  # 清空data_list

            except json.JSONDecodeError as e:
                print_and_log(f"Failed to parse JSON: {e}")
            except TypeError as e:
                print_and_log(f"Type error: {e}")

    def scroll_to_bottom(element, step=1200, timeout=20):
        start_time = time.time()
        
        packet = wp.listen.wait(timeout=1)
        handle_packet(packet)

        while True:
            scroll_top = wp.run_js("return arguments[0].scrollTop;", element)
            scroll_height = wp.run_js("return arguments[0].scrollHeight;", element)
            client_height = wp.run_js("return arguments[0].clientHeight;", element)
            
            # message = f"Current scroll top: {scroll_top}, Scroll height: {scroll_height}, Client height: {client_height}"
            # print_and_log(message)
            
            if scroll_top + client_height >= scroll_height:
                print_and_log("Reached the bottom of the page.")
                break
            
            element.scroll(step)
            packet = wp.listen.wait(timeout=1)
            handle_packet(packet)

            try:
                folded_comments = wp.eles('xpath://div[@class="show-more"]', timeout=0.5)
                for comment in folded_comments:
                    comment.click()
                    time.sleep(0.3)
                    packet = wp.listen.wait(timeout=1)
                    handle_packet(packet)
            except Exception as e:
                print_and_log(f"Error finding folded comments: {e}")
            
            if time.time() - start_time > timeout:
                print_and_log("Timeout: 在本Title中没有搜索到底部")
                break
        
        wp.ele('xpath://div[@class="close close-mask-dark"]').click()
        time.sleep(1)

    print_and_log(f"本次搜索的关键词：{search_query}")
    i = 1
    while search_max_num_of_title>i:
        try:
            print_and_log("click title")
            # wp.eles('xpath://a[@class="cover ld mask"]',timeout=3)[i%21].click()
            wp.eles('xpath://a[@class="cover mask ld"]',timeout=3)[i%21].click()
            print_and_log("click title ok")
            # 等待笔记页面加载完成
            time.sleep(1)

            # 查找滚动元素
            scroller_element = wp.ele('xpath://div[@class="note-scroller"]')

            scroll_to_bottom(element=scroller_element,step=search_step_in_one_title,timeout=search_time_in_one_title)
        except Exception as e:
            print_and_log(f"Error finding comments: {e}")
            print_and_log("在首页title，滚动一下。。。")
            ac.scroll(delta_y=1200)
            time.sleep(1.5)
        i+=1
        print_and_log(f"第{i}个title")


pandas_df = pd.read_csv(csv_file_path)

# 定义Excel文件路径
excel_file_path = args.excel_name

# 使用 ExcelWriter 和 xlsxwriter 引擎
with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
    # 将 DataFrame 写入 Excel 文件
    pandas_df.to_excel(writer, sheet_name='Sheet1', index=False)
    
    # 获取工作表对象
    worksheet = writer.sheets['Sheet1']
    
    # 设置每一列的宽度（可以根据实际内容调整）
    for i, column in enumerate(pandas_df.columns):
        # 计算每列的最大长度
        max_length = max(pandas_df[column].astype(str).map(len).max(), len(column))
        # 设置列宽为最大长度加2个字符空间
        worksheet.set_column(i, i, max_length + 2)

print(f"Excel文件已创建: {excel_file_path}")
