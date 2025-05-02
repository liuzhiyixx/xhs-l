# 前置条件
**Windows中装有谷歌浏览器，并将其设置为默认**

# 操作步骤
## 1.双击执行open_redbook.exe，打开小红书自行完成登录

## 2.登录成功后不要关闭谷歌页面，在listen_test.exe所在目录输入cmd，打开命令行
![image](https://github.com/user-attachments/assets/1ac1fd8c-9c70-4174-aacc-58d38217cb26)
![image](https://github.com/user-attachments/assets/4ab59400-4ea2-4029-adb7-7aca22a2db42)
![image](https://github.com/user-attachments/assets/fb350c1f-1828-47ec-98c2-c52e25c65c43)
## 3.在命令行中执行
例如:需要搜索早饭，搜索12个帖子，可以在命令行中输入以下内容，会在该目录下生成excel和csv文件：
.\listen_test.exe --query 早饭 --max-title 12 --excel-name 早饭.xlsx

![image](https://github.com/user-attachments/assets/3c6b4ce7-045e-474c-9900-c232c5b18c59)
![image](https://github.com/user-attachments/assets/62112d6a-c181-409b-b4ae-b9b061829482)

## 4.listen_test.exe的可选参数
--query			'搜索关键词'
--max-title :  		'最大搜索的title数量'
--step :  			'在一个title中搜索每页滚动的步长'
--time-in-title :  	'在一个title中搜索的最大时间'
--excel-name :  	'自己指定excel文件名'
--csv-name :  		'自己指定csv文件名'

# 注意
csv文件可能会由格式问题乱码

# 声明
本工具仅供个人学习和研究，切勿将其用于未经授权的数据抓取、商业分发或任何其他活动。

