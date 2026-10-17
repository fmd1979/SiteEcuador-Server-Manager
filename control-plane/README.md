# Control Plane 2.1 — Preview de laboratorio

Prototipo web para operar junto al monitor local APC English sin alterar Moodle.

Funciones: login con hash scrypt, segundo factor TOTP, cookies seguras, protección CSRF, usuarios vinculados a organizaciones, servidores por empresa, endpoint de métricas JSON autenticado y registro de inicios de sesión.

**NO desplegar en Internet o vender aún**. Pendientes: MFA robusto ante fuerza bruta, gestión segura de altas/bajas, recuperación MFA, permisos por rol/servidor, pruebas de aislamiento tenant, auditoría inmutable, control multiagente, validación externa de seguridad, automatización de despliegue y hardening. Terminal SSH y comandos root intencionalmente no implementados.

Para la versión experimental completa y pruebas locales ver ZIP de entrega del proyecto. Para desarrollo: usar entorno Python venv separado y Nginx HTTPS privado; no publicar puerto Gunicorn ni sustituir el monitor actual.

Dependencias: Flask 3.1.1, Gunicorn 23.0.0. Configurar SSM_SESSION_SECRET (aleatorio de al menos 32 caracteres), SSM_DATABASE y SSM_APC_METRICS. El secreto no debe incluirse en Git.

Nota: el diseño SQLite de prueba no reemplaza el PostgreSQL propuesto para despliegue SaaS real.
