from stim import *
import random
import matplotlib.pyplot as plt
import numpy 
from math import *
import multiprocessing
import copy
import time
import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit.tools.visualization import circuit_drawer
from qiskit.quantum_info import state_fidelity, Statevector
from qiskit import BasicAer
from qiskit.circuit import Parameter
import statistics

class VariationalCircuit_2Fold(Circuit):
    def __init__(self, Qubit_Num: int, Layer_Num: int, Shift_Parameter = 0, r1 = 0, r2 = 0, Assigned_Sampler_Index = [], Assigned_Gate_Index = [], Fake = False) -> None:
        super().__init__('')
        self.Qubit_Num = Qubit_Num
        self.Layer_Num = Layer_Num
        self.Shift_Parameter = Shift_Parameter
        self.Random_Gate_list = []
        self.Random_SingleGate_list = []
        self.Qubit_List = []   #Start from 0
        self.Fake = Fake
        self.Assigned_Sampler_Index = copy.deepcopy(Assigned_Sampler_Index)
        self.Assigned_Gate_Index = copy.deepcopy(Assigned_Gate_Index)
        #print(self.Assigned_Gate_Index)
        #print(self.Assigned_Sampler_Index)
        
        self.Assigned_Gate_Index_Verify()
        self.Assigned_Sampler_Index_Verify()
        self.Assigned_Gate_Index_Generation()
        self.Assigned_Sampler_Index_Generation() 
                
        self.r1 = r1
        self.r2 = r2
        self.p1 = (1 + r2 + 2*r1)/4
        self.p2 = (1 + r2 - 2*r1)/4
        self.p3 = (1 - r2)/4
        self.p4 = (1 - r2)/4
        
        
        for _ in range(self.Layer_Num):
            self.Layer_Generation()
            self.Clifford_Sampler(self.Random_Gate_list[-1])
            self.Insert_Interplayer()
              
                
    
    def Assigned_Gate_Index_Generation(self):
        if len(self.Assigned_Gate_Index) == 0:
            for _ in range(self.Qubit_Num * self.Layer_Num):
                self.Assigned_Gate_Index.append(-1)
    
    def Assigned_Sampler_Index_Generation(self):
        if len(self.Assigned_Sampler_Index) == 0:
            for _ in range(self.Qubit_Num * self.Layer_Num):
                self.Assigned_Sampler_Index.append(-1)
    
    
    def Qubit_List_Generation(self):
        for i in range(2*self.Qubit_Num):
            self.Qubit_List.append(i)
        
        
    def Insert_Interplayer(self):
        for i in range(self.Qubit_Num-1):
            self.append('CZ', [i, i+1])
            if self.Fake == False:
                self.append('CZ', [self.Qubit_Num+i, self.Qubit_Num+i+1])
            
    def Layer_Generation(self):
        Gate_List = []
        for i in range(self.Qubit_Num):
            Gate = self.Assigned_Gate_Index[(len(self.Random_Gate_list))*self.Qubit_Num + i]
            if Gate == -1:
                Gate = random.randint(0, 2)
            if Gate == 0:
                Gate_List.append('Z')
            elif Gate == 1:
                Gate_List.append('X')
            elif Gate == 2:
                Gate_List.append('Y')
        self.Random_Gate_list.append(Gate_List)
        self.Random_SingleGate_list  += Gate_List
        
        
    def Clifford_Sampler(self, Single_Layer_Gate_List: list):
        for i in range(len(Single_Layer_Gate_List)):
            if (len(self.Random_Gate_list)-1)*self.Qubit_Num + i == self.Shift_Parameter:
                if Single_Layer_Gate_List[i] == 'Z':
                    self.Zshift_Sampler(i, Assigned_Index = self.Assigned_Sampler_Index[(len(self.Random_Gate_list)-1)*self.Qubit_Num + i])
                elif Single_Layer_Gate_List[i] == 'X':
                    self.Xshift_Sampler(i, Assigned_Index = self.Assigned_Sampler_Index[(len(self.Random_Gate_list)-1)*self.Qubit_Num + i])
                elif Single_Layer_Gate_List[i] == 'Y':
                    self.Yshift_Sampler(i, Assigned_Index = self.Assigned_Sampler_Index[(len(self.Random_Gate_list)-1)*self.Qubit_Num + i])
            
            else:
                if Single_Layer_Gate_List[i] == 'Z':
                    self.Z_Sampler(i, Assigned_Index = self.Assigned_Sampler_Index[(len(self.Random_Gate_list)-1)*self.Qubit_Num + i])
                elif Single_Layer_Gate_List[i] == 'X':
                    self.X_Sampler(i, Assigned_Index = self.Assigned_Sampler_Index[(len(self.Random_Gate_list)-1)*self.Qubit_Num + i])
                elif Single_Layer_Gate_List[i] == 'Y':
                    self.Y_Sampler(i, Assigned_Index = self.Assigned_Sampler_Index[(len(self.Random_Gate_list)-1)*self.Qubit_Num + i])
                    
    
    def Assigned_Sampler_Index_Verify(self):
        if len(self.Assigned_Sampler_Index)!=0:
            if len(self.Assigned_Sampler_Index)!=self.Qubit_Num*self.Layer_Num:
                raise Exception('The length of Assigned_Sampler_Index is Invalid!')
            for i in self.Assigned_Sampler_Index:
                if i!=0 and i!=1 and i!=2 and i!=3 and i!=-1:
                    raise Exception('The index inside is Invalid!')
                
    def Assigned_Gate_Index_Verify(self):
        if len(self.Assigned_Gate_Index)!=0:
            if len(self.Assigned_Gate_Index)!=self.Qubit_Num*self.Layer_Num:
                raise Exception('The length of Assigned_Gate_Index is Invalid!')
            for i in self.Assigned_Gate_Index:
                if i!=0 and i!=1 and i!=2 and i!=-1:
                    raise Exception('The index inside is Invalid!')
            
            
            
    def X_Sampler(self, Qubit_Indice: int, Assigned_Index = -1):
        self.append('H', Qubit_Indice)
        if self.Fake == False:
            self.append('H', Qubit_Indice + self.Qubit_Num)
        self.Z_Sampler(Qubit_Indice, Assigned_Index)
        self.append('H', Qubit_Indice)
        if self.Fake == False:
            self.append('H', Qubit_Indice + self.Qubit_Num)
    
    def Y_Sampler(self, Qubit_Indice: int, Assigned_Index = -1):
        self.append('S_DAG', Qubit_Indice)
        self.append('H', Qubit_Indice)
        if self.Fake == False:
            self.append('S_DAG', Qubit_Indice + self.Qubit_Num)
            self.append('H', Qubit_Indice + self.Qubit_Num)
        self.Z_Sampler(Qubit_Indice, Assigned_Index)
        self.append('H', Qubit_Indice)
        self.append('S', Qubit_Indice)
        if self.Fake == False:
            self.append('H', Qubit_Indice + self.Qubit_Num)
            self.append('S', Qubit_Indice + self.Qubit_Num)
        
    
    def Z_Sampler(self, Qubit_Indice: int, Assigned_Index = -1):
        if Assigned_Index == -1:
            Scheme = random.randint(0,3)
        if Assigned_Index!=-1:
            Scheme = Assigned_Index
        if Scheme == 0:
            self.append('I', Qubit_Indice)
            if self.Fake == False:
                self.append('I', Qubit_Indice + self.Qubit_Num)
        elif Scheme == 1:
            self.append('Z', Qubit_Indice)
            if self.Fake == False:
                self.append('Z', Qubit_Indice + self.Qubit_Num)
        elif Scheme == 2:
            self.append('S', Qubit_Indice)
            if self.Fake == False:
                self.append('S', Qubit_Indice + self.Qubit_Num)
        elif Scheme == 3:
            self.append('S_DAG', Qubit_Indice)
            if self.Fake == False:
                self.append('S_DAG', Qubit_Indice + self.Qubit_Num)
            
    def Zshift_Sampler(self, Qubit_Indice: int, Assigned_Index = -1):
        self.Z_Sampler(Qubit_Indice, Assigned_Index)
        
    def Xshift_Sampler(self, Qubit_Indice: int, Assigned_Index = -1):
        self.append('H', Qubit_Indice)
        if self.Fake == False:
            self.append('H', Qubit_Indice + self.Qubit_Num)
        self.Zshift_Sampler(Qubit_Indice, Assigned_Index)
        self.append('H', Qubit_Indice)
        if self.Fake == False:
            self.append('H', Qubit_Indice + self.Qubit_Num)
        
    def Yshift_Sampler(self, Qubit_Indice: int, Assigned_Index = -1):
        self.append('S_DAG', Qubit_Indice)
        self.append('H', Qubit_Indice)
        if self.Fake == False:
            self.append('S_DAG', Qubit_Indice + self.Qubit_Num)
            self.append('H', Qubit_Indice + self.Qubit_Num)
        self.Zshift_Sampler(Qubit_Indice, Assigned_Index)
        self.append('H', Qubit_Indice)
        self.append('S', Qubit_Indice)
        if self.Fake == False:
            self.append('H', Qubit_Indice + self.Qubit_Num)
            self.append('S', Qubit_Indice + self.Qubit_Num)
            

    def Zshift_Sampler(self, Qubit_Indice: int, Assigned_Index: -1):
        if self.Fake == True:
            raise Exception('PN Circuit does not support Fake!')
        if Assigned_Index == -1:
            Scheme = random.randint(0,3)
        if Assigned_Index!=-1:
            Scheme = Assigned_Index
        if Scheme == 0:
            self.append('S', Qubit_Indice)
            self.append('S_DAG', Qubit_Indice + self.Qubit_Num)
        elif Scheme == 1:
            self.append('S_DAG', Qubit_Indice)
            self.append('S', Qubit_Indice + self.Qubit_Num)
        elif Scheme == 2:
            self.append('Z', Qubit_Indice)
            self.append('I', Qubit_Indice + self.Qubit_Num)
        elif Scheme == 3:
            self.append('I', Qubit_Indice)
            self.append('Z', Qubit_Indice + self.Qubit_Num)

