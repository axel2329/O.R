import job
import ordonnancement
import Flowshop
import random
import numpy as np
import time


#Execution Time Limit
Tps = 300   # 5 min
# Tps = 600    # 10 min

# Simulated Annealing Parameter       
K = 1.38e23 # Boltzmann Constant
alpha = 0.999
# Tabu Search Parameters           
MAX_MEMOIRE = 30
# Genetic Algorithm Parameter           
N = 100
T = 0.15    # Mutation Rate

class MetaH():
    def __init__(self, nombre_jobs=0, nombre_machines=0, liste_jobs=None):

        # Number of jobs for the problem
        self.nombre_jobs = nombre_jobs

        # nombre de machines pour le problème
        self.nombre_machines = nombre_machines

        # Set of jobs for the problem (order is not important)
        self.liste_jobs = liste_jobs


    def definir_par_fichier(self, nom):
        """Create a flowshop problem from a file"""
        fdonnees = open(nom,"r")
        ligne = fdonnees.readline() 
        l = ligne.split() # Retrieve the values into a list
        self.nombre_jobs = int(l[0])
        self.nombre_machines = int(l[1])
       
        self.liste_jobs = []
        for i in range(self.nombre_jobs):
            ligne = fdonnees.readline() 
            l = ligne.split()
            # Convert the sequence of strings representing
            # the durations of operations into a list of integers
            l = [int(i) for i in l]
            j = job.Job(i, l)
            self.liste_jobs.append(j)
        fdonnees.close()
        
                                        ##########################################
                                        #########  SIMULATED ANNEALING  ##########
                                        ##########################################

    def Recuit_Simule(self, heuristique) :
        t1 = time.time()        #Initialization of the time
        t2 = t1
        l = heuristique.copy()      # We start with a good heuristic: NEH
        ordo = ordonnancement.Ordonnancement(self.nombre_machines)
        ordo.ordonnancer_liste_job(l)
        seq_en_cour, duree_en_cour = ordo.sequence, ordo.duree          # We initialize the current solution
        best_seq, best_duree = ordo.sequence, ordo.duree                # We initialize the optimal solution
        nb_iter = 0
        T = 1
        while (t2-t1) < Tps : 
            # The neighbor is chosen randomly by performing a permutation on the list l
            # Ensuring not to have the same neighbor twice
            index1 = random.randint(0, len(self.liste_jobs)-1)
            index2 = random.randint(0, index1)          
            if index1 > 0 and index2 > 0 and index1 < len(self.liste_jobs)-1 and index2 < len(self.liste_jobs)-1 :  #Pour une meilleure recherche on modifie deux élements succesifs pour obtenir un voisin
                l[index1:index1+1], l[index2:index2+1] = l[index2:index2+1], l[index1:index1+1]
            else :
                l[index1], l[index2] = l[index2], l[index1]
            new_ordo = ordonnancement.Ordonnancement(self.nombre_machines)
            new_ordo.ordonnancer_liste_job(l)

            if new_ordo.duree < duree_en_cour :
                duree_en_cour = new_ordo.duree
                seq_en_cour = new_ordo.sequence
            
            else :                                      
                p = random.uniform(0,1)
                if p <= np.exp((duree_en_cour - new_ordo.duree)/(K*T)) :
                    duree_en_cour = new_ordo.duree
                    seq_en_cour = new_ordo.sequence
                if duree_en_cour < best_duree :
                    best_duree = duree_en_cour
                    best_seq = seq_en_cour
                T = T * alpha
            
            t2 = time.time()
            nb_iter += 1

        return best_duree, best_seq


                                        ##########################################
                                        #############  TABU SEARCH  ##############
                                        ##########################################

