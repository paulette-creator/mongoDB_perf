Projet de Performance de Base de Données
Ce projet explore l'optimisation des performances SQL via l'indexation et la mise en place  des données temps réel utilisant MongoDB, PostgreSQL et Grafana.

Partie 1 : Optimisation SQL (PostgreSQL)
Cette section se concentre sur l'analyse de l'impact des index sur les performances de lecture.

Initialisation : Création des tables et scripts d'insertion massive de données.

Tests de Performance : Exécution de requêtes complexes avant et après l'application d'index.

Analyse : Un fichier SQL dédié compare les temps d'exécution (EXPLAIN ANALYZE) pour quantifier le gain de performance.

Partie 2 : Pipeline de Données Velib (NoSQL vers SQL)
L'objectif est de récupérer les données de l'API Velib en temps réel et de les superviser.

Étapes d'exécution :
Collecte : Lancement de la fonction get_api() pour récupérer les données brutes.

Stockage Temporaire : Connexion et insertion des données dans MongoDB.

Infrastructure : Lancement des services via la commande :

Bash
docker-compose up -d
Transfert & Analyse : Connexion avec PostgreSQL pour structurer les données.

Monitoring & Visualisation
Une fois le pipeline actif, les métriques de performance et les données de disponibilité des vélos sont visualisables directement dans Grafana.

Consultez les tableaux de bord inclus pour observer les métriques recueillies en temps réel.

Comment lancer le projet ?
Exécutez les scripts SQL de la Partie 1.
Lancez le script Python pour l'API Velib.
Démarrez l'environnement Docker : docker-compose up.

Accédez à Grafana (localhost:3000).