class VariationalCircuit_2Fold_PP(VariationalCircuit_2Fold):
    def Zshift_Sampler(self, Qubit_Indice: int, Assigned_Index: -1):
        if Assigned_Index == -1:
            Scheme = random.randint(0,3)
        if Assigned_Index!=-1:
            Scheme = Assigned_Index
        if Scheme == 0:
            self.append('I', Qubit_Indice)
            if self.Fake == False:
                self.append('I', Qubit_Indice + self.Qubit_Num)
        elif Scheme == 1:
            self.append('Z', Qubit_Indice)
            if self.Fake == False:
                self.append('Z', Qubit_Indice + self.Qubit_Num)
        elif Scheme == 2:
            self.append('S', Qubit_Indice)
            if self.Fake == False:
                self.append('S', Qubit_Indice + self.Qubit_Num)
        elif Scheme == 3:
            self.append('S_DAG', Qubit_Indice)
            if self.Fake == False:
                self.append('S_DAG', Qubit_Indice + self.Qubit_Num)
    
class VariationalCircuit_2Fold_NN(VariationalCircuit_2Fold):
    def Zshift_Sampler(self, Qubit_Indice: int, Assigned_Index: -1):
        if Assigned_Index == -1:
            Scheme = random.randint(0,3)
        if Assigned_Index!=-1:
            Scheme = Assigned_Index
        if Scheme == 0:
            self.append('I', Qubit_Indice)
            if self.Fake == False:
                self.append('I', Qubit_Indice + self.Qubit_Num)
        elif Scheme == 1:
            self.append('Z', Qubit_Indice)
            if self.Fake == False:
                self.append('Z', Qubit_Indice + self.Qubit_Num)
        elif Scheme == 2:
            self.append('S', Qubit_Indice)
            if self.Fake == False:
                self.append('S', Qubit_Indice + self.Qubit_Num)
        elif Scheme == 3:
            self.append('S_DAG', Qubit_Indice)
            if self.Fake == False:
                self.append('S_DAG', Qubit_Indice + self.Qubit_Num)
    
