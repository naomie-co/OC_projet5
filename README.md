# OC Projet 5 - Trouver un substitut alimentaire


## 1 - Création de l’environnement virtuel
Ce programme est exécuté en Python et utilise également Mysql.

Pour l'exécuter, il faut au préalable créer un environnement virtuel. 

Une fois l'environnement virtuel créé, lancez l'installation de dépendances avec la commande:

    pip install -r requirements.txt 

## 2 - Création du fichier permettant la connexion. 
L’exécution de la parties MySql du fichier nécessite la création au préalable d’un fichier **DB_info.py** qui contient les données de connexion suivantes : 

    HOST = "YourHost"
    USER = "YourUserName"
    PASSWORD = "YourPassword"
    DB = "off"

## 3 - Lancer le fichier main.py

L'utilisateur est sur le terminal. Ce dernier lui affiche les choix suivants :

1 - Quel aliment souhaitez-vous remplacer ? 

2 - Retrouver mes aliments substitués.

3 - Quitter le programme.

L'utilisateur sélectionne 1. Le programme pose les questions suivantes à l'utilisateur et ce dernier sélectionne les réponses :

Sélectionnez la catégorie. [Plusieurs propositions associées à un chiffre. L'utilisateur entre le chiffre correspondant et appuie sur entrée]

Sélectionnez l'aliment. [Plusieurs propositions associées à un chiffre. L'utilisateur entre le chiffre correspondant à l'aliment choisi et appuie sur entrée]

Le programme propose un substitut, sa description, un magasin ou l'acheter (le cas échéant) et un lien vers la page d'Open Food Facts concernant cet aliment.

L'utilisateur a alors la possibilité d'enregistrer le résultat dans la base de données.

L'utilisateur peut retrouver ses produits sauvegardés à partir du menu en sélectionnant 2. 

Si l'utilisateur sélectionne 3, le programme s'arrête. 
