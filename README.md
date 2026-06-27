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

### Déploiement recommandé : Render

Render propose un plan gratuit supportant Django/Python et l'hébergement de votre backend.

1. Créez un compte Render.
2. Connectez votre dépôt GitHub `kalifa4y/Ackermann`.
3. Créez un nouveau service Web Python en utilisant la branche `main`.
4. Configurez :
   - Build command : `pip install -r requirements.txt`
   - Start command : `gunicorn ackermann.wsgi:application`
5. Ajoutez les variables d'environnement suivantes dans Render :
   - `DJANGO_SECRET_KEY` (clé secrète sécurisée)
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=your-app.onrender.com`
   - `DJANGO_LOGIN_URL=/comptes/login/`
   - `DJANGO_LOGIN_REDIRECT_URL=/`
   - `DJANGO_LOGOUT_REDIRECT_URL=/`
6. Exécutez `python manage.py migrate` dans l'interface Render ou via une commande de démarrage si nécessaire.

> Note : Render gère bien Django côté serveur, contrairement à Netlify qui est plutôt prévu pour des frontends statiques. Ce dépôt est maintenant configuré pour Render.

## Configuration d'environnement Recommandée

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=example.com`
- `DJANGO_LOGIN_URL=/comptes/login/`
- `DJANGO_LOGIN_REDIRECT_URL=/`
- `DJANGO_LOGOUT_REDIRECT_URL=/`
