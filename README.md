# Ackermann

Une application pour la gestion d'un cabinet d'avocat en HTML/CSS, Bootstrap et Django.

## Installation locale

1. Crée un environnement virtuel Python 3.12+.
2. Installe les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Crée une clé secrète et charge les variables d'environnement :
   - `DJANGO_SECRET_KEY`
   - `DJANGO_DEBUG=True`
   - `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1`
4. Exécute les migrations :
   ```bash
   python manage.py migrate
   ```
5. Lance le serveur :
   ```bash
   python manage.py runserver
   ```

## Déploiement

Le projet est préparé pour un déploiement Python standard via `requirements.txt` et `runtime.txt`.

> Note : Netlify ne prend pas en charge une application Django complète en mode serveur classique. Le fichier `netlify.toml` est fourni pour déployer les fichiers statiques générés par Django (`collectstatic`). Pour héberger le backend Django réel, il est recommandé d'utiliser une plateforme compatible Python/Django comme Render, Railway, Heroku ou un conteneur Docker.

## Configuration d'environnement Recommandée

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=example.com`
- `DJANGO_LOGIN_URL=/comptes/login/`
- `DJANGO_LOGIN_REDIRECT_URL=/`
- `DJANGO_LOGOUT_REDIRECT_URL=/`
