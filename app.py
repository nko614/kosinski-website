import os
import re
from datetime import datetime
from flask import Flask, render_template, abort

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

POSTS_DIR = os.path.join(os.path.dirname(__file__), 'posts')


def parse_post(filename):
    """Parse a markdown blog post with YAML-style frontmatter."""
    filepath = os.path.join(POSTS_DIR, filename)
    with open(filepath, 'r') as f:
        text = f.read()

    # Split frontmatter from content
    parts = text.split('---', 2)
    if len(parts) < 3:
        return None

    frontmatter = parts[1].strip()
    body = parts[2].strip()

    # Parse frontmatter
    meta = {}
    for line in frontmatter.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            meta[key.strip()] = val.strip()

    slug = filename.replace('.md', '')

    return {
        'slug': slug,
        'title': meta.get('title', slug),
        'date': meta.get('date', ''),
        'summary': meta.get('summary', ''),
        'body': body,
    }


def render_markdown(text):
    """Simple markdown to HTML converter."""
    try:
        import markdown
        return markdown.markdown(text, extensions=['fenced_code'])
    except ImportError:
        # Fallback: basic conversion without the markdown library
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
        paragraphs = html.split('\n\n')
        html = ''.join(
            f'<p>{p.strip()}</p>' if not p.strip().startswith('<h') else p
            for p in paragraphs if p.strip()
        )
        return html


def get_all_posts():
    """Load and sort all blog posts by date (newest first)."""
    posts = []
    if not os.path.exists(POSTS_DIR):
        return posts
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith('.md'):
            post = parse_post(filename)
            if post:
                posts.append(post)
    posts.sort(key=lambda p: p['date'], reverse=True)
    return posts


# Press items
DAILY_QUOTES = [
    {'text': 'The best thing you can possibly do with your life is to tackle the motherfucking shit out of it.', 'author': 'Cheryl Strayed'},
    {'text': 'One man that has a mind and knows it can always beat ten men who haven\'t and don\'t.', 'author': 'George Bernard Shaw'},
    {'text': 'The world is a very malleable place. If you know what you want, and you go for it with maximum energy and drive and passion, the world will often reconfigure itself around you much more quickly and easily than you would think.', 'author': 'Marc Andreessen'},
    {'text': 'Do not anticipate trouble, or worry about what may never happen. Keep in the sunlight.', 'author': 'Benjamin Franklin'},
    {'text': 'I constantly see people rise in life who are not the smartest, sometimes not even the most diligent, but they are learning machines. They go to bed every night a little wiser than they were when they got up and boy does that help, particularly when you have a long run ahead of you.', 'author': 'Charlie Munger'},
    {'text': 'People are always blaming their circumstances for what they are. I don\'t believe in circumstances. The people who get on in this world are the people who get up and look for the circumstances they want, and if they can\'t find them, make them.', 'author': 'George Bernard Shaw'},
    {'text': 'I never allow myself to hold an opinion on anything that I don\'t know the other side\'s argument better than they do.', 'author': 'Charlie Munger'},
    {'text': 'There is no better teacher than history in determining the future... There are answers worth billions of dollars in 30$ history book.', 'author': 'Charlie Munger'},
    {'text': 'To get what you want, you have to deserve what you want. The world is not yet a crazy enough place to reward a whole bunch of undeserving people.', 'author': 'Charlie Munger'},
    {'text': 'Honesty is a very expensive gift, Don\'t expect it from cheap people.', 'author': 'Warren Buffett'},
    {'text': 'Somebody once said that in looking for people to hire, you look for three qualities: integrity, intelligence, and energy. And if you don\'t have the first, the other two will kill you.', 'author': 'Warren Buffett'},
    {'text': 'Tell me who your heroes are and I\'ll tell you how you\'ll turn out to be.', 'author': 'Warren Buffett'},
    {'text': 'I could end the deficit in five minutes. You just pass a law that says that anytime there is a deficit of more than 3% of GDP all sitting members of congress are ineligible for reelection.', 'author': 'Warren Buffett'},
    {'text': 'Intensity is the price of excellence.', 'author': 'Warren Buffett'},
    {'text': 'Take time to deliberate, but when the time for action comes, stop thinking and go in.', 'author': 'Napoleon Bonaparte'},
    {'text': 'A leader is a dealer in hope.', 'author': 'Napoleon Bonaparte'},
    {'text': 'The reason most people fail instead of succeed is they trade what they want most for what they want at the moment.', 'author': 'Napoleon Bonaparte'},
    {'text': 'Circumstances - what are circumstances? I make circumstances.', 'author': 'Napoleon Bonaparte'},
    {'text': 'All great events hang by a single thread. The clever man takes advantage of everything, neglects nothing that may give him some added opportunity; the less clever man, by neglecting one thing, sometimes misses everything.', 'author': 'Napoleon Bonaparte'},
    {'text': 'If the art of war were nothing but the art of avoiding risks, glory would become the prey of mediocre minds.... I have made all the calculations; fate will do the rest.', 'author': 'Napoleon Bonaparte'},
    {'text': 'At the moment of commitment the entire universe conspires to assist you.', 'author': 'Johann Wolfgang von Goethe'},
]