class VariationalCircuit_2Fold_PN(VariationalCircuit_2Fold):
    def Zshift_Sampler(self, Qubit_Indice: int, Assigned_Index: -1):
        if self.Fake == True:
            raise Exception('PN Circuit does not support Fake!')
        if Assigned_Index == -1:
            Scheme = random.randint(0,3)
        if Assigned_Index!=-1:
            Scheme = Assigned_Index
        if Scheme == 0:
            self.append('S', Qubit_Indice)
            self.append('S_DAG', Qubit_Indice + self.Qubit_Num)
        elif Scheme == 1:
            self.append('S_DAG', Qubit_Indice)
            self.append('S', Qubit_Indice + self.Qubit_Num)
        elif Scheme == 2:
            self.append('Z', Qubit_Indice)
            self.append('I', Qubit_Indice + self.Qubit_Num)
        elif Scheme == 3:
            self.append('I', Qubit_Indice)
            self.append('Z', Qubit_Indice + self.Qubit_Num)
   
def Direct_Estimate(K = 500, Qubit_Num = 3, Layer_Num =1):
    sum = 0
    for _ in range(K):
        theta = [Parameter(f'theta{i}') for i in range(Qubit_Num*Layer_Num)]
        state = Statevector.from_int(0, 2**Qubit_Num)
        qc = QuantumCircuit(Qubit_Num)
        for i in range(Qubit_Num*Layer_Num):
            Gate_Index = random.randint(1, 3)
            if Gate_Index == 1:
                qc.rz(theta[i], i%Qubit_Num)
            elif Gate_Index == 2:
                qc.rx(theta[i], i%Qubit_Num)
            elif Gate_Index == 3:
                qc.ry(theta[i], i%Qubit_Num)
            if (i+1)%Qubit_Num == 0:
                for j in range(Qubit_Num-1):
                    qc.cz(j, j+1)
        random_dict = {theta[i]: random.uniform(-pi, pi) for i in range(Qubit_Num*Layer_Num)}
        random_dictp = copy.deepcopy(random_dict)
        random_dictn = copy.deepcopy(random_dict)
        random_dictp[theta[0]] = random_dictp[theta[0]] + pi/2
        random_dictn[theta[0]] = random_dictn[theta[0]] - pi/2
        circuitp = qc.bind_parameters(random_dictp)
        circuitn = qc.bind_parameters(random_dictn)
        sum+= ((abs(state.evolve(circuitp)[0])**2 - abs(state.evolve(circuitn)[0])**2)/2)**2
        
    #print(circuit.draw())
    #print(abs(state.evolve(circuit)[0])**2)
    return sum/K
         
