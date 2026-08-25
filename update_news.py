import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import escape
from pathlib import Path


# ---------------------------------------------------------
# CITYUPDATER - CHICAGO NEWS RSS GENERATOR
# ---------------------------------------------------------

CITY = "Chicago"
SITE_NAME = "CityUpdater"
SITE_URL = "https://cityupdater.com"
OUTPUT_FILE = Path("chicago/news/index.html")

SEARCH_QUERY = "Chicago"
MAX_ARTICLES = 25


def get_google_news_rss_url(query):
    encoded_query = urllib.parse.quote(query)

    return (
        "https://news.google.com/rss/search"
        f"?q={encoded_query}"
        "&hl=en-US"
        "&gl=US"
        "&ceid=US:en"
    )


def fetch_rss(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; CityUpdater/1.0; "
                "+https://cityupdater.com/)"
            )
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def format_date(date_string):
    if not date_string:
        return ""

    try:
        parsed = parsedate_to_datetime(date_string)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.strftime("%B %d, %Y · %H:%M UTC")

    except Exception:
        return escape(date_string)


def parse_feed(xml_data):
    root = ET.fromstring(xml_data)

    articles = []

    for item in root.findall(".//item"):
        title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()
        pub_date = item.findtext("pubDate", default="").strip()
        source_element = item.find("source")

        source = ""

        if source_element is not None and source_element.text:
            source = source_element.text.strip()

        if not title or not link:
            continue

        articles.append(
            {
                "title": title,
                "link": link,
                "date": format_date(pub_date),
                "source": source,
            }
        )

        if len(articles) >= MAX_ARTICLES:
            break

    return articles


def build_articles_html(articles):
    if not articles:
        return """
        <article class="news-item">
          <div class="meta">CityUpdater</div>
          <h3>Chicago news is temporarily unavailable</h3>
          <p>Please check back later for the latest Chicago headlines.</p>
        </article>
        """

    output = []

    for article in articles:
        title = escape(article["title"])
        link = escape(article["link"], quote=True)
        source = escape(article["source"])
        date = article["date"]

        meta_parts = []

        if source:
            meta_parts.append(source)

        if date:
            meta_parts.append(date)

        meta = " · ".join(meta_parts)

        output.append(
            f"""
        <article class="news-item">

          <div class="meta">
            {meta}
          </div>

          <h3>
            <a
              href="{link}"
              target="_blank"
              rel="noopener noreferrer"
            >
              {title}
            </a>
          </h3>

          <p>
            Read the full story from the original news publisher.
          </p>

          <a
            class="read-more"
            href="{link}"
            target="_blank"
            rel="noopener noreferrer"
          >
            Read full article →
          </a>

        </article>
        """
        )

    return "\n".join(output)


def build_page(articles):
    articles_html = build_articles_html(articles)

    updated = datetime.now(timezone.utc).strftime(
        "%B %d, %Y · %H:%M UTC"
    )

    return f"""<!DOCTYPE html>
<html lang="en">

<head>

  <meta charset="UTF-8">

  <meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
  >

  <title>
    Chicago News Today – Latest Local Headlines | CityUpdater
  </title>

  <meta
    name="description"
    content="Latest Chicago news today. Follow local headlines, breaking news, business, politics, transportation, events, sports and community updates from Chicago."
  >

  <meta
    name="robots"
    content="index, follow"
  >

  <link
    rel="canonical"
    href="https://cityupdater.com/chicago/news/"
  >

  <meta
    property="og:title"
    content="Chicago News Today | CityUpdater"
  >

  <meta
    property="og:description"
    content="Latest Chicago news, local headlines and city updates from multiple news sources."
  >

  <meta
    property="og:url"
    content="https://cityupdater.com/chicago/news/"
  >

  <meta
    property="og:type"
    content="website"
  >

  <style>

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: #f4f6f8;
      color: #1f2937;
      line-height: 1.6;
    }}

    header {{
      background: #111827;
      color: white;
      text-align: center;
      padding: 65px 20px;
    }}

    header h1 {{
      margin: 0;
      font-size: 46px;
    }}

    header p {{
      margin-top: 10px;
      font-size: 19px;
    }}

    nav {{
      background: white;
      border-bottom: 1px solid #ddd;
      padding: 14px 20px;
      text-align: center;
    }}

    nav a {{
      color: #111827;
      text-decoration: none;
      margin: 0 10px;
      font-weight: bold;
    }}

    main {{
      max-width: 1000px;
      margin: auto;
      padding: 45px 20px;
    }}

    .intro {{
      margin-bottom: 35px;
    }}

    h2 {{
      font-size: 30px;
      margin-bottom: 15px;
    }}

    .updated {{
      color: #6b7280;
      font-size: 14px;
      margin-bottom: 30px;
    }}

    .news-list {{
      display: grid;
      gap: 20px;
    }}

    .news-item {{
      background: white;
      padding: 25px;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,.07);
    }}

    .news-item h3 {{
      margin-top: 5px;
      margin-bottom: 10px;
      font-size: 23px;
      line-height: 1.35;
    }}

    .news-item h3 a {{
      color: #111827;
      text-decoration: none;
    }}

    .news-item h3 a:hover {{
      text-decoration: underline;
    }}

    .meta {{
      font-size: 14px;
      color: #6b7280;
    }}

    .read-more {{
      display: inline-block;
      margin-top: 5px;
      font-weight: bold;
      color: #1d4ed8;
      text-decoration: none;
    }}

    .read-more:hover {{
      text-decoration: underline;
    }}

    footer {{
      margin-top: 60px;
      background: #111827;
      color: #ccc;
      text-align: center;
      padding: 30px 20px;
    }}

    footer a {{
      color: white;
      text-decoration: none;
    }}

    @media (max-width: 600px) {{

      header h1 {{
        font-size: 36px;
      }}

      nav a {{
        display: inline-block;
        margin: 5px 7px;
      }}

      .news-item {{
        padding: 20px;
      }}

    }}

  </style>

</head>

<body>

<header>

  <h1>Chicago News</h1>

  <p>
    Latest local headlines and updates from Chicago
  </p>

</header>


<nav>

  <a href="../">Chicago</a>

  <a href="../events/">Events</a>

  <a href="../restaurants/">Restaurants</a>

  <a href="../jobs/">Jobs</a>

  <a href="../real-estate/">Real Estate</a>

  <a href="../sports/">Sports</a>

</nav>


<main>

  <section class="intro">

    <h2>Latest Chicago News</h2>

    <p>
      Follow the latest Chicago news and local headlines covering
      business, politics, neighborhoods, transportation, community
      developments, sports, entertainment and events.
    </p>

    <p class="updated">
      Last updated: {updated}
    </p>

  </section>


  <section class="news-list">

{articles_html}

  </section>

</main>


<footer>

  <p>
    <a href="../../">CityUpdater</a>
    –
    Local Updates from Cities Around the World
  </p>

  <p>
    © 2026 CityUpdater.com
  </p>

</footer>

</body>

</html>
"""


def main():

    rss_url = get_google_news_rss_url(SEARCH_QUERY)

    print("Downloading Chicago news...")
    print(rss_url)

    xml_data = fetch_rss(rss_url)

    articles = parse_feed(xml_data)

    print(f"Found {len(articles)} articles.")

    html_page = build_page(articles)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        html_page,
        encoding="utf-8"
    )

    print(
        f"Updated: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
