"""Build a dependency-free static site. Run from any working directory."""
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
esc = lambda value: html.escape(str(value), quote=True)

def read(name):
    return json.loads((ROOT / name).read_text())

def build():
    site = read('content/site.json')
    groups = read('content/help.json')['groups']
    entries = sorted(read('content/changelog.json')['entries'], key=lambda x: x['date'], reverse=True)
    config = read('deploy.json')
    ids = [g['id'] for g in groups]
    if len(set(ids)) != len(ids) or any(not re.fullmatch(r'[a-z0-9-]+', x) for x in ids):
        raise ValueError('分类标识必须是唯一的小写英文、数字或横线')
    for entry in entries:
        from datetime import date
        date.fromisoformat(entry['date'])
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT / 'assets', OUT / 'assets', dirs_exist_ok=True)
    (OUT / '.nojekyll').touch()
    domain = config.get('domain', '')
    if domain:
        if not re.fullmatch(r'[A-Za-z0-9.-]+', domain):
            raise ValueError('域名不能包含协议、路径或空格')
        (OUT / 'CNAME').write_text(domain + '\n')
    elif (OUT / 'CNAME').exists():
        (OUT / 'CNAME').unlink()

    def page(title, active, content, prefix=''):
        nav = ''.join(f'<a href="{prefix}{file}"'+(' aria-current="page"' if key == active else '')+f'>{label}</a>' for key, file, label in [('home','index.html','主页'),('help','help.html','指令帮助'),('logs','changelog.html','更新日志')])
        categories = [('all', '全部指令')] + [(g['id'], g['title']) for g in groups]
        if active == 'help':
            children = ''.join(f'<button class="filter" data-filter="{esc(key)}" aria-pressed="false">{esc(label)}</button>' for key, label in categories)
        else:
            children = ''.join(f'<a href="{prefix}help.html?category={esc(key)}">{esc(label)}</a>' for key, label in categories)
        expanded = ' open' if active == 'help' else ''
        mobile_nav = f'<a href="{prefix}index.html"' + (' aria-current="page"' if active == 'home' else '') + '>主页</a>'
        mobile_nav += f'<details class="help-menu"{expanded}><summary>指令帮助<span class="submenu-chevron" aria-hidden="true">⌄</span></summary><div class="menu-subcategories">{children}</div></details>'
        mobile_nav += f'<a href="{prefix}changelog.html"' + (' aria-current="page"' if active == 'logs' else '') + '>更新日志</a>'
        return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · {esc(site['name'])}</title><meta name="description" content="{esc(site['description'])}"><link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/style.css"><script defer src="{prefix}assets/site.js"></script></head><body><div class="wrap"><header class="nav"><a class="brand" href="{prefix}index.html"><img src="{prefix}assets/avatar.jpg" alt="">{esc(site['name'])}</a><nav class="desktop-nav" aria-label="主导航">{nav}</nav><button class="menu-toggle" aria-label="打开导航菜单" aria-controls="mobile-menu" aria-expanded="false"><span aria-hidden="true">☰</span></button></header><dialog id="mobile-menu" class="mobile-menu" aria-labelledby="menu-title"><div class="menu-heading"><strong id="menu-title">{esc(site['name'])}</strong><button class="menu-close" aria-label="关闭导航菜单">×</button></div><nav aria-label="手机导航">{mobile_nav}</nav></dialog><main>{content}</main><footer class="footer"><span>✦ {esc(site['name'])} · 陪你记录每一点进步</span><span>QQ 机器人 / 音游与日常</span></footer></div></body></html>'''

    cards = ''.join(f'''<a class="feature" href="help.html?category={esc(g['id'])}"><span class="symbol" aria-hidden="true">{esc(g['symbol'])}</span><h3>{esc(g['title'])}</h3><p>{esc(g['subtitle'])}</p><div class="feature-bottom"><span>{len(g['commands'])} 条常用指令</span><span aria-hidden="true">↗</span></div></a>''' for g in groups)
    latest = '<p class="muted">更新故事，即将开始。</p>'
    if entries:
        entry = entries[0]
        latest = f'''<a class="latest" href="changelog.html"><time>{esc(entry['date'])}</time><h3>{esc(entry['title'])}</h3><span class="tag">{esc(entry['version'])}</span></a>'''
    home = f'''<section class="hero"><div class="hero-copy"><span class="eyebrow">A little rhythm, a little magic</span><h1>你好呀，<br>我是<em>{esc(site['name'])}</em>。</h1><p class="intro">{esc(site['tagline'])}<br>{esc(site['description']).replace(chr(10), '<br>')}</p><div class="actions"><a class="btn" href="help.html">查看指令帮助 <span aria-hidden="true">↗</span></a><a class="btn secondary" href="changelog.html">最近更新</a></div><p class="hero-note">从一条指令开始，发现更多小惊喜。</p></div><div class="hero-art"><img src="assets/avatar.jpg" alt="鳕烩烩：浅紫色头发的猫耳角色，手持冰淇淋"><div class="art-caption"><div><small>YOUR LITTLE COMPANION</small><strong>今天，也一起玩吧。</strong></div><span class="star" aria-hidden="true">✦</span></div></div></section><section><div class="section-title"><h2>一起发现，我能做什么</h2><a href="help.html">全部指令 ↗</a></div><div class="feature-grid">{cards}</div></section><div class="lower"><section class="panel"><div class="section-title"><h2>鳕烩烩的成长日记</h2><a href="changelog.html">查看全部 ↗</a></div>{latest}</section><section class="panel"><h2>第一次见面？</h2><div class="start-step"><span class="step-num">01</span><p><strong>选一个想体验的功能</strong>从指令帮助里找到用法和示例。</p></div><div class="start-step"><span class="step-num">02</span><p><strong>在 QQ 里和我打招呼</strong>群聊请先 @鳕烩烩，再发送指令。</p></div><div class="start-step"><span class="step-num">03</span><p><strong>按提示完成绑定</strong>查分功能可能需要先绑定游戏账号。</p></div></section></div>'''
    (OUT / 'index.html').write_text(page('主页','home',home))
    filters = '<button class="filter" data-filter="all" aria-pressed="true">全部指令</button>' + ''.join(f'<button class="filter" data-filter="{esc(g["id"])}" aria-pressed="false">{esc(g["title"])}</button>' for g in groups)
    sections = ''
    for g in groups:
        commands = ''
        for c in g['commands']:
            example = ''
            if c.get('example'):
                example = f'<div class="example"><code>{esc(c["example"])}</code><button data-copy="{esc(c["example"])}" aria-label="复制{esc(c["title"])}示例">复制</button></div>'
            commands += f'<article class="command"><h3>{esc(c["title"])}</h3><code>{esc(c["command"])}</code><p>{esc(c["description"])}</p>{example}</article>'
        sections += f'<section class="command-group" id="{esc(g["id"])}"><h2>{esc(g["title"])}</h2>{commands}</section>'
    help_page = f'''<div class="page-head"><span class="eyebrow">The little handbook</span><h1>指令帮助</h1><p>你想做的事，从这里找到答案。</p></div><div class="help-layout"><aside class="sidebar" aria-label="指令分类"><small>探索功能</small>{filters}</aside><div><div class="search-bar"><input id="search" type="search" aria-label="搜索指令或功能" placeholder="搜索指令、功能或关键词…"><span id="result-count" role="status"></span></div><div class="notice">{esc(site['notice'])}</div>{sections}<div id="empty" class="empty" hidden><h2>还没找到这条指令</h2><p>试试其他关键词，或者切换到「全部指令」。</p></div></div></div>'''
    (OUT / 'help.html').write_text(page('指令帮助','help',help_page))
    releases = ''.join(f'<article class="release panel"><span class="tag">{esc(e["version"])}</span><time datetime="{esc(e["date"])}">{esc(e["date"])}</time><h2>{esc(e["title"])}</h2><p>{esc(e["body"])}</p></article>' for e in entries)
    (OUT / 'changelog.html').write_text(page('更新日志','logs',f'<div class="page-head"><span class="eyebrow">Growing, little by little</span><h1>每一点更新，都记在这里。</h1><p>新功能、小修复，还有不断变好的鳕烩烩。</p></div><div class="timeline">{releases or "还没有更新记录。"}</div>'))
    (OUT / 'admin').mkdir(exist_ok=True)
    ready = bool(config.get('repository') and config.get('oauth_base_url'))
    if ready:
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',config['repository']):
            raise ValueError('仓库格式应为 owner/repo')
        if not config['oauth_base_url'].startswith('https://'):
            raise ValueError('OAuth 服务必须使用 HTTPS')
        shutil.copy(ROOT / 'admin/index.html', OUT / 'admin/index.html')
        cms = read('admin/config.json')
        cms['backend'] = {'name':'github','repo':config['repository'],'branch':config['branch'],'base_url':config['oauth_base_url'],'auth_endpoint':'auth'}
        # JSON is valid YAML; Decap accepts this config via its explicit link.
        (OUT / 'admin/config.yml').write_text(json.dumps(cms,ensure_ascii=False,indent=2))
    else:
        (OUT / 'admin/index.html').write_text(page('管理后台','admin','<section class="panel admin-box"><span class="eyebrow">FOR THE KEEPER</span><h1>鳕烩烩的管理室</h1><p>这里将使用 GitHub 账号登录，用来编辑指令帮助、更新日志和首页介绍。</p><div class="notice">当前为本地预览。连接网站仓库和登录服务后，即可开启内容管理。</div><a class="btn secondary" href="../help.html">先看看指令帮助 ↗</a></section>','../'))
        if (OUT / 'admin/config.yml').exists():
            (OUT / 'admin/config.yml').unlink()
    print(f'Built {OUT}; GitHub CMS: {"configured" if ready else "awaiting repository and OAuth service"}')

if __name__ == '__main__':
    build()
