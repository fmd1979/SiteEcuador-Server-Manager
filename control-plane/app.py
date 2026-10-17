"""2.1 preview: local-only control plane; NOT production SaaS or shell gateway."""
import base64,hashlib,hmac,json,os,secrets,sqlite3,struct,time,uuid,html
from functools import wraps
from pathlib import Path
from flask import Flask,session,request,redirect,jsonify,abort
from werkzeug.security import generate_password_hash,check_password_hash

DB=Path(os.environ.get('SSM_DATABASE','/var/lib/siteecuador-manager/control-plane.sqlite3'))
METRICS=Path(os.environ.get('SSM_APC_METRICS','/var/lib/apc-moodle-monitor/status.json'))
app=Flask(__name__)
app.secret_key=os.environ.get('SSM_SESSION_SECRET','')
if len(app.secret_key)<32:raise RuntimeError('Configure SSM_SESSION_SECRET with a strong random string')
app.config.update(SESSION_COOKIE_SECURE=True,SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Strict',PERMANENT_SESSION_LIFETIME=1800)

def conn():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON');return c

def schema():
 DB.parent.mkdir(parents=True,exist_ok=True)
 with conn() as c:c.executescript("""
 CREATE TABLE IF NOT EXISTS organizations(id TEXT PRIMARY KEY,name TEXT NOT NULL);
 CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,org_id TEXT NOT NULL REFERENCES organizations(id),email TEXT NOT NULL UNIQUE,pw TEXT NOT NULL,role TEXT NOT NULL,mfa TEXT NOT NULL);
 CREATE TABLE IF NOT EXISTS servers(id TEXT PRIMARY KEY,org_id TEXT NOT NULL REFERENCES organizations(id),name TEXT NOT NULL,provider TEXT NOT NULL);
 CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,org_id TEXT,user_id TEXT,action TEXT,ts INTEGER);
 CREATE TABLE IF NOT EXISTS attempts(id INTEGER PRIMARY KEY,ip TEXT,ts INTEGER);
 """)

def otp(secret,step=None):
 step=int(time.time())//30 if step is None else step
 digest=hmac.new(base64.b32decode(secret),struct.pack('>Q',step),hashlib.sha1).digest()
 off=digest[-1]&15
 return str((struct.unpack('>I',digest[off:off+4])[0]&0x7fffffff)%1000000).zfill(6)

def otp_ok(secret,value):
 return len(value)==6 and value.isascii() and value.isdigit() and any(hmac.compare_digest(otp(secret,int(time.time())//30+n),value) for n in (-1,0,1))

def csrf():
 if 'csrf' not in session:session['csrf']=secrets.token_urlsafe(24)
 return session['csrf']

def check():
 if not hmac.compare_digest(str(session.get('csrf','')),str(request.form.get('csrf',''))):abort(403)

def ui(title,body):
 return '<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SiteEcuador Manager</title><style>body{font:16px system-ui;background:#eef3f9;color:#123;margin:0}header{background:#112d53;color:white;padding:22px}main{max-width:960px;margin:30px auto;padding:0 20px}.card{background:white;padding:25px;border-radius:14px;margin:12px 0}input,button{padding:12px;display:block;margin:12px 0;width:100%;max-width:400px}button{background:#1766bd;color:white;border:0;border-radius:8px}a{color:#1469bb}</style><header><b>SiteEcuador Server Manager · 2.1 preview</b></header><main><h1>'+html.escape(title)+'</h1>'+body+'</main></html>'

@app.after_request
def headers(r):
 r.headers['Cache-Control']='no-store';r.headers['X-Content-Type-Options']='nosniff';r.headers['X-Frame-Options']='DENY';r.headers['Referrer-Policy']='no-referrer'
 r.headers['Content-Security-Policy']="default-src 'none';style-src 'unsafe-inline';form-action 'self';base-uri 'none';frame-ancestors 'none'"
 return r

def login_required(fn):
 @wraps(fn)
 def inner(*args,**kwargs):
  if not session.get('uid') or not session.get('verified'):return redirect('/login')
  return fn(*args,**kwargs)
 return inner

def log(org,uid,action):
 with conn() as c:c.execute('INSERT INTO audit(org_id,user_id,action,ts) VALUES(?,?,?,?)',(org,uid,action,int(time.time())))

@app.get('/healthz')
def health():return jsonify(status='ok',release='2.1-preview')

@app.route('/login',methods=['GET','POST'])
def login():
 error=''
 if request.method=='POST':
  check();ip=request.remote_addr or '?';now=int(time.time())
  with conn() as c:
   c.execute('DELETE FROM attempts WHERE ts<?',(now-900,))
   if c.execute('SELECT count(*) FROM attempts WHERE ip=?',(ip,)).fetchone()[0]>=10:abort(429)
   c.execute('INSERT INTO attempts(ip,ts) VALUES(?,?)',(ip,now))
   u=c.execute('SELECT * FROM users WHERE email=?',(request.form.get('email','').lower().strip(),)).fetchone()
  if u and check_password_hash(u['pw'],request.form.get('password','')):
   session.clear();session.update(uid=u['id'],org=u['org_id'],email=u['email'],verified=False);csrf();log(u['org_id'],u['id'],'password_ok');return redirect('/mfa')
  error='<p>Credenciales inválidas.</p>'
 form='<form method="post"><input type="hidden" name="csrf" value="'+csrf()+'"><label>Correo<input type="email" name="email" required></label><label>Contraseña<input type="password" name="password" required></label><button>Entrar</button></form>'
 return ui('Ingreso administrativo','<div class="card">'+error+form+'</div>'),(401 if error else 200)

@app.route('/mfa',methods=['GET','POST'])
def mfa():
 if not session.get('uid'):return redirect('/login')
 with conn() as c:u=c.execute('SELECT * FROM users WHERE id=? AND org_id=?',(session['uid'],session['org'])).fetchone()
 if not u:session.clear();return redirect('/login')
 error=''
 if request.method=='POST':
  check()
  if otp_ok(u['mfa'],request.form.get('code','')):
   session['verified']=True;session.permanent=True;log(u['org_id'],u['id'],'mfa_ok');return redirect('/')
  error='Código incorrecto';log(u['org_id'],u['id'],'mfa_failed')
 return ui('Verificación TOTP','<div class="card">'+html.escape(error)+'<form method="post"><input type="hidden" name="csrf" value="'+csrf()+'"><input name="code" pattern="[0-9]{6}" maxlength="6" required><button>Verificar</button></form></div>'),(401 if error else 200)

@app.post('/logout')
@login_required
def logout():check();session.clear();return redirect('/login')

@app.get('/')
@login_required
def dashboard():
 with conn() as c:servers=c.execute('SELECT id,name,provider FROM servers WHERE org_id=?',(session['org'],)).fetchall()
 rows=''.join('<li>'+html.escape(s['name'])+' — <a href="/api/servers/'+s['id']+'/metrics">Métricas JSON</a></li>' for s in servers)
 logoutform='<form method="post" action="/logout"><input type="hidden" name="csrf" value="'+csrf()+'"><button>Salir</button></form>'
 return ui('Panel central','<div class="card">Organización aislada por tenant · Sólo lectura<h2>Servidores ('+str(len(servers))+')</h2><ul>'+rows+'</ul><p>Terminal SSH: DESHABILITADA · Edición de servicios: DESHABILITADA</p>'+logoutform+'</div>')

@app.get('/api/servers/<server_id>/metrics')
@login_required
def metrics(server_id):
 with conn() as c:s=c.execute('SELECT * FROM servers WHERE id=? AND org_id=?',(server_id,session['org'])).fetchone()
 if not s:abort(404)
 if s['provider']!='local':return jsonify(error='Agente remoto todavía no disponible'),501
 try:
  d=json.loads(METRICS.read_text(encoding='utf-8'))
  keys=('cpu','memory','disk','services','mysql','moodle','redis_sessions','redis_muc','php_fpm','restic','ssl','updated_at')
  return jsonify({k:d[k] for k in keys if k in d})
 except (OSError,ValueError):return jsonify(error='Monitor no disponible'),503

if __name__=='__main__':raise SystemExit('Run with gunicorn on localhost; never expose Flask dev server.')
