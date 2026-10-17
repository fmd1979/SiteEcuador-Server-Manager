# Fase 1 — instalación y alcance

**Disponible:** alertas Telegram locales, basadas en JSON del APC Moodle Monitor v1.1, con timer systemd y notificaciones de incidencias/resoluciones.

**No disponible aún:** API SaaS, login, MFA, terminal web real, configuración remota.

Requisitos: Debian 13, Python 3, root para instalar el temporizador, archivo `/var/lib/apc-moodle-monitor/status.json` generado por el monitor local.

```bash
sudo bash install-telegram.sh
sudoedit /etc/siteecuador-manager/telegram.json
sudo chmod 600 /etc/siteecuador-manager/telegram.json
sudo python3 /opt/siteecuador-manager/telegram/alert_worker.py --dry-run
sudo systemctl enable --now siteecuador-alerts.timer
sudo journalctl -u siteecuador-alerts.service -n 30 --no-pager
```

Configura bot_token y chat_ids con valores privados. No confirmamos la entrega real con `--dry-run`; hay que probar mensajes reales sin revelar el token.

El agente actual **no** detecta la caída total del servidor: para eso se necesita una comprobación externa.

Para actualizaciones: revisar cambios, mantener la configuración privada fuera del repositorio, y no sustituir los archivos productivos sin comprobar compatibilidad.
