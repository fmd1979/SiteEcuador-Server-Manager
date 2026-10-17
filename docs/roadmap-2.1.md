# SiteEcuador Server Manager 2.1: plan de aceptación

- [x] Telegram verificado en APC English
- [x] Monitor local y dashboard existentes (sin sustituir)
- [x] Prototipo independiente de control-plane (entrega ZIP y rama)
- [x] MFA TOTP y login incluidos para pruebas aisladas
- [x] Modelo conceptual multiempresa/multiservidor
- [ ] Pruebas de aislamiento y permisos de roles
- [ ] Revisión de hardening y acceso HTTPS/Host separado
- [ ] Gateway WebSocket SSH y reautenticación MFA
- [ ] Acciones permitidas: Nginx test/reload, PHP-FPM y MySQL
- [ ] Auditoría y rotación de secretos
- [ ] Alertas de caída del host comprobadas por agente exterior
- [ ] Pruebas de carga, backup de base SaaS, test de recuperación

**Límite fase 2.1:** no se habilitan operaciones privilegiadas ni terminal. Evitar compartir servidor de producción Moodle con componentes SaaS no verificados.
