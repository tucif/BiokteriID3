#ID3 Module
import math
import random
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
        self.sysEntropy =  self.calculate_entropy(totals, self.trainingSetSize)
        
        for c in self.characteristics:
            #indiv totals es (por ejemplo):
            #[(sunny_total,[cuantos_sunny_si,cuantos_sunny_no]), (rain_total,[cuantos_rain_si,cuantos_rain_no]),...]
            indiv_totals = self.get_totals_characteristic(c, CHARACTERISTICS_DICT[c])
            entropies = [] #se convierte en una lista con las entropias de cada valor de "c"
            
            for (total_value,total_of_value_per_class) in indiv_totals:
                #Calcular entropia individual de cada valor posible de la caracteristica "c"
                value_entropy = self.calculate_entropy(total_of_value_per_class, total_value)
                entropies.append(value_entropy)

            #En base a las entropias de cada valor de "c", calcular la entropia de "c"
            char_entropy = self.characteristic_entropy([t[0] for t in indiv_totals], entropies)
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
        for i in xrange(len(totals)):
            result+=(totals[i]/self.trainingSetSize)*entropies[i]
        return result
    
    def calculate_entropy(self, individualTotals, totalSystem):
        """General rule to calculate a system entropy given a list of individual totals and the system total"""
        if totalSystem==0:
            print "total system was zero"
            print "global total system: %f"% self.sysEntropy
            return 0.0
        
        result = 0.0
        for tot in individualTotals:
            #print totalSystem
            fraction = float(tot)/totalSystem
            #print "tot: %d  / totalSys: %d= %f"%(tot,totalSystem,fraction)
            if fraction:
                result+= -fraction * math.log(fraction,2)
        return result
        
    def get_sorted_characteristics(self):
        """Decorate-sort-undecorate method to sort characteristics according to their entropy"""
        to_sort = []
        for charac in self.entropyDict.keys():
            [charac_entropy,charac_gain,indiv_totals,entropies] = self.entropyDict[charac]
            to_sort.append( (charac_gain, [charac,charac_entropy,charac_gain,indiv_totals,entropies]) )

        
        to_sort.sort()
        #Here to_sort is sorted, duh!
        sorted_tuples = to_sort
        #the returned list contains elements like:
        #[charac_name, char_entropy,char_gain,indiv_totals, entropies]
        return [list for gain,list in sorted_tuples]
            

    def build_tree(self):
        """Builds the nodes of the tree with the enough information to be able to classify"""
        self.select_root()
        self.genera_arbol(self.rootNode)
