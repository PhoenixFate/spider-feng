import datetime
import time
import pymongo  # 引入pymongo模块
import requests
import re


def save_to_mongo(news_array):
    client = pymongo.MongoClient(host='114.67.89.253', port=40017)  # 进行连接
    db = client.feng  # 指定数据库
    db.authenticate("feng", "feng")
    collection = db.fengNews  # 指定集合
    news_detail_collection = db.fengNewsDetail
    try:
        for news in news_array:
            print(news["tid"])
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            news["createTime"] = create_time
            result = collection.find_one({'tid': news["tid"]})
            # print(result)
            # 不存在 则插入
            if result is None:
                print("insert one news")
                collection.insert(news)
            detail_result = news_detail_collection.find_one({'tid': news["tid"]})
            if detail_result is None:
                print("detail insert one")
                data = get_news_detail(news)
                news_detail_collection.insert(data)
    except Exception as e:
        print('存储到MongoDb失败', e)


def get_news_detail(news):
    session = requests.session()
    news_detail_url = "https://www.feng.com/post/" + str(news["tid"])
    headers = {
        "Origin": "https://www.feng.com",
        "Referer": "https://www.feng.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.37"}
    response = session.get(url=news_detail_url, headers=headers)
    message = re.findall(r'message:(.*?),', response.content.decode("unicode_escape").encode('latin1').decode('utf-8'))
    message[0] = message[0].replace("\"", "\'")[1:-1]
    subject = re.findall(r'subject:(.*?),', response.content.decode('utf-8'))
    subject_data = subject[0][1:-1]
    subject_data = subject_data.encode("utf-8").decode("unicode_escape").encode('latin1').decode('utf-8')
    if subject_data.endswith("\\n"):
        subject_data = subject[0][1:-3]
    introduction = re.findall(r'intro:(.*?),',
                              response.content.decode('utf-8'))
    introduction_data = introduction[0][1:-1]
    if introduction_data.endswith("\\n"):
        introduction_data = introduction[0][1:-3]
    update_time = re.findall(r'updateTime:(.*?),',
                             response.content.decode('utf-8'))
    year = datetime.datetime.now().year
    data = {"message": message[0], "subject": subject_data, "introduction": introduction_data,
            "updateTime": str(year) + "-" + update_time[0][1:-1],
            "tid": news["tid"], "createTime": news["createTime"]}
    return data