def Guass_Eliminate(A: numpy.ndarray):
    if A.shape[0] > A.shape[1]:
        raise Exception('The Col is....')
    for i in range(A.shape[0]):
        for j in range(A.shape[0]- i):
            if A[i+j, i] == True: 
                Row_Exchange(A, i, i+j)
                break
        for j in range(A.shape[0]- i- 1):
            if A[i+j+1, i] == True:
                Row_Add(A, i+j+1, i)

def Row_Exchange(A: numpy.ndarray, i: int, j: int):
    B = copy.deepcopy(A[i])
    A[i] = copy.deepcopy(A[j])
    A[j] = copy.deepcopy(B)
    
def Row_Add(A: numpy.ndarray, i: int, j: int):
    Qubit_Num = (A.shape[1]-1)/2
    A[i, -1] = not(A[i, -1] ^ A[j, -1])
    sum = 0
    for k in range(Qubit_Num):
        if A[i, k] and A[j, k+Qubit_Num] == True:
            sum+=1
        if A[i, k+Qubit_Num] and A[j, k] == True:
            sum+=1
    if sum%4 == 2:
        A[i, -1] = not A[i, -1]
    A[i, :-1] = A[i, :-1] ^ A[j, :-1]

def Tableau_to_StaMatrix(Tableau1: Tableau):
    Qubit_Num = len(Tableau1)
    String1 = ''
    Matrix = numpy.ones((Qubit_Num, 2*Qubit_Num+1) , dtype=bool)
    for _ in range(Qubit_Num):
        String1 +='_'
    for i in range(Qubit_Num):
        String2 = String1[:i] + 'Z' + String1[i+1:]
        PauliString1 = PauliString(String2)
        PauliString2 = Tableau1(PauliString1)
        String3 = str(PauliString2)
        #print(String3)
        pos = 0
        for c in String3:
            if c == '+':
                Matrix[i, 2*Qubit_Num] = True
            elif c == '-':
                Matrix[i, 2*Qubit_Num] = False
            elif c == 'X':
                Matrix[i, pos] = True
                Matrix[i, pos + Qubit_Num] = False
                pos = pos + 1
            elif c == 'Y':
                Matrix[i, pos] = True
                Matrix[i, pos + Qubit_Num] = True
                pos = pos + 1
            elif c == 'Z':
                Matrix[i, pos] = False
                Matrix[i, pos + Qubit_Num] = True
                pos = pos + 1
            elif c == '_':
                Matrix[i, pos] = False
                Matrix[i, pos + Qubit_Num] = False
                pos = pos + 1
    
    return Matrix 