DAILY_SONGS = [
    {'title': 'Groove Movement - Edit', 'artist': '', 'url': 'https://open.spotify.com/track/7wKNfmCbxSFxhVOKc6S0tJ'},
    {'title': 'Bitter Sweet Symphony', 'artist': 'The Verve', 'url': 'https://open.spotify.com/track/57iDDD9N9tTWe75x6qhStw'},
    {'title': 'Joanna - Tony De Vit V2 Remix', 'artist': '', 'url': 'https://open.spotify.com/track/1ywLToC7aeJEdnZQcLiisN'},
    {'title': 'Simple Twist of Fate', 'artist': 'Bob Dylan', 'url': 'https://open.spotify.com/track/3wAX3qn53iQUFE84hpfeen'},
    {'title': 'Servo', 'artist': '', 'url': 'https://open.spotify.com/track/0tQumXkf8SIbqvoNvcPVBY'},
    {'title': 'Silent Acknowledgement', 'artist': '', 'url': 'https://open.spotify.com/track/3wFVKi2sXsM2s106hOKlnJ'},
    {'title': 'Shake The Walls', 'artist': '', 'url': 'https://open.spotify.com/track/3MWgDB4iiM7JwjFI0qAMcX'},
    {'title': 'Lovers In The Dance', 'artist': '', 'url': 'https://open.spotify.com/track/2VSnKYC9w0j8kireb1THn5'},
]


PRESS_ITEMS = [
    {
        'source': 'Buffalo Business First',
        'title': 'Odoo adding jobs in Buffalo with new downtown office expansion',
        'date': 'November 2025',
        'url': 'https://www.bizjournals.com/buffalo/news/2025/11/19/odoo-jobs-buffalo-downtown-office.html',
    },
    {
        'source': 'Buffalo News',
        'title': '1,000 employees in Buffalo: It\'s not an unrealistic goal for Odoo, top local executive says',
        'date': 'August 2024',
        'url': 'https://buffalonews.com/news/local/business/employment/article_5112f8ae-6184-11ef-80d8-63e973f29587.html',
    },
    {
        'source': 'Buffalo News',
        'title': 'Turns out, there is such a thing as a free lunch at Buffalo\'s Odoo',
        'date': 'October 2023',
        'url': 'https://buffalonews.com/news/local/business/article_18bd1528-82b0-45be-b090-d6a8750680cf.html',
    },
    {
        'source': 'Buffalo Business First',
        'title': 'Odoo deal for Fountain Plaza: Buffalo reactions to the sale',
        'date': 'September 2023',
        'url': 'https://www.bizjournals.com/buffalo/news/2023/09/07/odoo-deal-fountain-plaza-buffalo-reactions-sale.html',
    },
    {
        'source': 'Buffalo News',
        'title': 'Odoo to add 350 jobs over five years in WNY as part of 40 Fountain Plaza purchase',
        'date': 'August 2023',
        'url': 'https://buffalonews.com/news/local/business/article_5835b8a0-41f6-11ee-a291-fb7487600473.html',
    },
    {
        'source': 'Buffalo Rising',
        'title': 'Big Deal: Odoo to expand with Fountain Plaza office purchase',
        'date': 'August 2023',
        'url': 'https://www.buffalorising.com/2023/08/big-deal-odoo-to-expand-with-fountain-plaza-office-purchase/',
    },
    {
        'source': 'WGRZ (Channel 2)',
        'title': 'Buffalo software company growth outpaces expectations',
        'date': '2023',
        'url': 'https://www.wgrz.com/article/money/business/business-first/software-company-odoos-growth-outpaces-expectations/71-233594a7-1d4d-4b2f-9489-b1e3eb183b0e',
    },
    {
        'source': '43North',
        'title': 'The Odoo playbook and the players who helped lure the company to Buffalo',
        'date': 'April 2020',
        'url': 'https://43north.org/the-odoo-playbook-and-the-players-who-helped-lure-the-company-to-buffalo/',
    },
    {
        'source': 'Invest Buffalo Niagara',
        'title': 'POD: Nick Kosinski, on Odoo\'s East Coast HQ',
        'date': 'June 2020',
        'url': 'https://info.buffaloniagara.org/blog/pod-nick-kosinski-on-odoos-east-coast-hq',
    },
    {
        'source': 'San Francisco Business Times',
        'title': 'Odoo opts to grow in Buffalo instead of San Francisco',
        'date': '2020',
        'url': 'https://www.bizjournals.com/sanfrancisco/c/oodo-opts-to-grow-in-buffalo-instead-of-san.html',
    },
]


