#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import re
import os
import gdata.sites.client
import gdata.sites.data
import sqlite3
from cs.zwitscher import zwitscher


BASE_URL = 'https://sites.google.com/a/hudora.de/intern'
GOOGLE_USERNAME = 'xxxxxxxxxxxxxx'
GOOGLE_PASSWORD = 'xxxxxxxxxxxxxx'
GOOGLE_DOMAIN = 'hudora.de'
GOOGLE_SITE = 'intern'
ZWITSCHR_USERNAME = 'xxxxxxxxxxxxxx'
ZWITSCHR_PASSWORD = 'xxxxxxxxxxxxxx'


def sites_client():
    """ create a fully functional google sites client instance """
    client = gdata.sites.client.SitesClient(source='activity-feed-observer',
                                                  site=GOOGLE_SITE,
                                                  domain=GOOGLE_DOMAIN)
    client.ssl = True
    client.ClientLogin(GOOGLE_USERNAME, GOOGLE_PASSWORD, client.source)
    return client


def was_tweeted_before(text):
    """ ueberprueft in einer kleinen SQlite-DB, ob das Blogposting bereits getweetet
        wurde oder nicht. Im Fehlerfall oder wenn's schon mal da war wird False geliefert,
        ansonsten ist das Ergebnis True """
    dbname = os.path.join(os.path.dirname(__file__), 'blog_activities.sqlite3')
    conn = sqlite3.connect(dbname)
    try:
        cur = conn.cursor()
        cur.execute("""create table if not exists tweets(
                       text varchar primary key not null, created_at timestamp);""")
        cur.execute("insert into tweets values('%s',date('now'));" % text.replace("'", '"'))
        conn.commit()
        return False
    except:
        return True
    finally:
        conn.close()


def check_for_new_blog_posts():
    """ ueberprueft den Activity Feed der Google Sites auf neue Blogposts
        und zwitschert, wenn sich ein neues Posting findet """
    client = sites_client()
    feed = client.GetActivityFeed()
    for entry in feed.entry:
        summary = str(entry.summary.html)
        regex = r'xhtml">(.+) created <html:a href="%s([^"]+)">([^<]+)</html:a>' % BASE_URL
        m = re.search(regex, summary)
        if m:
            url = BASE_URL + m.group(2)
            title = m.group(3)
            text = "%s - %s" % (title[0:130], url)
            if not was_tweeted_before(text):
                zwitscher(text, username=ZWITSCHR_USERNAME, password=ZWITSCHR_PASSWORD)
            
if __name__ == '__main__':
    check_for_new_blog_posts()
