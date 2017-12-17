import os
import time
import datetime
import hashlib
import urllib
import sqlite3
import json
import tweepy as tp

def reset(dbfile, mode):
    """保存用のフォルダーを生成し、必要な変数を初期化する"""
    try:
        dbfile.execute("drop table result")
    except:
        pass
    try:
        dbfile.execute("drop table {}".format(mode))
    except:
        pass
    dbfile.execute("vacuum")
    dbfile.execute("create table {} (filename, image, username, url, tags, time)".format(mode))
    dbfile.execute("create table result (mode, time, image_count, tweet_count)")
    dbfile.commit()

def on_status(status, dbfile, mode, id, file_md5):
    """UserStreamから飛んできたStatusを処理する"""
    return_md5 = []
    # ツイートについてる画像枚数
    image_count = 0
    # Tweetに画像がついているか
    is_media = False
    # TweetがRTかどうか
    if hasattr(status, "retweeted_status"):
        status = status.retweeted_status
    # Tweetが引用ツイートかどうか
    if hasattr(status, "quoted_status"):
        status = status.quoted_status
    # 複数枚の画像ツイートのとき
    if hasattr(status, "extended_entities"):
        if 'media' in status.extended_entities:
            status_media = status.extended_entities
            is_media = True
    # 一枚の画像ツイートのとき
    elif hasattr(status, "entities"):
        if 'media' in status.entities:
            status_media = status.entities
            is_media = True

    # 画像がついていたとき
    if is_media:
        for image in status_media['media']:
            if image['type'] != 'photo':
                break
            # URL, ファイル名
            media_url = image['media_url']
            filename = str(id).zfill(5)
            # ダウンロード
            # try:
            #     temp_file = urllib.request.urlopen(media_url+":small").read()
            # except:
            #     continue
            # # md5の取得
            # current_md5 = hashlib.md5(temp_file).hexdigest()
            # # すでに取得済みの画像は飛ばす
            # if current_md5 in file_md5:
            #     continue
            # # 取得済みとしてハッシュ値を保存
            # return_md5.append(current_md5)
            # ハッシュタグがあれば保存する
            tags = []
            if hasattr(status, "entities"):
                if "hashtags" in status.entities:
                    for hashtag in status.entities['hashtags']:
                        tags.append(hashtag['text'])
            # データベースに保存
            SQL = "insert into {} values (?,?,?,?,?,?)".format(mode)
            url = "https://twitter.com/" + status.user.screen_name + "/status/" + status.id_str
            value = (filename, media_url.replace('http://','https://'), status.user.screen_name, url, str(tags).replace("'",""), 
                    str(datetime.datetime.now()))
            dbfile.execute(SQL, value)
            dbfile.commit()
            id += 1
            temp_file = None
            image_count += 1
    return id, image_count, return_md5

def getTweets(api, mode, count, query):
    start = time.time()

    dbpath = os.path.abspath(__file__).replace(os.path.basename(__file__),"/DB/user/"+ api.me().id_str + ".db")
    dbfile = sqlite3.connect(dbpath)
    
    # DBのリセット等
    reset(dbfile, mode)
    tweet_count = 0
    image_count = 0
    temp_count = 0
    id = 0
    tweet_id = []
    file_md5 = []
    return_md5 = []
    # 取得モード
    if mode == "timeline":
        for status in tp.Cursor(api.home_timeline).items(count):
            if status.id in tweet_id:
                continue
            else:
                tweet_id.append(status.id)
            id, temp_count, return_md5 = on_status(status, dbfile, mode, id, file_md5)
            file_md5 += return_md5
            image_count += temp_count
            tweet_count += 1
    elif mode == "fav":
        for status in tp.Cursor(api.favorites).items(count):
            if status.id in tweet_id:
                continue
            else:
                tweet_id.append(status.id)
            id, temp_count, return_md5 = on_status(status, dbfile, mode, id, file_md5)
            file_md5 += return_md5
            image_count += temp_count
    elif mode == "user":
        for status in tp.Cursor(api.user_timeline, screen_name=query).items(count):
            if status.id in tweet_id:
                continue
            else:
                tweet_id.append(status.id)
            id, temp_count, return_md5 = on_status(status, dbfile, mode, id, file_md5)
            file_md5 += return_md5
            image_count += temp_count
            tweet_count += 1
    elif mode == "list":
        listurl = query.replace("https://","")
        owner = listurl.split("/")[1]
        slug = listurl.split("/")[3]
        for status in tp.Cursor(api.list_timeline, owner_screen_name=owner, slug=slug).items(count):
            if status.id in tweet_id:
                continue
            else:
                tweet_id.append(status.id)
            id, temp_count, return_md5 = on_status(status, dbfile, mode, id, file_md5)
            file_md5 += return_md5
            image_count += temp_count
            tweet_count += 1
    elif mode == "tag":
        for status in tp.Cursor(api.search, q="#" + query).items(count):
            if status.id in tweet_id:
                continue
            else:
                tweet_id.append(status.id)
            id, temp_count, return_md5 = on_status(status, dbfile, mode, id, file_md5)
            file_md5 += return_md5
            image_count += temp_count
            tweet_count += 1
    elif mode == "keyword":
        for status in tp.Cursor(api.search, q=query).items(count):
            if status.id in tweet_id:
                continue
            else:
                tweet_id.append(status.id)
            id, temp_count, return_md5 = on_status(status, dbfile, mode, id, file_md5)
            file_md5 += return_md5
            image_count += temp_count
            tweet_count += 1
    
    elapsed_time = time.time() - start
    # 実行時間,全ツイート数,全画像枚数をデータベースに
    SQL = "insert into result values (?,?,?,?)"
    value = (mode, str(elapsed_time), str(image_count), str(tweet_count))
    dbfile.execute(SQL, value)
    dbfile.commit()
        