@app.context_processor
def inject_globals():
    today = datetime.now()
    day_of_year = today.timetuple().tm_yday
    quote = DAILY_QUOTES[day_of_year % len(DAILY_QUOTES)]
    song = DAILY_SONGS[day_of_year % len(DAILY_SONGS)]
    return {'now': today, 'daily_quote': quote, 'daily_song': song}


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/resume')
def resume():
    return render_template('resume.html')


@app.route('/terminal')
def terminal():
    return render_template('terminal.html')


@app.route('/blog')
def blog():
    posts = get_all_posts()
    return render_template('blog.html', posts=posts)


@app.route('/blog/<slug>')
def blog_post(slug):
    posts = get_all_posts()
    post = next((p for p in posts if p['slug'] == slug), None)
    if not post:
        abort(404)
    post['html'] = render_markdown(post['body'])
    return render_template('blog_post.html', post=post)


@app.route('/contact')
def contact():
    return render_template('contact.html')


WEB_APPS = [
    {
        'name': 'Mental Models Guide',
        'desc': 'Interactive guide to 20+ mental models across six disciplines. Calculators, examples, and a quiz.',
        'url': 'http://167.71.247.51/mental_models/',
    },
    {
        'name': 'Should I Customize?',
        'desc': 'Decision tool for Odoo prospects evaluating whether to customize or stay standard.',
        'url': 'https://shouldicustomize.com',
    },
    {
        'name': 'I Heart Finance',
        'desc': 'Financial education platform with interactive tools and calculators.',
        'url': 'https://iheartfinance.com',
    },
    {
        'name': 'Death to Mortgage',
        'desc': 'Mortgage payoff calculator and strategy tool.',
        'url': 'https://deathtomortgage.com',
    },
]

ODOO_APPS = [
    {
        'name': 'Google Maps Route Optimization',
        'desc': 'Odoo module that optimizes delivery routes using the Google Maps API. Geocodes partner addresses and calculates optimal stop sequences for stock pickings.',
        'url': 'https://github.com/nko614/odoo_customizations/tree/main/delivery_optimizer',
    },
]


BOOKS = [
    {
        'title': 'The Wealth of Nations',
        'author': 'Adam Smith',
        'note': 'The original. Essential for understanding how economies and incentives work.',
    },
    {
        'title': 'Poor Charlie\'s Almanack',
        'author': 'Charlie Munger',
        'note': 'The playbook for mental models, multidisciplinary thinking, and avoiding stupidity.',
    },
    {
        'title': 'The Intelligent Investor',
        'author': 'Benjamin Graham',
        'note': 'By far the best book on investing ever written. The foundation of value investing.',
    },
    {
        'title': 'Shoe Dog',
        'author': 'Phil Knight',
        'note': 'The raw, honest story of building Nike from nothing. A masterclass in grit and perseverance.',
    },
    {
        'title': 'Influence',
        'author': 'Robert Cialdini',
        'note': 'The psychology of why people say yes. Required reading for anyone in business.',
    },
    {
        'title': 'The Essays of Warren Buffett',
        'author': 'Warren Buffett, edited by Lawrence Cunningham',
        'note': 'Decades of shareholder letters distilled into lessons on business, investing, and management.',
    },
    {
        'title': 'Seeking Wisdom: From Darwin to Munger',
        'author': 'Peter Bevelin',
        'note': 'A synthesis of mental models with biology, psychology, and physics.',
    },
    {
        'title': 'Meditations',
        'author': 'Marcus Aurelius',
        'note': 'Private journals of a Roman emperor. Timeless wisdom on discipline, perspective, and self-control.',
    },
    {
        'title': 'Thinking, Fast and Slow',
        'author': 'Daniel Kahneman',
        'note': 'How the two systems in your brain shape every decision you make. Changes how you think about thinking.',
    },
    {
        'title': 'Where Are the Customers\' Yachts?',
        'author': 'Fred Schwed Jr.',
        'note': 'A funny, honest look at Wall Street\'s self-serving nature.',
    },
]


@app.route('/projects')
def projects():
    return render_template('projects.html', web_apps=WEB_APPS, odoo_apps=ODOO_APPS)


@app.route('/reading')
def reading():
    return render_template('reading.html', books=BOOKS)


@app.route('/activities')
def activities():
    return render_template('activities.html')


@app.route('/press')
def press():
    return render_template('press.html', press_items=PRESS_ITEMS)


if __name__ == '__main__':
    app.run(debug=True, port=5013)
