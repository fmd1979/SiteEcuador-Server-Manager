#!/usr/bin/env bash
set -Eeuo pipefail
[[ $(id -u) -eq 0 ]] || { echo 'Ejecutar como root'; exit 1; }
cd "$(dirname "$0")"
test -f /var/lib/apc-moodle-monitor/status.json || { echo 'No existe status.json del monitor; confirma instalación v1.1'; exit 1; }
install -d -o root -g root -m 700 /etc/siteecuador-manager /var/lib/siteecuador-manager
install -d -o root -g root -m 755 /opt/siteecuador-manager/telegram
install -o root -g root -m 750 telegram/alert_worker.py /opt/siteecuador-manager/telegram/alert_worker.py
if [[ ! -f /etc/siteecuador-manager/telegram.json ]]; then
 install -o root -g root -m 600 telegram/telegram.json.example /etc/siteecuador-manager/telegram.json
 echo 'CONFIGURA primero token y chat_ids en /etc/siteecuador-manager/telegram.json'
fi
install -o root -g root -m 644 systemd/siteecuador-alerts.service /etc/systemd/system/
install -o root -g root -m 644 systemd/siteecuador-alerts.timer /etc/systemd/system/
python3 -m py_compile /opt/siteecuador-manager/telegram/alert_worker.py
systemctl daemon-reload
printf 'Instalación preparada. Tras configurar Telegram, ejecutar:\n'
printf ' python3 /opt/siteecuador-manager/telegram/alert_worker.py --dry-run\n'
printf ' systemctl enable --now siteecuador-alerts.timer\n'
