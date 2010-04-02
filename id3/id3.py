#ID3 Module
import math
from constants import CHARACTERISTICS_DICT
from constants import EVALUATE_FUNC_DICT

class ID3Tree:
    def __init__(self, classificationList,characteristics, trainingSet ):
        self.classes = classificationList #List containing classes [Yes, No] or [Good,Bad,Ugly]
        self.characteristics = characteristics #List containing characteristics names ["outerShape","outerColor",...]
        
        self.trainingSet = trainingSet # List of tuples like (CellObject, classification)
        self.trainingSetSize= len(self.trainingSet)

        self.entropyDict = {}
        self.sysEntropy = 0

        self.rootNode = None

    def calculate(self):
        """Makes all the required calculus for entropies and gains and saves them
           in the entropyDict"""
        #Generar totals con cada total para cada clase
        totals = []
        for c in self.classes:
            totals.append( len( filter(lambda k: k[1]==c,self.trainingSet) ) )
        #Entropia del sistema
        self.sysEntropy =  calculate_entropy(self.totals.values(), self.trainingSetSize)
        
        for c in characteristics:
            #indiv totals es (por ejemplo):
            #[(sunny_total,[cuantos_sunny_si,cuantos_sunny_no]), (rain_total,[cuantos_rain_si,cuantos_rain_no]),...]
            indiv_totals = get_totals_characteristic(c, CHARACTERISTICS_DICT[c])
            entropies = [] #se convierte en una lista con las entropias de cada valor de "c"
            
            for (total_value,total_of_value_per_class) in indiv_totals:
                #Calcular entropia individual de cada valor posible de la caracteristica "c"
                value_entropy = calculate_entropy(total_of_value_per_class, total_value)
                entropies.append(value_entropy)

            #En base a las entropias de cada valor de "c", calcular la entropia de "c"
            char_entropy = characteristic_entropy([t[0] for t in indiv_totals], entropies, self.trainingSetSize)
            #Calcular la ganancia de esta caracteristica "c"
            char_gain = self.sysEntropy-char_entropy
            #Guardar los calculos para despues
            self.entropyDict.update({c: [char_entropy,char_gain,indiv_totals, entropies]})
            #Tomar en cuenta que las cosas en entropies e indiv_totals[1] estan
            #en el orden de las listas de CHARACTERISTICS_DICT en constants.py


    def get_totals_characteristic(self, characteristicName, characteristicValues):
        """Calculates how many patterns of each value of a certain characteristic are in the system
           And also how many are classified as each possible class on the system"""
        totalsList = []
        for cvalue in characteristicValues:

            total_of_cvalue_in_sys = len( filter(lambda k: k[0].get_characteristic(characteristicName)==cvalue,self.trainingSet) )
            total_per_class_list=[]
            for clase in self.classes:                
                total_of_cvalue_in_clase = len( filter(lambda k: k[0].get_characteristic(characteristicName)==cvalue and k[1]==clase,self.trainingSet) )
                total_per_class_list.append(total_of_cvalue_in_clase)
            
            totalsList.append( (total_of_cvalue_in_sys, total_per_class_list) )
                                                 
        return totalsList

    def characteristic_entropy(self,totals,entropies):
        """Calculates the entropy of certain characteristic according to its possible values entropies"""
        result=0.0
        for i in xrange(totals):
            result+=(totals[i]/self.trainingSetSize)*entropies[i]
        return result
    
    def calculate_entropy(self, individualTotals, totalSystem):
        """General rule to calculate a system entropy given a list of individual totals and the system total"""
        result = 0.0
        for tot in individualTotals:
            fraction = float(tot)/totalSystem
            result+= -fraction * math.log(fraction,2)
        return result
        
    def get_sorted_characteristics(self):
        """Decorate-sort-undecorate method to sort characteristics according to their entropy"""
        to_sort = []
        for charac in self.entropyDict.keys():
            [charac_entropy,charac_gain,indiv_totals,entropies] = self.entropyDict[charac]
            to_sort.append( (charac_gain, [charac_entropy,charac_gain,indiv_totals,entropies]) )

        sorted_tuples = simplifiedDict.items().sort()
        
        self.rootNode = sorted_tuples[-1]
        return [list for gain,list in sorted_tuples]
            

    def build_tree(self):
        """Builds the nodes of the tree with the enough information to be able to classify"""
        #entropy_list contains elements like:
        #[charac_name, char_entropy,char_gain,indiv_totals, entropies]
        entropy_list = get_sorted_characteristics()
        mapping_list = []
        for list in entropy_list:
            (charac_name, char_entropy,char_gain,indiv_totals, entropies) = list
            node = CharacteristicNode(
                        charac_name,
                        EVALUATE_FUNC_DICT[charac_name],
                        CHARACTERISTICS_DICT[charac_name]
                    )
            mapping_list.append( (node,list) )            
        generate_mapping_dict(mapping_list)

    
    def generate_mapping_dict(self,mapping_list):
        """Populates the mappingDict for every node on the tree"""
        index = 0        
        while index < len(mapping_list)-1:
            currentMapping = mapping_list[index]
            currentNode = currentMapping[0]
            (charac_name, char_entropy,char_gain,indiv_totals, entropies) = currentMapping[1]
            charac_val_totals = [t[1] for t in indiv_totals]
            k = 0
            for value_ind_totals in charac_val_totals:
                val = currentNode.possibleValues[k]
                if value_ind_totals.count(0) == (len(value_ind_totals)-1):
                    #Leave node, all are zero except from one
                    #So lets get it's index:
                    for j in xrange(len(charac_val_tots)):
                        if value_ind_totals[j]!=0:
                            break
                    #Add the mapping from the value directly to a Class
                    self.mappingDict.update({val:self.classes[j]})                
                else:
                    self.mappingDict.update({val:mapping_list[index+1][0]}) #Next node in mapping list
                k+=1
        index+=1

    def classify(self, pattern):
        """Determines to which class belongs the received pattern"""
        currentNode = rootNode
        while currentNode not in self.classes:
            result = currentNode.evaluate_func(pattern)
            currentNode = currentNode.mappingDict[result]            
        return currentNode
            
class CharacteristicNode:
    def __init__(self, name, evaluate_func, possibleValues, mappingDict={}):
        self.name = name
        self.evaluate_func = evaluate_func
        self.possibleValues= possibleValues
        self.mappingDict = mappingDict

    def __str__(self):
        return name

