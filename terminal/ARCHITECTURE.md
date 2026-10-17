# Terminal web segura — diseño y puertas de activación

La terminal interactiva NO está habilitada en este paquete. Evitar cualquier endpoint que ejecute shell desde parámetros HTTP.

Arquitectura propuesta:

Navegador (xterm.js) → HTTPS/WSS → API autenticada (sesión corta + MFA) → gateway SSH dedicado → host seleccionado.

Reglas obligatorias:
1. Identidad multiempresa con aislamiento por `organization_id` y autorización por `server_id` en el backend para CADA conexión WebSocket.
2. MFA reciente (step-up, máximo 5 minutos), permiso `terminal`, sin cuentas compartidas.
3. Gateway sin acceso root al panel, ejecución con cuenta Unix `siteops` sin privilegios de administración predeterminados. Escalamiento puntual sólo por acciones autorizadas y auditadas; nunca ejecutar shell remoto como root por defecto.
4. Llaves SSH por agente/servidor cifradas y almacenadas fuera del frontend; validación estricta de huellas host (sin AutoAddPolicy).
5. Duración máxima de sesión 15 minutos de inactividad y 60 minutos absoluta; caducidad de token WebSocket de un solo uso; origen estricto y CSRF.
6. Registrar inicio, fin, usuario, IP, destino, cambios privilegiados y resultado. La grabación del terminal contiene secretos potenciales: cifrar, restringir acceso y retener conforme a política; nunca enviar contenido a Telegram.
7. Puertos SSH no expuestos al público general: red privada WireGuard o SSH gateway con reglas explícitas.
8. No incluir comandos de mantenimiento root en la aplicación web como texto editable. Usar catálogo de acciones, validación, respaldos, pruebas (`nginx -t`, `php-fpm -t`) y rollback.
9. Separar agente, gateway y API SaaS; el monitor actual permanece solo lectura hasta auditar esta capa.
10. No habilitar terminal por Nginx proxy_pass directamente a `ttyd` sin controles. `ttyd` a root o SSH compartido equivaldría a exponer administración total.

Ruta recomendada para la primera versión interactiva: integrar Apache Guacamole (SSH) o un gateway basado en AsyncSSH y xterm.js tras implementar MFA, tenant checks y auditoría. Probar primero en máquina de laboratorio, no en Moodle productivo.
