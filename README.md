# Odoo 19 Custom Addons — Seriaflow

Custom modules untuk Odoo 19 Community di `odoo.seriaflow.com`.

## Modul

### seriaflow_hello
Modul test sederhana yang menampilkan halaman di `/hello`.

## Deployment
Push ke branch `main` → GitHub Actions otomatis `git pull` ke `/opt/odoo19/custom-addons` di server.

Setelah deploy, restart Odoo:
```bash
sudo systemctl restart odoo19
```
Lalu install modul dari **Settings → Apps**.