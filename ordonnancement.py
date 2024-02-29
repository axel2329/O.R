#!/usr/bin/env python

""" Classe Ordonnancement """

__author__ = 'Chams Lahlou'
__date__ = 'Octobre 2019 - janvier 2021'
__version__ = '0.2'

import job

class Ordonnancement():

    # constructeur pour un ordonnancement vide
    def __init__(self, nombre_machines):
        # liste des jobs dans l'ordre où ils doivent être ordonnancés
        self.sequence = [] 

        # nombre de machines utilisées
        self.nombre_machines = nombre_machines

        # durée de l'ordonnancement, c'est-à-dire date de fin de la dernière
        # opération exécutée
        self.duree = 0 

        # pour chaque machine, date à partir de laquelle on peut exécuter une
        # nouvelle opération.
        # Les machines sont numérotées à partir de 0
        self.date_disponibilite = [0 for i in range(self.nombre_machines)]

    
    def afficher(self):
        print("Ordre des jobs :", end='')
        for job in self.sequence:
            print(" ",job.numero," ", end='')
        print()
        for job in self.sequence:
            print("Job", job.numero, ":", end='')
            for machine in range(self.nombre_machines):
                print(" op", machine, 
                      "à t =", job.date_debut[machine],
                      "|", end='')
            print()
        print("Cmax =", self.duree)


    #####################
    # exo 2 :  A REMPLIR
    #####################
    def ordonnancer_job(self, job):
        self.sequence += [job]
        for i in range (self.nombre_machines):
            if i==0:
                job.date_debut[i] = self.date_disponibilite[i]
                self.date_disponibilite[i] += job.duree_operation[i]
            else : 
                job.date_debut[i] = max(self.date_disponibilite[i], self.date_disponibilite[i-1])
                self.date_disponibilite[i] = job.date_debut[i] + job.duree_operation[i]
        
        self.duree = self.date_disponibilite[-1]
          #donne le dernier élément de la liste
            


    #####################
    # exo 3 :  A REMPLIR
    #####################
    def ordonnancer_liste_job(self, liste_jobs):
        for job in liste_jobs:
            self.ordonnancer_job(job)
            

# Pour tester
if __name__ == "__main__":
    a = job.Job(1,[1,1,1,10,1])
    b = job.Job(2,[1,10,1,1,1])
    a.afficher()
    b.afficher()
    l = [a,b]
    ordo = Ordonnancement(5)
    #ordo.ordonnancer_job(a)
    #ordo.ordonnancer_job(b)
    ordo.ordonnancer_liste_job(l)
    ordo.sequence
    ordo.afficher()
    a.afficher()
    b.afficher()