def Calculate_Inner_Product_0N(A: numpy.ndarray):
    Qubit_Num = A.shape[0]
    s = Qubit_Num
    for i in range(Qubit_Num):
        flag = True
        for j in range(Qubit_Num):
            if A[i, j] == True:
                flag = False
                break
        if flag == True:
            if A[i, -1] == False:
                Exp = 0
                return Exp
            else:
                s-=1
    Exp = 2**(-s/2)
    return Exp

def Inner_Product_0N(Circuit1: Circuit):
    Simulator1 = TableauSimulator()
    Simulator1.do_circuit(Circuit1)
    Tableau1 = Simulator1.current_inverse_tableau()**-1
    Matrix1 = Tableau_to_StaMatrix(Tableau1)
    Guass_Eliminate(Matrix1)
    return Calculate_Inner_Product_0N(Matrix1)
    
def Real2Fold(K = 500, Layer_Num = 1, Qubit_Num = 3, Assigned_Gate_Index = [], Assigned_Sampler_Index = []):
    Sum1 = 0
    Sum2 = 0
    Sum3 = 0
    flag = True
    if Assigned_Sampler_Index == []:
      flag = False
    for _ in range(K):
      if flag == False:
        Assigned_Sampler_Index = []
        for _ in range(Qubit_Num*Layer_Num):
          Assigned_Sampler_Index.append(random.randint(0,3))   
      Circuit1 = Circuit(repr(VariationalCircuit_2Fold_PP(Qubit_Num, Layer_Num, Assigned_Gate_Index = Assigned_Gate_Index, Assigned_Sampler_Index = Assigned_Sampler_Index ,Fake = False))[17:-5])
      Circuit2 = Circuit(repr(VariationalCircuit_2Fold_NN(Qubit_Num, Layer_Num, Assigned_Gate_Index = Assigned_Gate_Index, Assigned_Sampler_Index = Assigned_Sampler_Index ,Fake = False))[17:-5])
      Circuit3 = Circuit(repr(VariationalCircuit_2Fold_PN(Qubit_Num, Layer_Num, Assigned_Gate_Index = Assigned_Gate_Index, Assigned_Sampler_Index = Assigned_Sampler_Index))[17:-5])
    
      
      Average1 = Inner_Product_0N(Circuit1)**2
      Average2 = Inner_Product_0N(Circuit2)**2
      Average3 = Inner_Product_0N(Circuit3)**2
      
      #print(Average1, Average2, Average3)
    
      Sum1 += Average1
      Sum2 += Average2
      Sum3 += Average3
      
    print((Sum1 + Sum2 - 2*Sum3)/(4*K))
    #print(Sum1/K, Sum2/K, Sum3/K)
    return (Sum1 + Sum2 - 2*Sum3)/(4*K)
  
