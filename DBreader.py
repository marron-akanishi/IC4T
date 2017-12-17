import os
import sqlite3
import requests
import json

# DBからファイルリスト取得
def get_list(path, table):
    images = []
    result = { 'time' : 0, 'image_count' : 0, 'tweet_count' : 0}
    if os.path.exists(path):
        conn = sqlite3.connect(path)
    else:
        raise ValueError
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("select count(filename) from {}".format(table))
    count = cur.fetchone()[0]
    cur.execute( "select * from {} order by filename".format(table) )
    for row in cur:
        images.append({"id":int(row["filename"]), "tags":row["tags"][1:-1], "image":row["image"]})
    if table != "list":
        cur.execute("select * from result")
        for row in cur:
            if(row["mode"] == table):
                result["time"] = int(float(row["time"]))
                result["image_count"] = int(row["image_count"])
                result["tweet_count"] = int(row["tweet_count"])
                break
    cur.close()
    conn.close()
    return images,count,result

# DBからIDで検索
def search_db(userid, dbfile, table):
    images = []
    if os.path.exists(dbfile):
        conn = sqlite3.connect(dbfile)
    else:
        raise ValueError
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("select count(filename) from {} where username like '%{}%'".format(table,userid))
    count = cur.fetchone()[0]
    cur.execute( "select * from {} where username like '%{}%'".format(table,userid) )
    for row in cur:
        images.append({"id":int(row["filename"]), "tags":row["tags"][1:-1], "image":row["image"]})
    cur.close()
    conn.close()
    return images,count

# DBから詳細情報取得
def get_detail(filename, dbfile, table):
    detail = {}
    if os.path.exists(dbfile):
        conn = sqlite3.connect(dbfile)
    else:
        raise ValueError
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("select count(filename) from {}".format(table))
    count = cur.fetchone()[0]
    cur.execute( "select * from {} where filename = '{}'".format(table,str(filename).zfill(5)) )
    row = cur.fetchone()
    detail = {
        "id":int(row["filename"]),
        "image":row["image"],
        "url":row["url"],
        "userid":row["username"],
        "tags":row["tags"][1:-1],
        "time":row["time"]
    }
    cur.close()
    conn.close()
    temp, idinfo = search_db(detail["userid"], dbfile, table)
    try:
        html = get_html(detail["url"])
    except:
        html = "<p>ツイートが見つかりません</p>"
    return detail,html,idinfo,count

# 埋め込み用HTMLの取得(detail用)
def get_html(url):
    try:
        r = requests.get("https://publish.twitter.com/oembed", {"url":url})
        data = json.loads(r.text)
        return data["html"]
    except:
        raise
