# Abonoteatro Scraper

Script para monitorizar eventos de Abonoteatro y recibir notificaciones por email.

## Configuración

### 1. Crear el archivo de configuración
```bash
cp config.json.example config.json
```

Edita `config.json` con la configuración general (URLs, rutas, etc.)

### 2. Crear el archivo de variables de entorno (RECOMENDADO para datos sensibles)
```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:
- **ABONO_ABONOTEATRO_USER**: Tu número de abonado
- **ABONO_ABONOTEATRO_PASSWORD**: Tu contraseña de Abonoteatro
- **ABONO_GMAIL_USER**: Tu email de Gmail
- **ABONO_GMAIL_PASSWORD**: Contraseña de aplicación de Gmail (ver más abajo)
- **ABONO_GMAIL_RECIPIENTS**: Emails destinatarios separados por comas

**⚠️ El archivo `.env` NO se subirá a Git (está en .gitignore)**

### 3. Obtener contraseña de aplicación de Gmail

1. Ve a https://myaccount.google.com/security
2. Activa la verificación en 2 pasos
3. Busca "Contraseñas de aplicaciones"
4. Genera una contraseña para "Correo"
5. Copia esa contraseña en `ABONO_GMAIL_PASSWORD` en el archivo `.env`

### 4. Instalar dependencias
```bash
python3 -m venv venv
source venv/bin/activate
pip install selenium
```

## Ejecución

```bash
./abonoteatro.sh
```

O manualmente:
```bash
source venv/bin/activate
python abonoteatro.py
```

## Prioridad de configuración

El script buscará las credenciales en este orden:
1. **Variables de entorno** (desde `.env` o sistema)
2. **config.json** (si no están en variables de entorno)

Esto permite tener las credenciales seguras en `.env` y la configuración general en `config.json`.
