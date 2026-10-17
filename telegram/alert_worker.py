#!/usr/bin/env python3
"""Read-only watchdog for existing APC Moodle Monitor v1.1 JSON.
Telegram delivery uses stdlib HTTPS. Never accepts remote commands.
"""
import json, os, pathlib, sys, time, urllib.parse, urllib.request

STATUS=pathlib.Path('/var/lib/apc-moodle-monitor/status.json')
CONF=pathlib.Path('/etc/siteecuador-manager/telegram.json')
STATE=pathlib.Path('/var/lib/siteecuador-manager/alert-state.json')


def load(path, default=None):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return default


def send(token, chat, msg):
    endpoint='https://api.telegram.org/bot'+token+'/sendMessage'
    payload=urllib.parse.urlencode({'chat_id':str(chat),'text':msg,'disable_web_page_preview':'true'}).encode()
    req=urllib.request.Request(endpoint,data=payload,method='POST')
    with urllib.request.urlopen(req,timeout=12) as response:
        answer=json.load(response)
        if not answer.get('ok'):
            raise RuntimeError('Telegram rejected message')


def main():
    cfg=load(CONF)
    if not isinstance(cfg,dict) or not cfg.get('bot_token') or not cfg.get('chat_ids'):
        sys.exit('Configura /etc/siteecuador-manager/telegram.json antes de activar alertas.')
    dry='--dry-run' in sys.argv
    data=load(STATUS)
    if not isinstance(data,dict):
        sys.exit('No hay JSON del monitor; comprueba el recolector.')
    state=load(STATE,{}) or {}
    findings={}
    for name, status in (data.get('services') or {}).items():
        if str(status).lower() not in ('active','running'):
            findings['service:'+name]='Servicio '+name+' en estado '+str(status)
    for name in ('redis_sessions','redis_muc','mysql','moodle'):
        value=data.get(name) or {}
        if isinstance(value,dict) and value.get('ok') is False:
            findings['health:'+name]='Verificación '+name+' fallida'
    # Avoid guessing backup freshness from unknown fields. Explicit monitor alerts preferred.
    for alert in (data.get('alerts') or []):
        if isinstance(alert,dict) and str(alert.get('level','')).lower() in ('critical','error'):
            ident=str(alert.get('id') or alert.get('message',''))[:120]
            findings['monitor:'+ident]=str(alert.get('message') or ident)
    old=set(state.get('active',[])); current=set(findings)
    new=sorted(current-old); recovered=sorted(old-current)
    messages=['🚨 SiteEcuador | APC English\n'+findings[key] for key in new]
    messages+=['✅ SiteEcuador | APC English\nIncidencia recuperada: '+key for key in recovered]
    if dry:
        print(json.dumps({'new':new,'recovered':recovered,'messages':messages},ensure_ascii=False,indent=2))
        return
    for msg in messages:
        for chat in cfg['chat_ids']:
            send(cfg['bot_token'],chat,msg)
    # Only update state when every delivery succeeds, so failed notifications retry.
    STATE.parent.mkdir(parents=True,exist_ok=True)
    tmp=STATE.with_suffix('.tmp')
    tmp.write_text(json.dumps({'active':sorted(current),'updated':int(time.time())}),encoding='utf-8')
    os.chmod(tmp,0o600)
    tmp.replace(STATE)
    print(f'Incidencias activas: {len(current)}, alertas nuevas: {len(new)}, recuperadas: {len(recovered)}')

if __name__=='__main__':
    main()
