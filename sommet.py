#!/usr/bin/env python

""" Classe Sommet :

Pour un arbre de recherche.
A utiliser avec une file de priorité (heapq)
dans une méthode par évaluation et séparation

"""

__author__ = 'Chams Lahlou'
__date__ = 'Octobre 2019 - novembre 2020'
__version__ = '0.2'

class Sommet():

    def __init__(self, places, non_places, evaluation, numero):
        # liste des jobs déjà placés
        self.places = places

        # liste des jobs qui ne sont pas encore placés
        self.non_places = non_places

        # valeur de la fonction d'évaluation pour le sommet
        self.evaluation = evaluation

        # numéro du sommet
        self.numero = numero


    def __lt__(self, sommet):
        """ permet d'utiliser les fonctions de tri de python 
        en comparant deux sommets selon l'attribut 'valeur' 
        """
        return self.evaluation < sommet.evaluation
