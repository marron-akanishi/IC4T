import os
import time
import datetime
import hashlib
import urllib
import sqlite3
import json
import tweepy as tp
import threading

def get_oauth(setting):
    """設定ファイルから各種キーを取得し、OAUTH認証を行う"""
    auth = tp.OAuthHandler(setting['twitter_API']['CK'], setting['twitter_API']['CS'])
    auth.set_access_token(setting['twitter_API']['Admin_Key'], setting['twitter_API']['Admin_Secret'])
    return auth

class StreamListener(tp.StreamListener):
    def __init__(self, api):
        """コンストラクタ"""
        self.api = api
        # 保存先
        self.old_date = datetime.date.today()
        self.reset()

    def on_status(self, status):
        """UserStreamから飛んできたStatusを処理する"""
        # Tweetに画像がついているか
        is_media = False
        # 日付の確認
        now = datetime.date.today()
        if now != self.old_date:
            self.old_date = now
            self.dbfile.commit()
            self.dbfile.close()
            self.logfile.close()
            self.reset()
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
            # 自分のツイートは飛ばす(RT対策)
            if status.user.screen_name != self.api.me().screen_name:
                for image in status_media['media']:
                    if image['type'] != 'photo':
                        break
                    # URL, ファイル名
                    media_url = image['media_url']
                    filename = str(self.fileno).zfill(5)
                    # # ダウンロード
                    # try:
                    #     temp_file = urllib.request.urlopen(media_url+":small").read()
                    # except:
                    #     self.logfile.write("Download Error<br>\n")
                    #     continue
                    # # md5の取得
                    # current_md5 = hashlib.md5(temp_file).hexdigest()
                    # # すでに取得済みの画像は飛ばす
                    # if current_md5 in self.file_md5:
                    #     self.logfile.write("geted  : " + status.user.screen_name + "-" + filename+"<br>\n")
                    #     continue
                    # self.file_md5.append(current_md5)
                    # ハッシュタグがあれば保存する
                    tags = []
                    if hasattr(status, "entities"):
                        if "hashtags" in status.entities:
                            for hashtag in status.entities['hashtags']:
                                tags.append(hashtag['text'])
                    # データベースに保存
                    SQL = "insert into list values (?,?,?,?,0,0,?,?)"
                    url = "https://twitter.com/" + status.user.screen_name + "/status/" + status.id_str
                    value = (filename, media_url, status.user.screen_name, url, str(tags).replace("'",""),
                            str(datetime.datetime.now()))
                    self.dbfile.execute(SQL, value)
                    self.dbfile.commit()
                    self.logfile.write("saved  : " + status.user.screen_name + "-" + filename+"<br>\n")
                    self.fileno += 1
                    temp_file = None

    def reset(self):
        """保存用のフォルダーを生成し、必要な変数を初期化する"""
        self.logfile = open(os.path.abspath(__file__).replace(os.path.basename(__file__),"DB/log/"+self.old_date.isoformat() + ".log"),'a')
        dbpath = os.path.abspath(__file__).replace(os.path.basename(__file__),"DB/admin/" + self.old_date.isoformat() + ".db")
        if os.path.exists(dbpath):
            self.logfile.write("DB file exist<br>\n")
            self.dbfile = sqlite3.connect(dbpath)
            cur = self.dbfile.cursor()
            cur.execute("select count(filename) from list")
            self.fileno = cur.fetchone()[0]
            cur.close()
        else:
            self.dbfile = sqlite3.connect(dbpath)
            self.dbfile.execute("create table list (filename, image, username, url, fav, retweet, tags, time)")
            self.fileno = 0
        self.file_hash = []
        self.file_md5 = []

class TLThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
 
    def run(self):
        setting = json.load(open("setting.json"))
        auth = get_oauth(setting)
        stream = tp.Stream(auth, StreamListener(tp.API(auth)), secure=True)
        print('Start Streaming!')
        if setting['Debug']:
            try:
                stream.userstream()
            except KeyboardInterrupt:
                exit()
        else:
            while True:
                try:
                    stream.userstream()
                except KeyboardInterrupt:
                    exit()
                except:
                    print('UserStream Error')
                    time.sleep(60)