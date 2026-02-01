-- Accélère la recherche exacte (Requête 1)
CREATE INDEX idx_utilisateurs_email ON utilisateurs(email);
explain analyze
SELECT * FROM utilisateurs WHERE email = 'alice@email.com';
-- Accélère les recherches de prix (Requêtes 2 et 9)
CREATE INDEX idx_produits_prix ON produits(prix);
explain analyze 
SELECT * FROM produits WHERE prix BETWEEN 100 AND 500;
explain analyze
SELECT c.id, p.nom_produit, c.montant_total
FROM commandes c
JOIN produits p ON c.produit_id = p.id
WHERE p.prix > (SELECT AVG(prix) FROM produits);
--  les regroupements par nom (Requêtes 3, 4, 8)
CREATE INDEX idx_utilisateurs_nom ON utilisateurs(nom);
-- Accélère les filtres et groupements par catégorie (Requêtes 5, 10)
CREATE INDEX idx_produits_categorie ON produits(categorie);
--Accélèrent TOUTES les jointures (Requêtes 3, 6)
CREATE INDEX idx_commandes_produit_id ON commandes(produit_id);
-- Accélère les calculs de montants (Requêtes 4, 5, 7, 10)
CREATE INDEX idx_commandes_montant ON commandes(montant_total);
--R3
explain analyze 
SELECT p.nom_produit, u.nom, COUNT(c.id) as nombre_achats
FROM commandes c
JOIN produits p ON c.produit_id = p.id
JOIN utilisateurs u ON c.utilisateur_id = u.id
WHERE p.categorie = 'Electronique' AND u.ville = 'Paris'
GROUP BY p.nom_produit, u.nom;
--R4
explain analyse
SELECT u.nom, SUM(c.montant_total) 
FROM utilisateurs u
JOIN commandes c ON u.id = c.utilisateur_id
GROUP BY u.nom
ORDER BY SUM(c.montant_total) DESC;
--R5
explain analyse
SELECT p.categorie, SUM(c.montant_total) as CA
FROM commandes c
JOIN produits p ON c.produit_id = p.id
GROUP BY p.categorie;
--R6
explain analyze
SELECT p.nom_produit 
FROM produits p
LEFT JOIN commandes c ON p.id = c.produit_id
WHERE c.id IS NULL;
--R7
explain analyze
SELECT u.ville, SUM(c.montant_total) AS chiffre_affaires
FROM utilisateurs u
JOIN commandes c ON u.id = c.utilisateur_id
GROUP BY u.ville
ORDER BY chiffre_affaires DESC;
--R8
explain analyze
SELECT u.nom, COUNT(c.id) AS nombre_de_commandes
FROM utilisateurs u
JOIN commandes c ON u.id = c.utilisateur_id
GROUP BY u.nom
HAVING COUNT(c.id) > 3;
--R10
explain analyze
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
