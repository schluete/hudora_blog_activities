#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cs.salesforce
import gdata.sites.client
import gdata.sites.data
import huTools.http
import htmlentitydefs
import os
import re
import sqlite3


BASE_URL = 'https://sites.google.com/a/hudora.de/intern'
GOOGLE_USERNAME = 'xxxxxxxxxxxxxx'
GOOGLE_PASSWORD = 'xxxxxxxxxxxxxx'
GOOGLE_DOMAIN = 'hudora.de'
GOOGLE_SITE = 'intern'

SALESFORCE_USERNAME = 'xxxxxxxxxxxxx'
SALESFORCE_PASSWORD = 'xxxxxxxxxxxxx'
SALESFORCE_SECURITY_TOKEN = 'xxxxxxxxxxxxx'


def chatter(status):
    """Post the given message to the user's chatter stream."""
    sforce = cs.salesforce.Client(SALESFORCE_USERNAME,
                                  SALESFORCE_PASSWORD,
                                  SALESFORCE_SECURITY_TOKEN)
    sforce.update({'type': 'User',
                   'Id': sforce.user_id,
                   'CurrentStatus': status})


def sites_client():
    """Create a fully functional google sites client instance """
    client = gdata.sites.client.SitesClient(source='activity-feed-observer',
                                                  site=GOOGLE_SITE,
                                                  domain=GOOGLE_DOMAIN)
    client.ssl = True
    client.ClientLogin(GOOGLE_USERNAME, GOOGLE_PASSWORD, client.source)
    return client


def was_tweeted_before(text):
    """Ueberprueft in einer kleinen SQlite-DB, ob das Blogposting bereits getweetet
       wurde oder nicht. Im Fehlerfall oder wenn's schon mal da war wird False geliefert,
       ansonsten ist das Ergebnis True """
    dbname = os.path.join(os.path.dirname(__file__), 'blog_activities.sqlite3')
    conn = sqlite3.connect(dbname)
    try:
        cur = conn.cursor()
        cur.execute("""create table if not exists tweets(
                       text varchar primary key not null, created_at timestamp);""")
        cur.execute("insert into tweets values('%s',datetime('now'));" % text.replace("'", '"'))
        conn.commit()
        return False
    except:
        return True
    finally:
        conn.close()


def check_for_new_blog_posts():
    """Ueberprueft den Activity Feed der Google Sites auf neue Blogposts
       und zwitschert, wenn sich ein neues Posting findet """
    client = sites_client()
    feed = client.GetActivityFeed()
    for entry in feed.entry:
        summary = str(entry.summary.html)
        regex = r'xhtml">(.+) created <html:a href="%s([^"]+)">([^<]+)</html:a>' % BASE_URL
        m = re.search(regex, summary)
        if m:
            url = _tiny_url(BASE_URL + m.group(2))
            title = _unescape(m.group(3))
            text = "%s - %s" % (title[0:130], url)
            if not was_tweeted_before(text):
                chatter(text)


def _tiny_url(url):
    """Does a API call to is.gd to get a shortened URL."""
    apiurl = 'http://is.gd/api.php?longurl='
    status, headers, content = huTools.http.fetch(apiurl + url, ua='cs.notifications')
    return content


def _unescape(text):
    """Removes HTML or XML character references and entities from a text string.
       http://effbot.org/zone/re-sub.htm#unescape-html
       @param text The HTML (or XML) source text.
       @return The plain text, as a Unicode string, if necessary."""
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


if __name__ == '__main__':
    check_for_new_blog_posts()
