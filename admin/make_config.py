import json
from pathlib import Path

def field(name,label,widget='string',**kwargs):
    return dict(name=name,label=label,widget=widget,**kwargs)
config = {'locale':'zh_Hans','media_folder':'assets/uploads','public_folder':'../assets/uploads','collections':[{'name':'content','label':'网站内容','files':[
{'name':'site','label':'首页介绍','file':'content/site.json','fields':[field('name','机器人名称'),field('tagline','一句话介绍'),field('description','详细介绍','text'),field('notice','使用提示','text')]},
{'name':'help','label':'指令帮助','file':'content/help.json','fields':[field('groups','功能分类','list',summary='{{fields.title}}',fields=[field('id','分类标识',hint='唯一的小写英文、数字或横线，例如 platina',pattern=['^[a-z0-9-]+$','请使用小写英文、数字或横线']),field('title','分类名称'),field('subtitle','分类简介'),field('symbol','分类符号'),field('commands','指令','list',summary='{{fields.title}}',fields=[field('command','指令格式'),field('title','功能名称'),field('description','说明','text'),field('example','可复制示例',required=False)])])]},
{'name':'changelog','label':'更新日志','file':'content/changelog.json','fields':[field('entries','更新记录','list',summary='{{fields.date}} · {{fields.title}}',fields=[field('version','版本'),field('date','日期','datetime',format='YYYY-MM-DD',date_format='YYYY-MM-DD',time_format=False),field('title','标题'),field('body','更新内容','text')])]}]}]}
Path(__file__).with_name('config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2))
