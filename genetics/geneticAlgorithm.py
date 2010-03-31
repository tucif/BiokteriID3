import random
from virus import Virus

##LIMITS
limitsTemperature = (0,6)
limitsPH = (7,10)
limitsAggres = (11,17)
limitsVis = (18,24)

def evolve(virList, environment):
    print str([str(vir) for vir in virList])
    nextGeneration=reproduction(virList)
    newVirList = crossover(nextGeneration)
    for vir in newVirList:
        vir.update_fitness(environment)
        oldVir = virList.pop()
        vir.posX = oldVir.posX
        vir.posY = oldVir.posY
        vir.rot = oldVir.rot
        vir.rotVis=oldVir.rotVis
        vir.transTempLevel = oldVir.tempLevel
        vir.transPhLevel = oldVir.phLevel
        vir.transAggresiveness = oldVir.aggresiveness
        vir.transVisibility = oldVir.visibility
        vir.transFitnessPercentage=oldVir.fitnessPercentage
        print vir
    if len(virList)>0:
        return newVirList+virList
    return newVirList

def reproduction(virList):

    populationFitness=0
    averageFitness=0

    #calculate population fitness and average_virus_fitness_fitness
    for virus in virList:
        populationFitness+=virus.fitness;
    averageFitness=float(populationFitness)/len(virList)

    print "popFit=%d | averageFit= %d\n" % (populationFitness,averageFitness)

    #calculate probability of being selected for reproduction
    pSelectList=[(virus,float(virus.fitness)/populationFitness) for virus in virList]

    print "pSelect: \n"+str([str(vir)+","+str(prob) for (vir,prob) in pSelectList])
    #select members of the population to reproduce
    selectedVirus=[]

    for i in xrange(len(virList)):
        selectionNumber=random.random()
        accumProb=0
        for (virus,probability) in pSelectList:
            accumProb+=probability
            if selectionNumber<=accumProb:
                selectedVirus.append(virus)
                break

    print "selectedMembers: \n"+str([str(vir) for vir in selectedVirus])
    return selectedVirus

def crossover(virList):
    
    #ENCODING
    virusPool = [encode_virus(vir) for vir in virList]
    
    #MATE SELECTION
    mateList = [] #List with mates ( virA, virB )
    while virusPool:
        if len(virusPool) <= 1:
            break
        mate1 = virusPool.pop(random.randint(0,len(virusPool)-1))
        mate2 = virusPool.pop(random.randint(0,len(virusPool)-1))
        mateList.append( (mate1,mate2) )

    #MATING
    for vir in mateList:
        print vir
    newPopulation = mate(mateList)
    for newVir in newPopulation:        
        if random.randint(0,100)==42:
            print "Hubo mutacion en %s"%str(newVir)
            mutVir = mutation(newVir)
            newVir.tempLevel = mutVir.tempLevel
            newVir.phLevel = mutVir.phLevel
            newVir.aggresiveness = mutVir.aggresiveness
            newVir.visibility = mutVir.visibility
            print "ahora es: %s"%str(newVir)

    return newPopulation
    

    
def mate(mateList):

    crossPoints = [random.randint(0,6),
                   random.randint(7,10),
                   random.randint(11,17),
                   random.randint(18,24)]


    newPopulation = []
    for (virA, virB) in mateList:
        newTempA = virA[limitsTemperature[0]:crossPoints[0]] + \
                  virB[crossPoints[0]:limitsTemperature[1]+1]

        newPHA =   virA[limitsPH[0]:crossPoints[1]] + \
                  virB[crossPoints[1]:limitsPH[1]+1]

        newAggresA= virA[limitsAggres[0]:crossPoints[2]] + \
                  virB[crossPoints[2]:limitsAggres[1]+1]

        newVisA =  virA[limitsVis[0]:crossPoints[3]] + \
                  virB[crossPoints[3]:limitsVis[1]+1]


        newPopulation.append(
           decode_virus(newTempA+newPHA+newAggresA+newVisA)
        )

        newTempB = virB[limitsTemperature[0]:crossPoints[0]] + \
                  virA[crossPoints[0]:limitsTemperature[1]+1]

        newPHB =   virB[limitsPH[0]:crossPoints[1]] + \
                  virA[crossPoints[1]:limitsPH[1]+1]

        newAggresB= virB[limitsAggres[0]:crossPoints[2]] + \
                  virA[crossPoints[2]:limitsAggres[1]+1]

        newVisB =  virB[limitsVis[0]:crossPoints[3]] + \
                  virA[crossPoints[3]:limitsVis[1]+1]


        newPopulation.append(
            decode_virus(newTempB+newPHB+newAggresB+newVisB)
        )

    return newPopulation



def encode_virus(vir):
    bin_temperature = bin(vir.tempLevel)[2:].zfill(7)
    bin_phLevel = bin(vir.phLevel)[2:].zfill(4)
    bin_agressiveness = bin(vir.aggresiveness)[2:].zfill(7)
    bin_visibility = bin(vir.visibility)[2:].zfill(7)

    return bin_temperature + bin_phLevel + bin_agressiveness + bin_visibility

def decode_virus(bin_vir, posX=0, posY=0):
    temperature = int(bin_vir[limitsTemperature[0]:limitsTemperature[1]+1],2)
    ph = int(bin_vir[limitsPH[0]:limitsPH[1]+1],2)
    aggres = int(bin_vir[limitsAggres[0]:limitsAggres[1]+1],2)
    vis = int(bin_vir[limitsVis[0]:limitsVis[1]+1],2)

    return Virus(posX,posY,temperature,ph,aggres,vis)


def mutation(vir):
    bin_vir = encode_virus(vir)
    mutant_bit = random.randint(0,24)
    print "bit mutante: %d"%mutant_bit
    mutant_value = '1' if bin_vir[mutant_bit]=='0' else '0'
    bin_vir = bin_vir[0:mutant_bit] +mutant_value+ bin_vir[mutant_bit+1:]

    return decode_virus(bin_vir, vir.posX, vir.posY)
