import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import escape
from pathlib import Path


SITE_NAME = "CityUpdater"
SITE_URL = "https://cityupdater.com"
CITY = "Chicago"
MAX_ARTICLES = 25

AMAZON_AFFILIATE_TAG = "custommade01-20"

CATEGORIES = {
    "news": {
        "query": "Chicago",
        "title": "Chicago News",
        "description": "Latest Chicago news, local headlines, breaking stories and city updates.",
        "amazon_query": "Chicago gifts",
        "deal_text": "Chicago Deals",
    },
    "restaurants": {
        "query": "Chicago restaurants",
        "title": "Chicago Restaurants",
        "description": "Latest Chicago restaurant news, openings, food trends and dining updates.",
        "amazon_query": "Chicago restaurant gifts kitchen",
        "deal_text": "Chicago Restaurant Deals",
    },
    "events": {
        "query": "Chicago events",
        "title": "Chicago Events",
        "description": "Latest Chicago events, festivals, concerts, exhibitions and local happenings.",
        "amazon_query": "Chicago event gifts",
        "deal_text": "Chicago Event Deals",
    },
    "jobs": {
        "query": "Chicago jobs",
        "title": "Chicago Jobs",
        "description": "Latest Chicago job market news, employment updates and career-related stories.",
        "amazon_query": "office work accessories",
        "deal_text": "Chicago Work Deals",
    },
    "real-estate": {
        "query": "Chicago real estate",
        "title": "Chicago Real Estate",
        "description": "Latest Chicago real estate news, housing updates, property trends and market developments.",
        "amazon_query": "home moving organization",
        "deal_text": "Chicago Home Deals",
    },
    "sports": {
        "query": "Chicago sports",
        "title": "Chicago Sports",
        "description": "Latest Chicago sports news, teams, games, players and sporting events.",
        "amazon_query": "Chicago sports",
        "deal_text": "Chicago Sports Deals",
    },
}


def get_google_news_rss_url(query):
    encoded_query = urllib.parse.quote(query)

    return (
        "https://news.google.com/rss/search"
        f"?q={encoded_query}"
        "&hl=en-US"
        "&gl=US"
        "&ceid=US:en"
    )


def get_amazon_url(query):
    encoded_query = urllib.parse.quote_plus(query)

    return (
        "https://www.amazon.com/s"
        f"?k={encoded_query}"
        f"&tag={AMAZON_AFFILIATE_TAG}"
        "&language=en_US"
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
          <h3>Updates are temporarily unavailable</h3>
          <p>Please check back later for fresh local updates.</p>
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
          <div class="meta">{meta}</div>

          <h3>
            <a href="{link}" target="_blank" rel="noopener noreferrer">
              {title}
            </a>
          </h3>

          <p>Read the full story from the original publisher.</p>

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


def build_navigation(current_slug):
    links = []

    for slug, data in CATEGORIES.items():
        label = data["title"].replace("Chicago ", "")

        if slug == current_slug:
            links.append(f"<strong>{label}</strong>")
        else:
            links.append(f'<a href="../{slug}/">{label}</a>')

    return "\n".join(links)


def build_page(slug, data, articles):
    articles_html = build_articles_html(articles)
    navigation = build_navigation(slug)

    updated = datetime.now(timezone.utc).strftime(
        "%B %d, %Y · %H:%M UTC"
    )

    canonical = f"{SITE_URL}/chicago/{slug}/"
    amazon_url = get_amazon_url(data["amazon_query"])

    return f"""<!DOCTYPE html>
<html lang="en">

<head>

  <meta charset="UTF-8">

  <meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
  >

  <title>{data["title"]} Today | CityUpdater</title>

  <meta
    name="description"
    content="{escape(data["description"], quote=True)}"
  >

  <meta
    name="robots"
    content="index, follow"
  >

  <link
    rel="canonical"
    href="{canonical}"
  >

  <meta
    property="og:title"
    content="{data["title"]} | CityUpdater"
  >

  <meta
    property="og:description"
    content="{escape(data["description"], quote=True)}"
  >

  <meta
    property="og:url"
    content="{canonical}"
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

    nav a,
    nav strong {{
      margin: 0 10px;
      font-weight: bold;
    }}

    nav a {{
      color: #111827;
      text-decoration: none;
    }}

    nav strong {{
      color: #2563eb;
    }}

    main {{
      max-width: 1000px;
      margin: auto;
      padding: 45px 20px;
    }}

    .intro {{
      margin-bottom: 25px;
    }}

    h2 {{
      font-size: 30px;
      margin-bottom: 15px;
    }}

    .updated {{
      color: #6b7280;
      font-size: 14px;
      margin-bottom: 20px;
    }}

    .deal-box {{
      background: white;
      border-radius: 12px;
      padding: 24px;
      margin: 25px 0 35px;
      box-shadow: 0 2px 8px rgba(0,0,0,.07);
      text-align: center;
    }}

    .deal-box h2 {{
      margin-top: 0;
      font-size: 24px;
    }}

    .deal-button {{
      display: inline-block;
      margin-top: 10px;
      padding: 15px 24px;
      background: #111827;
      color: white;
      text-decoration: none;
      font-weight: bold;
      border-radius: 8px;
    }}

    .deal-button:hover {{
      opacity: 0.9;
    }}

    .affiliate-note {{
      margin-top: 14px;
      font-size: 13px;
      color: #6b7280;
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

      nav a,
      nav strong {{
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

  <h1>{data["title"]}</h1>

  <p>{data["description"]}</p>

</header>


<nav>

  <a href="../">Chicago Home</a>

  {navigation}

</nav>


<main>

  <section class="intro">

    <h2>Latest {data["title"]}</h2>

    <p>
      CityUpdater collects recent stories and updates related to
      {data["title"]} from multiple news publishers.
    </p>

    <p class="updated">
      Last updated: {updated}
    </p>

  </section>


  <section class="deal-box">

    <h2>{data["deal_text"]}</h2>

    <p>
      Discover products and offers related to {data["title"]}.
    </p>

    <a
      class="deal-button"
      href="{amazon_url}"
      target="_blank"
      rel="nofollow sponsored noopener"
    >
      View {data["deal_text"]} on Amazon
    </a>

    <p class="affiliate-note">
      As an Amazon Associate, CityUpdater may earn from qualifying purchases.
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


def update_category(slug, data):
    print(f"Updating {data['title']}...")

    rss_url = get_google_news_rss_url(data["query"])

    xml_data = fetch_rss(rss_url)

    articles = parse_feed(xml_data)

    print(f"Found {len(articles)} articles.")

    html_page = build_page(
        slug,
        data,
        articles,
    )

    output_file = Path(
        f"chicago/{slug}/index.html"
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file.write_text(
        html_page,
        encoding="utf-8",
    )

    print(f"Updated: {output_file}")


def main():

    for slug, data in CATEGORIES.items():

        try:
            update_category(slug, data)

        except Exception as error:
            print(
                f"Error updating {slug}: {error}"
            )


if __name__ == "__main__":
    main()
