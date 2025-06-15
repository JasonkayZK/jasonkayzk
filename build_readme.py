import feedparser
import httpx
import json
import pathlib
import re
import os
import datetime
import xml.etree.ElementTree as ET

blog_feed_url = "https://jasonkayzk.github.io/atom.xml"
wakatime_raw_url = "https://gist.githubusercontent.com/JasonkayZK/59ead22758ee823e48b558d3cff332f1/raw/"

root = pathlib.Path(__file__).parent.resolve()

def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)

def fetch_code_time():
    return httpx.get(wakatime_raw_url)

def fetch_blog_entries():
    entries = feedparser.parse(blog_feed_url)["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": entry["published"].split("T")[0],
        }
        for entry in entries
    ]

def fetch_douban_entries():
    douban_feed_url = "https://www.douban.com/feed/people/219317116/interests"
    entries = feedparser.parse(douban_feed_url)["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": datetime.datetime.strptime(entry["published"], "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d %H:%M:%S") if "published" in entry else "",
        }
        for entry in entries
    ]

if __name__ == "__main__":
    readme = root / "README.md"
    readme_contents = readme.open(encoding='UTF-8').read()

    code_time_text = "\n```text\n"+fetch_code_time().text+"\n```\n"
    rewritten = replace_chunk(readme_contents, "code_time", code_time_text)

    entries = fetch_blog_entries()[:10]
    entries_md = "\n".join(
        ["* <a href='{url}' target='_blank'>{title}</a> - {published}".format(**entry) for entry in entries]
    )
    rewritten = replace_chunk(rewritten, "blog", entries_md)

    douban_entries = fetch_douban_entries()[:10]
    douban_entries_md = "\n".join(
        ["* <a href='{url}' target='_blank'>{title}</a> - {published}".format(**entry) for entry in douban_entries]
    )
    rewritten = replace_chunk(rewritten, "douban", douban_entries_md)

    readme.open("w", encoding='UTF-8').write(rewritten)
