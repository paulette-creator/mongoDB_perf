-- Table des utilisateurs
CREATE TABLE utilisateurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    email VARCHAR(100),
    ville VARCHAR(50),
    date_inscription DATE
);

-- Table des produits
CREATE TABLE produits (
    id SERIAL PRIMARY KEY,
    nom_produit VARCHAR(100),
    categorie VARCHAR(50),
    prix DECIMAL(10, 2),
    stock INT
);

-- Table des commandes 
CREATE TABLE commandes (
    id SERIAL PRIMARY KEY,
    utilisateur_id INT,
    produit_id INT,
    date_commande TIMESTAMP,
    quantite INT,
    montant_total DECIMAL(10, 2),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id),
    FOREIGN KEY (produit_id) REFERENCES produits(id)
);
