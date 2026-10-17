"""Interactive once-only initialization; run from control-plane directory."""
import base64,getpass,secrets,sys,uuid
from werkzeug.security import generate_password_hash
from app import schema,conn
schema()
with conn() as c:
 if c.execute('SELECT count(*) FROM users').fetchone()[0]:sys.exit('Already initialized; refusing to overwrite.')
 name=input('Nombre de empresa: ').strip()
 email=input('Correo admin: ').strip().lower()
 if not name or '@' not in email:sys.exit('Datos incompletos.')
 pw=getpass.getpass('Contraseña (mínimo 14 caracteres): ')
 if len(pw)<14 or pw!=getpass.getpass('Confirmar contraseña: '):sys.exit('Contraseña corta o no coincide.')
 org,uid,sid=[str(uuid.uuid4()) for _ in range(3)]
 mfa=base64.b32encode(secrets.token_bytes(20)).decode()
 c.execute('INSERT INTO organizations VALUES(?,?)',(org,name))
 c.execute('INSERT INTO users VALUES(?,?,?,?,?,?)',(uid,org,email,generate_password_hash(pw,method='scrypt'),'owner',mfa))
 c.execute('INSERT INTO servers VALUES(?,?,?,?)',(sid,org,'APC English','local'))
print('TOTP secreto (NO compartir, anotar en autenticador):',mfa)
print('SHA1, 6 dígitos, intervalo 30 segundos. No mostrar a terceros.')
