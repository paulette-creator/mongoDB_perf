 --On insère des utilisateurs
INSERT INTO utilisateurs (nom, email, ville, date_inscription) VALUES
('Alice', 'alice@email.com', 'Paris', '2023-01-01'),
('Bob', 'bob@email.com', 'Lyon', '2023-02-15'),
('Charlie', 'charlie@email.com', 'Marseille', '2023-03-10'),
('Diane', 'diane@email.com', 'Lille', '2023-04-05'),
('Etienne', 'etienne@email.com', 'Bordeaux', '2023-05-12');

--  On insère des produits
INSERT INTO produits (nom_produit, categorie, prix, stock) VALUES
('Laptop Pro', 'Electronique', 1200.00, 50),
('Smartphone X', 'Electronique', 800.00, 100),
('Chaise Bureau', 'Mobilier', 150.00, 20),
('Cafetière', 'Electroménager', 80.00, 30),
('Souris Sans Fil', 'Electronique', 25.00, 200);

-- On génère 100 commandes aléatoires
INSERT INTO commandes (utilisateur_id, produit_id, date_commande, quantite, montant_total)
SELECT 
    floor(random() * 3 + 1)::int,        -- ID utilisateur aléatoire (entre 1 et 3)
    floor(random() * 4 + 1)::int,        -- ID produit aléatoire (entre 1 et 4)
    now() - (random() * (interval '365 days')), -- Date aléatoire sur l'année écoulée
    floor(random() * 5 + 1)::int,        -- Quantité entre 1 et 5
    (random() * 500 + 10)::decimal(10,2) -- Montant entre 10 et 510€
FROM generate_series(1, 100);