def Fake2Fold(K = 500, Layer_Num = 1, Qubit_Num = 3, Assigned_Gate_Index = [], Assigned_Sampler_Index = []):
    Sum1 = 0
    Sum2 = 0
    Sum3 = 0
    flag = True
    if Assigned_Sampler_Index == []:
      flag = False
    for _ in range(K):
      if flag == False:
        Assigned_Sampler_Index = []
        for _ in range(Qubit_Num*Layer_Num):
          Assigned_Sampler_Index.append(random.randint(0,3))   
      Circuit1 = Circuit(repr(VariationalCircuit_2Fold_PP(Qubit_Num, Layer_Num, Assigned_Gate_Index = Assigned_Gate_Index, Assigned_Sampler_Index = Assigned_Sampler_Index ,Fake = True))[17:-5])
      Circuit2 = Circuit(repr(VariationalCircuit_2Fold_NN(Qubit_Num, Layer_Num, Assigned_Gate_Index = Assigned_Gate_Index, Assigned_Sampler_Index = Assigned_Sampler_Index ,Fake = True))[17:-5])
      Circuit3 = Circuit(repr(VariationalCircuit_2Fold_PN(Qubit_Num, Layer_Num, Assigned_Gate_Index = Assigned_Gate_Index, Assigned_Sampler_Index = Assigned_Sampler_Index))[17:-5])
    
      Average1 = Inner_Product_0N(Circuit1)**2
      Average2 = Inner_Product_0N(Circuit2)**2
      Average3 = Inner_Product_0N(Circuit3)**2
      
      #print(Average1, Average2, Average3)
      #print((Sum1 + Sum2 - 2*Sum3)/(4))
      Sum1 += Average1**2
      Sum2 += Average2**2
      Sum3 += Average3
      
    #print((Sum1 + Sum2 - 2*Sum3)/(4*K))
    #print(Sum1/K, Sum2/K, Sum3/K)
    return (Sum1 + Sum2 - 2*Sum3)/(4*K)
  
def Weighted_Average_Assigned(Qubit_Num = 3, Layer_Num = 1, r1 = 0, r2 = 0, Assigned_Gate_Index = [1, 2, 0]):
    p0 = (1 + r2 + 2*r1)/4
    p1 = (1 + r2 - 2*r1)/4
    p2 = (1 - r2)/4
    p3 = (1 - r2)/4
    def Search(Assigned_Sampler_Index:list = []):
      if len(Assigned_Sampler_Index) == Qubit_Num * Layer_Num:
        Circuit1 = Circuit(repr(VariationalCircuit_2Fold_PP(Qubit_Num, Layer_Num, Assigned_Gate_Index = Assigned_Gate_Index, Assigned_Sampler_Index=Assigned_Sampler_Index))[17:-5])
        Circuit2 = Circuit(repr(VariationalCircuit_2Fold_NN(Qubit_Num, Layer_Num, Assigned_Gate_Index = Assigned_Gate_Index, Assigned_Sampler_Index=Assigned_Sampler_Index))[17:-5])
        Circuit3 = Circuit(repr(VariationalCircuit_2Fold_PN(Qubit_Num, Layer_Num, Assigned_Gate_Index = Assigned_Gate_Index, Assigned_Sampler_Index=Assigned_Sampler_Index))[17:-5])
        #print((Inner_Product_0N(Circuit1)**2+Inner_Product_0N(Circuit2)**2-2*Inner_Product_0N(Circuit3)**2)/4)
        return (Inner_Product_0N(Circuit1)**2+Inner_Product_0N(Circuit2)**2-2*Inner_Product_0N(Circuit3)**2)/4
      return p0*Search(Assigned_Sampler_Index+[0])+p1*Search(Assigned_Sampler_Index+[1])+p2*Search(Assigned_Sampler_Index+[2])+p0*Search(Assigned_Sampler_Index+[3])
    #print(Search())
    return Search()
          