#### Function used for displaying lists of job numbers and comparing with memory. It will also be essential in the Genetic Algorithm, as copies change the addresses.
    
    def list_job_to_num(self, liste_jobs) :
        L = []
        for job in liste_jobs :
            L.append(job.numero)
        return L


    def Tabou(self, heuristique) :
        t1 = time.time()        # Timer Initialization
        t2 = t1
        M = []  # Memory list of already visited schedules
        l = heuristique.copy()
        list_num = self.list_job_to_num(l)
        ordo = ordonnancement.Ordonnancement(self.nombre_machines)
        ordo.ordonnancer_liste_job(l)
        best_seq, best_duree = ordo.sequence, ordo.duree

        while (t2-t1) < Tps :
            index1 = random.randint(0, len(self.liste_jobs)-1)
            index2 = random.randint(0, index1)
            if index1 > 0 and index2 > 0 and index1 < len(self.liste_jobs)-1 and index2 < len(self.liste_jobs)-1 :
                l[index1:index1+1], l[index2:index2+1] = l[index2:index2+1], l[index1:index1+1]
            else :
                l[index1], l[index2] = l[index2], l[index1]
            list_num = self.list_job_to_num(l)

            # We set the maximum size of the memory MAX_MEMORY
            # If the new neighbor is not in the list and the list is already at the maximum size, we remove the first entry in the list and add the new one (FIFO).
            # We do this to avoid revisiting recent neighbors
            if list_num not in M :
                if len(M) >= MAX_MEMOIRE :
                    M.pop(0)
                M.append(list_num)              # The memory contains lists of job numbers
                new_ordo = ordonnancement.Ordonnancement(self.nombre_machines)
                new_ordo.ordonnancer_liste_job(l)
                if new_ordo.duree < best_duree :    
                    best_duree = new_ordo.duree
                    best_seq = new_ordo.sequence
            
                t2 = time.time()   

        return best_duree, best_seq


                                        ##########################################
                                        ###############  GENETIC  ################
                                        ##########################################

    def Croiser(self, population1, population2) :
        family = []
        i = 0
        enfant_1 = []
        enfant_2 = []
        while i < len(population1) :
            pos1 = random.randint(1, len(self.liste_jobs)-1)   # We start at 1 to avoid issues with slicing [:pos]
            pos2 = random.randint(1, len(self.liste_jobs)-1)

            if pos1 < pos2 :
                enfant_1.append(population1[i][:pos1] + population2[i][pos1:pos2] + population1[i][pos2:])
                enfant_2.append(population2[i][:pos1] + population1[i][pos1:pos2] + population2[i][pos2:])
                i += 1
                                            
            if pos1 > pos2 :
                enfant_1.append(population1[i][:pos2] + population2[i][pos2:pos1] + population1[i][pos1:])
                enfant_2.append(population2[i][:pos2] + population1[i][pos2:pos1] + population2[i][pos1:])
                i += 1

            # Check integrity (no job repeated)

            if pos1 != pos2 :       # If we added a child to each of the lists, we check its integrity each timeé

                for j in range(len(self.liste_jobs)):
                    if self.list_job_to_num(enfant_1[i-1]).count(self.list_job_to_num(enfant_1[i-1])[j]) > 1 : # i-1 because we are in the loop continuation, and we performed i += 1 after adding a child to each list
                        self.ajouter_job_manquant(enfant_1[i-1], j)         # We add a missing value in place of a duplicate (before removing it to avoid index problems)
                        enfant_1[i-1].remove(enfant_1[i-1][j+1])         # We then remove the occurrence (we will have the job at most twice with the crossover)

                for j in range(len(self.liste_jobs)):
                    if self.list_job_to_num(enfant_2[i-1]).count(self.list_job_to_num(enfant_2[i-1])[j]) > 1 :
                        self.ajouter_job_manquant(enfant_2[i-1], j) 
                        enfant_2[i-1].remove(enfant_2[i-1][j+1])  

        family = enfant_1 + enfant_2 + population1 + population2

        while len(family) != (len(population1)+len(population2)) :      # We randomly select elements from parents and children
            index = random.randint(0, len(family)-1)
            family.pop(index)
            
        return family

    
    def ajouter_job_manquant(self, liste, position) :       # This function, used in the correction of crossover, returns one of the possible missing jobs for a new individual 
        for job in self.liste_jobs :
            if job.numero not in self.list_job_to_num(liste) :
                liste.insert(position, job)         
                break                             # We only want to return one missing value

                

    def Muter(self, enfants) :
        nb_mutants = int(len(enfants)*T)           # Number of mutants to produce (T is defined as the mutation rate)
        for i in range(nb_mutants) : 
            mutant = enfants[random.randint(0, len(enfants)-1)]
            index1 = random.randint(0, len(self.liste_jobs)-1)
            index2 = random.randint(0, len(self.liste_jobs)-1)
            mutant[index1], mutant[index2] = mutant[index2], mutant[index1]             # We perform a swapping between two random values to model a mutation

        return enfants
  
    def Genetique(self, heuristique) :
        t1 = time.time()        
        t2 = t1
        l = heuristique
        ordo = ordonnancement.Ordonnancement(self.nombre_machines)
        ordo.ordonnancer_liste_job(l)
        best_seq, best_duree = ordo.sequence, ordo.duree    

        # Creation of the population
        P = []
        for i in range(N) :
            l_clone = l.copy()      # We start with NEH as the initial solution, and we will create a population based on the NEH solution.
            index1 = random.randint(0,len(self.liste_jobs)-1)
            index2 = random.randint(0, len(self.liste_jobs)-1)  
            l_clone[index1], l_clone[index2] = l_clone[index2], l_clone[index1]
            P.append(l_clone)     


        while (t2-t1) < Tps :     
            P1 = P[:int(N/2)]       # Ensure size of the population is an interger
            P2 = P[int(N/2):]
            for elem in P2 :        # To maximize the diversity of solutions, we reverse the order of half of a population to have even more possible solutions during crossover.
                elem.reverse()

            # Crossover of the two populations
            list_enfants = self.Croiser(P1,P2)

            # Mutation on certain offsprings
            individus = self.Muter(list_enfants)

            for ind in individus :
                new_ordo = ordonnancement.Ordonnancement(self.nombre_machines)
                new_ordo.ordonnancer_liste_job(ind)

                if new_ordo.duree < best_duree :
                    best_duree = new_ordo.duree
                    best_seq = new_ordo.sequence
            t2 = time.time()

        return best_duree, best_seq



                    #####################################
                    #############    MAIN   #############
                    #####################################



