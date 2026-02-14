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
    return {'now': datetime.now()}


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


@app.route('/activities')
def activities():
    return render_template('activities.html')


@app.route('/press')
def press():
    return render_template('press.html', press_items=PRESS_ITEMS)


if __name__ == '__main__':
    app.run(debug=True, port=5013)
