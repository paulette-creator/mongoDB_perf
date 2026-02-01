SELECT * FROM utilisateurs WHERE email = 'alice@email.com';
SELECT * FROM produits WHERE prix BETWEEN 100 AND 500;
SELECT p.nom_produit, u.nom, COUNT(c.id) as nombre_achats
FROM commandes c
JOIN produits p ON c.produit_id = p.id
JOIN utilisateurs u ON c.utilisateur_id = u.id
WHERE p.categorie = 'Electronique' AND u.ville = 'Paris'
GROUP BY p.nom_produit, u.nom; 
-- 4. client ayant depenser le plus d'argent
SELECT u.nom, SUM(c.montant_total) 
FROM utilisateurs u
JOIN commandes c ON u.id = c.utilisateur_id
GROUP BY u.nom
ORDER BY SUM(c.montant_total) DESC;
-- 5. chiffre d'affaire total par categorie de produits
SELECT p.categorie, SUM(c.montant_total) as CA
FROM commandes c
JOIN produits p ON c.produit_id = p.id
GROUP BY p.categorie;
-- 6. les produits qui ne partent pas
SELECT p.nom_produit 
FROM produits p
LEFT JOIN commandes c ON p.id = c.produit_id
WHERE c.id IS NULL;
-- 7.les villes les plus rentables
SELECT u.ville, SUM(c.montant_total) AS chiffre_affaires
FROM utilisateurs u
JOIN commandes c ON u.id = c.utilisateur_id
GROUP BY u.ville
ORDER BY chiffre_affaires DESC;
-- 8. cles clients avec plus de 3 commandes
SELECT u.nom, COUNT(c.id) AS nombre_de_commandes
FROM utilisateurs u
JOIN commandes c ON u.id = c.utilisateur_id
GROUP BY u.nom
HAVING COUNT(c.id) > 3;
-- 9.le nom du produit, mais seulement si le prix du produit est supérieur à la moyenne de tous les produits
SELECT c.id, p.nom_produit, c.montant_total
FROM commandes c
JOIN produits p ON c.produit_id = p.id
WHERE p.prix > (SELECT AVG(prix) FROM produits);
-- 10. le chiffre d'affaires par catégorie pour chaque mois, et classer les résultats.
SELECT 
    date_trunc('month', c.date_commande) AS mois,
    p.categorie,
    SUM(c.montant_total) AS chiffre_affaires,
    COUNT(c.id) AS nombre_ventes
FROM commandes c
JOIN produits p ON c.produit_id = p.id
GROUP BY mois, p.categorie
ORDER BY mois DESC, chiffre_affaires DESC
LIMIT 10;