if __name__ == "__main__":  # Uncomment the desired set and the 3 methods. Note that for the 10 minutes, you will need to change the value of 'Tps' at the very beginning of the code
    
####   5 min Max   #####

    print("JEU tai01 :")
    prob = Flowshop.Flowshop()
    prob.definir_par_fichier("tai01.txt")
    o = ordonnancement.Ordonnancement(prob.nombre_machines)
    l = prob.ordre_NEH()

    prob = MetaH()
    prob.definir_par_fichier("tai01.txt")
    o = ordonnancement.Ordonnancement(prob.nombre_machines)

    print("Recuit Simulé :")
    d, s = prob.Recuit_Simule(l)
    for i in s:
        print(i.numero," ", end="")
    print("durée : ", d)

    print("Tabou :")
    d, s = prob.Tabou(l)
    for i in s:
        print(i.numero," ", end="")
    print("durée : ", d)

    print("Génétique :")
    d, s = prob.Genetique(l)
    for i in s:
        print(i.numero," ", end="")
    print("durée : ", d)



    # print("JEU tai11 :")
    # prob = Flowshop.Flowshop()
    # prob.definir_par_fichier("tai11.txt")
    # o = ordonnancement.Ordonnancement(prob.nombre_machines)
    # l = prob.ordre_NEH()

    # prob = MetaH()
    # prob.definir_par_fichier("tai11.txt")
    # o = ordonnancement.Ordonnancement(prob.nombre_machines)

    # print("Recuit Simulé :")
    # d, s = prob.Recuit_Simule(l)
    # for i in s:
    #     print(i.numero," ", end="")
    # print("durée : ", d)

    # print("Tabou :")
    # d, s = prob.Tabou(l)
    # for i in s:
    #     print(i.numero," ", end="")
    # print("durée : ", d)

    # print("Génétique :")
    # d, s = prob.Genetique(l)
    # for i in s:
    #     print(i.numero," ", end="")
    # print("durée : ", d)



    # print("JEU tai21 :")
    # prob = Flowshop.Flowshop()
    # prob.definir_par_fichier("tai21.txt")
    # o = ordonnancement.Ordonnancement(prob.nombre_machines)
    # l = prob.ordre_NEH()

    # prob = MetaH()
    # prob.definir_par_fichier("tai21.txt")
    # o = ordonnancement.Ordonnancement(prob.nombre_machines)

    # print("Recuit Simulé :")
    # d, s = prob.Recuit_Simule(l)
    # for i in s:
    #     print(i.numero," ", end="")
    # print("durée : ", d)

    # print("Tabou :")
    # d, s = prob.Tabou(l)
    # for i in s:
    #     print(i.numero," ", end="")
    # print("durée : ", d)

    # print("Génétique :")
    # d, s = prob.Genetique(l)
    # for i in s:
    #     print(i.numero," ", end="")
    # print("durée : ", d)


