"""
Resolution of the permutation flowshop problem:

- by the NEH algorithm
- by an evaluation-separation method (Branch and Bound)
"""

import itertools
import job
import ordonnancement
import sommet

import heapq

MAXINT = 10000

class Flowshop():
    def __init__(self, nombre_jobs=0, nombre_machines=0, liste_jobs=None):

        # Number fo Jobs for the Problem
        self.nombre_jobs = nombre_jobs

        # Number of Machines for the Problem
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
            # the durations of operations into a list of integer
            l = [int(i) for i in l]
            j = job.Job(i, l)
            self.liste_jobs.append(j)
        fdonnees.close()
        
    
    def ordre_NEH(self):
        """Returns the list of jobs ordered according to NEH"""
    	
        # We sort the jobs in descending order of their durations
        l = [job for job in self.liste_jobs]
        l = sorted(l, key=lambda job:job.duree, reverse=True)

        mem = ordonnancement.Ordonnancement(self.nombre_machines)
        mem.ordonnancer_job(l[0])

        for n in range(1, len(l)):
            best_seq = mem.sequence
            mem = ordonnancement.Ordonnancement(self.nombre_machines)
            mem.ordonnancer_liste_job(l[:n+1])

            for i in range (n+1):
                o2 = ordonnancement.Ordonnancement(self.nombre_machines)
                seq = best_seq[:i] + [l[n]] + best_seq[i:]
                o2.ordonnancer_liste_job(seq)
                if (o2.duree < mem.duree) :
                    mem = o2
        return mem.sequence   
           

    # Calculation of r_kj considering a current schedule
    def date_dispo(self, ordo, machine, job):
        s=0
        for i in range(machine):
            s += job.duree_operation[i]
        if ordo.sequence != [] :
            return s + ordo.sequence[-1].date_debut[0] + ordo.sequence[-1].duree_operation[0]
        return s


    # Calculation of q_kj considering a current schedule
    def duree_latence(self, ordo, machine, job):
        s = 0
        if machine >= self.nombre_machines-1:
            return 0
        for i in range(machine+1,self.nombre_machines):
            s+= job.duree_operation[i]
        return s


    # Calculation of the sum of operation durations in a list executed on a given machine
    def duree_jobs(self, machine, liste_jobs):
        s = 0
        if liste_jobs == [] :
            return 0
        for job in liste_jobs:
            s += job.duree_operation[machine]
        return s


    # Calculation of a Lower Bound considering a current schedule
    def minorant(self, ordo, liste_jobs):
        LB =[]
        for machine in range(self.nombre_machines) :
            date_dispo = [self.date_dispo(ordo,machine,j) for j in self.liste_jobs]
            duree_latence = [self.duree_latence(ordo,machine,j) for j in self.liste_jobs]
            date_fin = min(date_dispo) + self.duree_jobs(machine, liste_jobs)

            if machine < self.nombre_machines-1 and ordo.sequence != [] :
                date_fin = max(date_fin, ordo.sequence[-1].date_debut[machine+1]+ordo.sequence[-1].duree_operation[machine+1])
            LB += [date_fin + min(duree_latence)]
            #minorant = (min(date_dispo)+min(duree_latence)+self.duree_jobs(machine,liste_jobs))        # Simpler version, but the lower bound is less accurate:
            #LB += [minorant]                                                                           
        return max(LB)


########################
### Branch and Bound ###
########################
    
    def evaluation_separation(self):

        ordo = ordonnancement.Ordonnancement(self.nombre_machines)
        ordo.ordonnancer_liste_job(self.liste_jobs)
        tas = []
        val_solution = ordo.duree       
        liste_solution = ordo.sequence      
        numero = 1      # First vertex

    # Construction of the priority queue based on a heap
        for job in self.liste_jobs :
            new_ordo = ordonnancement.Ordonnancement(self.nombre_machines)
            new_ordo.ordonnancer_job(job)
            minorant = self.minorant(new_ordo, [j for j in self.liste_jobs if j not in new_ordo.sequence])
            som = sommet.Sommet(new_ordo,[j for j in self.liste_jobs if j not in new_ordo.sequence] , minorant , numero)
            heapq.heappush(tas, som)
            numero += 1
    
    # Traversal of vertices
        while tas != [] and tas[0].evaluation < val_solution : 
            som = heapq.heappop(tas)
            val = som.places.duree

            if len(som.places.sequence)==self.nombre_jobs and val < val_solution :
                val_solution = val
                liste_solution = som.places.sequence
            
            else :
                for job in som.non_places:
                    new_ordo2 = ordonnancement.Ordonnancement(self.nombre_machines)
                    new_ordo2.ordonnancer_liste_job(som.places.sequence)
                    new_ordo2.ordonnancer_job(job)
                    new_minorant = self.minorant(new_ordo2, [j for j in self.liste_jobs if j not in new_ordo2.sequence])
                    new_som = sommet.Sommet(new_ordo2,[j for j in self.liste_jobs if j not in new_ordo2.sequence], new_minorant, numero )
                    
                    if new_som.places.duree < val_solution :
                        heapq.heappush(tas, new_som)
                        numero += 1

        return val_solution, liste_solution, numero


# Tests
if __name__ == "__main__":
    print("JEU 1 :")
    prob = Flowshop()
    prob.definir_par_fichier("jeu1.txt")
    o = ordonnancement.Ordonnancement(prob.nombre_machines)
    print("Minorant :", prob.minorant(o,prob.liste_jobs))

    print("Ordo NEH :")
    l = prob.ordre_NEH()
    for i in l:
        print(i.numero," ", end="")

    print()
    b, l, n = prob.evaluation_separation()
    print("Ordonnancement optimal :")
    for i in l:
        print(i.numero,' ',end="")
    print("de durée",b)
    print(n, "sommets")

    print()
    print("JEU 2 :")
    prob = Flowshop()
    prob.definir_par_fichier("jeu2.txt")
    o = ordonnancement.Ordonnancement(prob.nombre_machines)

    print("Evaluation :", prob.minorant(o,prob.liste_jobs))

    print("Ordo NEH :")
    l = prob.ordre_NEH()
    for i in l:
        print(i.numero," ", end="")

    print()
    b, l, n = prob.evaluation_separation()
    print("Ordonnancement optimal :")
    for i in l:
        print(i.numero,' ',end="")
    print("de durée",b)
    print(n, "sommets")