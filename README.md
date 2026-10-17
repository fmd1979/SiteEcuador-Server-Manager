# SiteEcuador Server Manager

Panel de monitoreo y administración de infraestructura, diseñado para evolución **multiservidor y multiempresa (SaaS)**.

> **Estado actual: fase 1 experimental.** El componente funcional disponible es el verificador local de servicios y alertas Telegram conectado al monitor APC Moodle v1.1. **Todavía no** implementa inicio de sesión SaaS, terminal web interactiva ni administración remota de servicios. No se recomienda comercializarlo o exponerlo como panel administrativo en este estado.

## Instalación — alertas Telegram (Debian 13)

En el servidor que **ya tiene instalado** APC Moodle Monitor v1.1:

```bash
sudo bash install-telegram.sh
sudoedit /etc/siteecuador-manager/telegram.json
sudo chmod 600 /etc/siteecuador-manager/telegram.json
sudo python3 /opt/siteecuador-manager/telegram/alert_worker.py --dry-run
sudo systemctl enable --now siteecuador-alerts.timer
sudo systemctl status siteecuador-alerts.timer --no-pager
```

Crea un bot desde @BotFather, inicia el chat con él, y coloca el token y chat ID **solo** en el archivo privado del servidor. Nunca subas el archivo real a GitHub. El bot envía alertas nuevas y de recuperación; no ejecuta comandos recibidos por Telegram.

Consulta la documentación original en [docs/fase1.md](docs/fase1.md) y la arquitectura prevista de la terminal en [terminal/ARCHITECTURE.md](terminal/ARCHITECTURE.md).

## Hoja de ruta

1. Agente de monitoreo desacoplado e identidad por servidor.
2. API multiempresa, autenticación MFA, roles, auditoría y aislamiento de datos.
3. Gateway SSH web independiente, autorización por servidor y registro de sesiones.
4. Acciones administrativas permitidas con prevalidación, aprobación y reversión.
5. Control SaaS de organizaciones, planes, límites y facturación.

## Seguridad

No publicar secretos, claves SSH, credenciales, snapshots Restic ni configuraciones reales. El puerto SSH y las interfaces MySQL/Redis/PHP-FPM no deben quedar expuestos al Internet. Reporta vulnerabilidades de manera privada al mantenedor, no mediante issues públicos con información sensible.

## Licencia

**Licencia aún no definida.** Publicar código no concede automáticamente derechos de reutilización comercial.
