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
        'name': 'Salesforce Integration',
        'desc': 'Sync leads, contacts, and opportunities between Salesforce CRM and Odoo in real time.',
        'price': '$2,999',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M10.05 5.64c.66-.7 1.58-1.14 2.6-1.14 1.3 0 2.43.7 3.06 1.73.54-.24 1.13-.37 1.75-.37 2.4 0 4.34 1.95 4.34 4.36 0 2.4-1.95 4.35-4.34 4.35-.28 0-.56-.03-.82-.08-.52 1.17-1.7 1.98-3.06 1.98-.44 0-.86-.09-1.24-.25-.56 1.34-1.87 2.28-3.41 2.28-1.55 0-2.87-.95-3.42-2.3-.2.03-.41.05-.63.05-2.13 0-3.88-1.75-3.88-3.88 0-1.53.9-2.86 2.19-3.48-.12-.4-.18-.82-.18-1.26C2.99 5.55 4.94 3.5 7.35 3.5c1.31 0 2.15.58 2.7 2.14z" fill="#00A1E0"/></svg>',
    },
    {
        'name': 'NetSuite Migration Tool',
        'desc': 'Structured data migration from NetSuite to Odoo — customers, items, transactions, and history.',
        'price': '$2,999',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M4 6h16v2H4V6zm0 5h16v2H4v-2zm0 5h16v2H4v-2z" fill="#1B3A55"/><path d="M17 4l3 4-3 4" stroke="#4285F4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M7 12l-3 4 3 4" stroke="#4285F4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    },
    {
        'name': 'QuickBooks Integration',
        'desc': 'Sync invoices, payments, chart of accounts, and journal entries between QuickBooks and Odoo.',
        'price': '$6,899',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="#2CA01C"/><path d="M9.5 8v8h1.5v-2.5h1c1.93 0 3.5-1.57 3.5-3.5v-.5C15.5 8 14.5 8 14 8H9.5zm1.5 1.5h2c.55 0 1 .45 1 1s-.45 1-1 1h-2v-2z" fill="#2CA01C"/></svg>',
    },
    {
        'name': 'HubSpot Integration',
        'desc': 'Push Odoo contacts and deals to HubSpot, and pull marketing data back into Odoo.',
        'price': '$1,899',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="15" cy="9.5" r="2.5" stroke="#FF7A59" stroke-width="2" fill="none"/><circle cx="9" cy="14.5" r="2" stroke="#FF7A59" stroke-width="2" fill="none"/><circle cx="18" cy="17" r="1.5" fill="#FF7A59"/><circle cx="6" cy="6" r="1.5" fill="#FF7A59"/><line x1="13" y1="11" x2="10.5" y2="13" stroke="#FF7A59" stroke-width="1.5"/><line x1="17" y1="11.5" x2="17.5" y2="15.5" stroke="#FF7A59" stroke-width="1.5"/><line x1="7.5" y1="7.5" x2="8" y2="12.5" stroke="#FF7A59" stroke-width="1.5"/></svg>',
    },
    {
        'name': 'Shopify Integration',
        'desc': 'Two-way sync of products, orders, inventory, and customers between Shopify and Odoo.',
        'price': '$1,299',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M15.34 3.04c-.07-.04-.14-.02-.18.04l-1.47 2.71-.63-.17s-.16-1.07-.18-1.2c-.02-.12-.1-.18-.18-.19h-.01L11.46 4l-1.88 10.8 6.73 1.27L19 5.42s-3.57-2.34-3.66-2.38zM12.4 7.24l-.55 1.93s-.62-.32-1.36-.26c-1.08.07-1.1.75-1.08.93.06.96 2.58 1.17 2.72 3.42.11 1.77-1 2.98-2.6 3.08-1.92.12-2.98-.96-2.98-.96l.4-1.62s1.07.77 1.93.71c.56-.04.76-.47.74-.78-.08-1.25-2.13-1.18-2.26-3.24-.11-1.73 1.07-3.49 3.57-3.65.96-.05 1.47.2 1.47.2z" fill="#95BF47"/><path d="M14.59 3.66l-.91-.25c0-.01-.02-.79-.34-1.2C12.92 1.66 12.24 1.7 12.24 1.7l-.27 1.56-.63-.17.18 1.2.63.17.55-1.93s-.51-.24-1.47-.2c-2.5.16-3.68 1.92-3.57 3.65.13 2.06 2.18 1.99 2.26 3.24.02.31-.18.74-.74.78-.86.06-1.93-.71-1.93-.71l-.4 1.62s1.06 1.08 2.98.96c1.6-.1 2.71-1.31 2.6-3.08-.14-2.25-2.66-2.46-2.72-3.42-.02-.18 0-.86 1.08-.93.74-.06 1.36.26 1.36.26l.55-1.93c0 .01.5.21 1.39.26l1.47-2.71c.04-.06.01-.12-.04-.15z" fill="#5E8E3E"/></svg>',
    },
    {
        'name': 'Toast POS Integration',
        'desc': 'Sync Toast restaurant POS transactions, menu items, and settlements into Odoo.',
        'price': '$1,199',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V8h16v10z" fill="#FF6600"/><rect x="6" y="10" width="5" height="3" rx="0.5" fill="#FF6600"/><rect x="6" y="14" width="12" height="1.5" rx="0.5" fill="#FF6600"/></svg>',
    },
    {
        'name': 'Dialpad Integration',
        'desc': 'Click-to-call from Odoo, auto-log call activity, and surface caller info on inbound rings.',
        'price': '$349',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56-.35-.12-.74-.03-1.01.24l-1.57 1.97c-2.83-1.35-5.48-3.9-6.89-6.83l1.95-1.66c.27-.28.35-.67.24-1.02-.37-1.11-.56-2.3-.56-3.53 0-.54-.45-.99-.99-.99H4.19C3.65 3 3 3.24 3 3.99 3 13.28 10.73 21 20.01 21c.71 0 .99-.63.99-1.18v-3.45c0-.54-.45-.99-.99-.99z" fill="#6C47FF"/></svg>',
    },
    {
        'name': 'Google Maps Route Optimization',
        'desc': 'Odoo module that optimizes delivery routes using the Google Maps API. Geocodes partner addresses and calculates optimal stop sequences for stock pickings.',
        'price': '$499',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5S10.62 6.5 12 6.5s2.5 1.12 2.5 2.5S13.38 11.5 12 11.5z" fill="#4285F4"/></svg>',
    },
    {
        'name': 'Margin Alert',
        'desc': 'Configurable margin threshold that warns or blocks salespeople from confirming low-margin orders. Protect your profitability automatically.',
        'price': '$109',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" fill="#FBBC04"/></svg>',
    },
    {
        'name': 'Duplicate Prevention',
        'desc': 'Configurable duplicate prevention for product SKUs and customer records. Stops duplicates before they enter your system.',
        'price': '$89',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14zm-4-4h-1v-2h-2v-2h2V11h1v2h2v2h-2v2z" fill="#EA4335"/><line x1="4" y1="4" x2="20" y2="20" stroke="#EA4335" stroke-width="2.5" stroke-linecap="round"/></svg>',
    },
    {
        'name': 'Maintenance Auto-Reminders',
        'desc': 'Automated email and in-app reminders for overdue or upcoming maintenance requests.',
        'price': '$149',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z" fill="#34A853"/></svg>',
    },
    {
        'name': 'Make to Order (Sales)',
        'desc': 'Trigger manufacturing or purchase orders automatically when a sales order is confirmed.',
        'price': '$199',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 3c1.93 0 3.5 1.57 3.5 3.5S13.93 13 12 13s-3.5-1.57-3.5-3.5S10.07 6 12 6zm7 13H5v-.23c0-.62.28-1.2.76-1.58C7.47 15.82 9.64 15 12 15s4.53.82 6.24 2.19c.48.38.76.97.76 1.58V19z" fill="#4285F4"/></svg>',
    },
    {
        'name': 'Bitcoin Currency',
        'desc': 'Adds BTC as a currency with live exchange rate sync for invoicing and payments.',
        'price': '$129',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M11.5 11.5v-3h1.25c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5H11.5zm0 1h1.5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5H11.5v-3z" fill="#F7931A"/><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm3.33 12.5c0 1.1-.6 2.05-1.48 2.56.02.01.15.44.15.44h-1.5l-.1-.5H11.5v.5H10v-.5H8.5v-1.5H10V8.5H8.5V7H10v-.5h1.5V7h.9l.1-.5h1.5l-.15.44c.88.51 1.48 1.46 1.48 2.56 0 .78-.3 1.48-.78 2 .48.52.78 1.22.78 2z" fill="#F7931A"/></svg>',
    },
    {
        'name': 'Task Cascade Scheduling',
        'desc': 'Automatically shift dependent project tasks when a parent task\'s dates change.',
        'price': '$179',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm-1 9h-2v5.5l3.5 2.1-.75 1.23L10 17.5V11H8l4-4 4 4h-3z" fill="#7B61FF"/></svg>',
    },
    {
        'name': 'Early Payment Discount',
        'desc': 'Offer customers automatic discounts for paying invoices before the due date.',
        'price': '$139',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1 1.05.82 1.87 2.65 1.87 1.96 0 2.4-.98 2.4-1.59 0-.83-.44-1.61-2.67-2.14-2.48-.6-4.18-1.62-4.18-3.67 0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87-1.5 0-2.4.68-2.4 1.64 0 .84.65 1.39 2.67 1.94s4.18 1.36 4.18 3.87c0 1.87-1.38 2.92-3.12 3.17z" fill="#34A853"/></svg>',
    },
    {
        'name': 'Bi-Directional Margin Calculator',
        'desc': 'Set a target dollar margin or percentage and auto-compute the other, right on the product form.',
        'price': '$99',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-4.5 14H13v-1.5h1.5V17zm0-3H13v-6h1.5v6zM10 17H8.5v-1.5H10V17zm0-3H8.5v-6H10v6z" fill="#EA4335"/><path d="M7 7l10 10M17 7L7 17" stroke="#EA4335" stroke-width="1.5" stroke-linecap="round"/></svg>',
    },
    {
        'name': 'Website Returns Processing',
        'desc': 'Let customers initiate product returns directly from the Odoo eCommerce portal.',
        'price': '$249',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M19 8l-4 4h3c0 3.31-2.69 6-6 6-1.01 0-1.97-.25-2.8-.7l-1.46 1.46C8.97 19.54 10.43 20 12 20c4.42 0 8-3.58 8-8h3l-4-4zM6 12c0-3.31 2.69-6 6-6 1.01 0 1.97.25 2.8.7l1.46-1.46C15.03 4.46 13.57 4 12 4c-4.42 0-8 3.58-8 8H1l4 4 4-4H6z" fill="#4285F4"/></svg>',
    },
    {
        'name': 'Auto-Assign Leads by Territory',
        'desc': 'Route incoming leads to the right salesperson based on state, zip code, or country.',
        'price': '$159',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" fill="#34A853"/></svg>',
    },
    {
        'name': 'Inventory Aging Report',
        'desc': 'Visualize how long stock has been sitting by warehouse, category, or product.',
        'price': '$179',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z" fill="#FBBC04"/></svg>',
    },
    {
        'name': 'Vendor Scorecard',
        'desc': 'Rate and rank vendors on delivery time, quality, and pricing to inform purchasing decisions.',
        'price': '$169',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" fill="#FBBC04"/></svg>',
    },
    {
        'name': 'Custom KPI Dashboard',
        'desc': 'Drag-and-drop dashboard with real-time KPIs across sales, inventory, and accounting.',
        'price': '$349',
        'icon': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" fill="#7B61FF"/></svg>',
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


@app.route('/apps')
def apps():
    return render_template('projects.html', odoo_apps=ODOO_APPS)


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
