import os,secrets,base64,tempfile
os.environ['SSM_SESSION_SECRET']='testing-'+secrets.token_urlsafe(48)
os.environ['SSM_DATABASE']=tempfile.mktemp(suffix='.sqlite3')
from app import app,schema,conn,otp,otp_ok

def test_mfa():
 key=base64.b32encode(secrets.token_bytes(20)).decode()
 assert otp_ok(key,otp(key))
 assert not otp_ok(key,'000abc')

def test_auth_required():
 schema()
 with app.test_client() as client:
  assert client.get('/').status_code==302
  assert client.get('/api/servers/xxx/metrics').status_code==302
  assert client.get('/healthz').status_code==200

def test_tenant_boundary():
 schema()
 with conn() as c:
  c.execute("INSERT INTO organizations VALUES('o','Other')")
  c.execute("INSERT INTO servers VALUES('s','o','Secret','local')")
 with app.test_client() as client:
  with client.session_transaction() as s:s.update(uid='u',org='another',verified=True)
  assert client.get('/api/servers/s/metrics').status_code==404