#        entropy_list = self.get_sorted_characteristics()
#        mapping_list = []
#        for list in entropy_list:
#            (charac_name, char_entropy,char_gain,indiv_totals, entropies) = list
#            node = CharacteristicNode(
#                        charac_name,
#                        EVALUATE_FUNC_DICT[charac_name],
#                        CHARACTERISTICS_DICT[charac_name]
#                    )
#            mapping_list.append( (node,list) )
#
#        self.rootNode = mapping_list[-1][0]
#        self.generate_mapping_dict(mapping_list)

    def select_root(self):
        entropy_list = self.get_sorted_characteristics()
        root_name = entropy_list[-1][0]
        self.rootNode=CharacteristicNode(
                        root_name,
                        EVALUATE_FUNC_DICT[root_name],
                        CHARACTERISTICS_DICT[root_name]
                    )

    def genera_arbol(self,nodo):
        entropy_dict_entry = self.entropyDict[nodo.name]
        nodo_entropies = entropy_dict_entry[3]
        nodo_totales = entropy_dict_entry[2]
        for rama in nodo.possibleValues:
            index_rama = nodo.possibleValues.index(rama)
            
            rama_total, rama_totales_clase = nodo_totales[index_rama]
            index_clase = self.es_clase(rama_totales_clase)
            if index_clase != -1:                
                nodo.mappingDict.update({rama:self.classes[index_clase]})                
            else:                
                
                rama_entropy = nodo_entropies[index_rama]

                next_hierarchy = nodo.hierarchy+[nodo.name]
                next_node = self.get_max_gain_node(rama_totales_clase, rama_entropy, next_hierarchy )

                nodo.mappingDict.update({rama: next_node})
                self.genera_arbol(next_node)

    def es_clase(self, totales_por_clase):
        class_index = -1
        if totales_por_clase.count(0) == (len(totales_por_clase)-1):
            #Leaf node, all are zero except from one
            #So lets get it's index:            
            for j in xrange(len(totales_por_clase)):
                if totales_por_clase[j]!=0:
                    class_index = j
                    break
        return class_index

                                    
    def get_max_gain_node(self,rama_totales_clase, rama_entropy, hierarchy):
        
        max_gain=0
        selected_nodo_name = ""
        #Depurar jerarquia, verificar unicamente los no utilizados previamente
        node_list = []
        for car in self.characteristics:
            node_list.append(car)
        
        for nod in hierarchy:
            node_list.remove(nod)
       
        #TEMP VALIDATION;
        if not node_list:
            #Ultimo nodo, debe generar clases
            #Genera un nodo de la clase mas comun en sus entropias relativas
            most_common_class_index=0
            for i in xrange(len(rama_totales_clase)):
                if rama_totales_clase[i] > most_common_class_index:
                    most_common_class_index = i
            
            return self.classes[most_common_class_index]            
        

        for nodo_name in node_list:
            nodo_entropy = self.entropyDict[nodo_name][0]
            nodo_relative_gain =(rama_entropy - nodo_entropy)
            if  nodo_relative_gain > max_gain:
                max_gain = nodo_relative_gain
                selected_nodo_name = nodo_name

        max_gain_node = CharacteristicNode(
                        selected_nodo_name,
                        EVALUATE_FUNC_DICT[selected_nodo_name],
                        CHARACTERISTICS_DICT[selected_nodo_name]
                    )
        max_gain_node.hierarchy=hierarchy
        return max_gain_node

    def generate_mapping_dict(self,mapping_list):
        """Populates the mappingDict for every node on the tree"""
        index = 0        
        while index < len(mapping_list)-1:
            currentMapping = mapping_list[index]            
            currentNode = currentMapping[0]
            #FUCKIN NECESSARY LINE:
            currentNode.mappingDict = {}
            #print "Current node", currentNode
            (charac_name, char_entropy,char_gain,indiv_totals, entropies) = currentMapping[1]
            charac_val_totals = [t[1] for t in indiv_totals]
            k = 0
            for value_ind_totals in charac_val_totals:
                #print currentNode
                #print currentNode.possibleValues
                val = currentNode.possibleValues[k]
                #print val
                #print value_ind_totals
                if value_ind_totals.count(0) == (len(value_ind_totals)-1):
                    print "if---"
                    #Leave node, all are zero except from one
                    #So lets get it's index:
                    for j in xrange(len(value_ind_totals)):
                        if value_ind_totals[j]!=0:
                            break
                    #Add the mapping from the value directly to a Class
                    currentNode.mappingDict.update({val:self.classes[j]})
                else:
                    currentNode.mappingDict.update({val:mapping_list[index+1][0]}) #Next node in mapping list
                k+=1
            #print currentNode.mappingDict
            index+=1

        lastNode = mapping_list[-1][0]
        for i in xrange(len(lastNode.possibleValues)):
            v = lastNode.possibleValues[i]
            #CHANGE THIS: random just to test
            lastNode.mappingDict.update({v:random.choice(self.classes)})
        print lastNode.mappingDict


    def print_tree(self):
       self._print_aux(self.rootNode)

    def _print_aux(self, node):
        if isinstance(node, CharacteristicNode):
            print "Node: %s"%node
            print node.mappingDict
            print "Possible values:"
            print node.possibleValues
            for val in node.possibleValues:
                self._print_aux(node.mappingDict[val])
        else:
            #Its a class Node (string)
            print "Class node: %s"% node
            


    def classify(self, pattern):
        """Determines to which class belongs the received pattern"""
        currentNode = self.rootNode
        while currentNode not in self.classes:
            result = currentNode.evaluate_func(pattern)
            currentNode = currentNode.mappingDict[result]
        pattern.name="Classified: %s"% str(currentNode)
        return currentNode
            
class CharacteristicNode:
    def __init__(self, name, evaluate_func, possibleValues, mappingDict={}):
        self.name = name
        self.evaluate_func = evaluate_func
        self.possibleValues= possibleValues
        self.mappingDict = mappingDict
        self.hierarchy = [] #Jerarquia de nodos padres

    def __str__(self):
        return self.name