def Weighted_Average(Qubit_Num = 3, Layer_Num = 1, r1 =0, r2 = 0):
  def Search(Assigned_Gate_Index = []):
    if len(Assigned_Gate_Index) == Qubit_Num*Layer_Num:
      return Weighted_Average_Assigned(Qubit_Num = Qubit_Num, Layer_Num = Layer_Num, r1 = r1, r2 = r2, Assigned_Gate_Index = Assigned_Gate_Index)
    return Search(Assigned_Gate_Index + [0])/3 + Search(Assigned_Gate_Index + [1])/3 + Search(Assigned_Gate_Index + [2])/3
  print(Search())
  return Search()

def Scability_2Fold(N = 8, K = 500, DE = True):
    n = []
    var_cliest = []
    var_direst = []
    for i in range(N-1):
      n.append(i+2)
      cli = Fake2Fold(K = K, Qubit_Num = i+2)
      if DE == True:
        dir = Direct_Estimate(K = K, Qubit_Num = i+2)
        var_direst.append(dir)
      var_cliest.append(cli)
    plt.semilogy(n, var_cliest, marker = '.', markersize = 10, markeredgecolor = '#2376b7')
    plt.semilogy(n, var_cliest, color = '#2376b7', label = 'Clifford Estimation')
    if DE == True:
        plt.semilogy(n, var_direst, marker = '.', markersize = 10, markeredgecolor = '#eb3c70')
        plt.semilogy(n, var_direst, color = '#eb3c70', label = 'Direct Estimation')
    plt.xlim(2,N)
    plt.xlabel('n')
    plt.ylabel(r'$\hat{\mathbb{E}}\left[\partial_{\theta_0} C(\theta)^2\right]$')
    plt.title(f'K={K}')
    plt.legend()
    
def Fake2Fold_Stability(K = 5000, Assigned_Gate_Index = [1, 1, 1], epsilon = 0.1):
  max = 0
  count = 0
  min = 1000
  real_value = Weighted_Average_Assigned(Assigned_Gate_Index = Assigned_Gate_Index)
  for _ in range(100):
    result = Fake2Fold(K = K, Qubit_Num=3, Assigned_Gate_Index = Assigned_Gate_Index )
    if result > max:
      max = result
    if result < min:
      min = result
    if abs(result - real_value) <= epsilon:
      count+=1
  print(f'min={min}', f'max={max}', f'range={(max-min)/2}', f'average={(max+min)/2}', f'confidence={count}%', f'epsilon={epsilon}', f'real_value={real_value}')

def Real2Fold_Stability(K = 5000, Assigned_Gate_Index = [1, 1, 1], epsilon = 0.1):
  max = 0
  count = 0
  min = 1000
  real_value = Weighted_Average_Assigned(Assigned_Gate_Index = Assigned_Gate_Index)
  for _ in range(100):
    result = Real2Fold(K = K, Qubit_Num=3, Assigned_Gate_Index = Assigned_Gate_Index )
    if result > max:
      max = result
    if result < min:
      min = result
    if abs(result - real_value) <= epsilon:
      count+=1
  print(f'min={min}', f'max={max}', f'range={(max-min)/2}', f'average={(max+min)/2}', f'confidence={count}%', f'epsilon={epsilon}', f'real_value={real_value}')

