# ClientHub – CI/CD

API Flask + MySQL + page statique Nginx, conteneurisées avec Docker Compose.

## Pipeline (GitHub Actions)
Chaque push sur `main` déclenche, dans l'ordre :
1. **Tests unitaires**  ;
2. **Tests E2E** : la stack Compose démarre sur le runner et pytest interroge l'API réelle (/health, /who, /clients) ;
3. **Build et push** de l'image sur Docker Hub, taguée `latest` et avec le SHA du commit ;
4. **Déploiement** sur la VM Azure en SSH : copie des fichiers, `docker compose pull` puis `up -d`, puis vérification HTTP sur l'IP publique.
Un job ne démarre que si le précédent a réussi. Aucune action manuelle après le push.

## Choix techniques
- Idempotence : noms de conteneurs fixes + `docker compose up -d` .
- Sécurité : identifiants Docker Hub, clé SSH et mots de passe MySQL dans les GitHub Secrets ; le `.env` de production est généré au déploiement et n'est pas versionné.
- Traçabilité : l'image déployée est celle du SHA du commit.
- Le service `db` attend d'être `healthy` avant l'API (`depends_on`).