##### 10 min max  #####


    # print("JEU tai31 :")
    # prob = Flowshop.Flowshop()
    # prob.definir_par_fichier("tai31.txt")
    # o = ordonnancement.Ordonnancement(prob.nombre_machines)
    # l = prob.ordre_NEH()


    # prob = MetaH()
    # prob.definir_par_fichier("tai31.txt")
    # o = ordonnancement.Ordonnancement(prob.nombre_machines)

    # print("Recuit Simulé :")
    # d, s = prob.Recuit_Simule(l)
    # for i in s:
    #     print(i.numero," ", end="")
    # print("durée : ", d)

    # print("Tabou :")
    # d, s = prob.Tabou(l)
    # for i in s:
    #     print(i.numero," ", end="")
    # print("durée : ", d)

    # print("Génétique :")
    # d, s = prob.Genetique(l)
    # for i in s:
    #     print(i.numero," ", end="")
    # print("durée : ", d)
        


    # print("JEU tai41 :")
    # prob = Flowshop.Flowshop()
    # prob.definir_par_fichier("tai41.txt")
    # o = ordonnancement.Ordonnancement(prob.nombre_machines)
    # l = prob.ordre_NEH()

    # prob = MetaH()
    # prob.definir_par_fichier("tai41.txt")
    # o = ordonnancement.Ordonnancement(prob.nombre_machines)

    # print("Recuit Simulé :")
    # d, s = prob.Recuit_Simule(l)
    # for i in s:
    #     print(i.numero," ", end="")
    # print("durée : ", d)

    # print("Tabou :")
    # d, s = prob.Tabou(l)
    # for i in s:
    #     print(i.numero," ", end="")
    # print("durée : ", d)

    # print("Génétique :")
    # d, s = prob.Genetique(l)
    # for i in s:
    #     print(i.numero," ", end="")
    # print("durée : ", d)



    # print("JEU tai51 :")
    # prob = Flowshop.Flowshop()
    # prob.definir_par_fichier("tai51.txt")
    # o = ordonnancement.Ordonnancement(prob.nombre_machines)
    # l = prob.ordre_NEH()

    # prob = MetaH()
    # prob.definir_par_fichier("tai51.txt")
    # o = ordonnancement.Ordonnancement(prob.nombre_machines)

    # print("Recuit Simulé :")
    # d, s = prob.Recuit_Simule(l)
    # for i in s:
    #     print(i.numero," ", end="")
    # print("durée : ", d)

    # print("Tabou :")
    # d, s = prob.Tabou(l)
    # for i in s:
    #     print(i.numero," ", end="")
    # print("durée : ", d)

    # print("Génétique :")
    # d, s = prob.Genetique(l)
    # for i in s:
    #     print(i.numero," ", end="")
    # print("durée : ", d)