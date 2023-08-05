import os
import pandas as pd
import numpy as np 
import time
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors



###############################################################
###############################################################
#########  Auxliar function interface excel  ##################
###############################################################
###############################################################

#load data from an excel spreadsheet
def ExcelMatrix(namearq, namesheet, Lineini, Columini, columnquantity, linesquantity):
    print('Loading data...')
    df = pd.read_excel(namearq, sheet_name=namesheet, header=None)
    Matriz = df.iloc[Lineini-1:Lineini+linesquantity-1, Columini-1:Columini+columnquantity-1].values.astype(np.float64)
    print('Loading data = ok')
    return Matriz



###############################################################
###############################################################
#########  Auxliar function to statistics   ###################
###############################################################
###############################################################



#Make basic comparative statistics between two sets of data
def Statistics(Calculated, Targeted):

    if np.ndim(Calculated) == 1: #ajusta caso for um vetor e não uma matriz de uma coluna com n linhas
        Calculated = np.reshape(Calculated, (-1, 1))
    if np.ndim(Targeted) == 1:
        Targeted = np.reshape(Targeted, (-1, 1))

    numdata,numevar = Calculated.shape
    
    print('------------------------')
    print ('Statistics between predictor variables and target variables:')
    print('------------------------')
    print('')
      
    for j in range(0,numevar):
        
        erroari = Calculated[:,j] - Targeted[:,j]
        erroper = ( ( Calculated[:,j] - Targeted[:,j] ) / (Targeted[:,j] + 1e-7)  )*100
        coefcorrelacao = np.corrcoef(Targeted[:,j], Calculated[:,j])[1][0]
        
        print ('Correlation coefficient between Calculated and Target, variable ' + str(j+1) +' = ' + str(coefcorrelacao))
        print('')
        print('----- About error = Calculated - Target --------')
        print('')
        print ('Mean difference, variable ' + str(j+1) +' = ' + str(np.mean(erroari)) + ' (' + str(np.mean(erroper)) + '%)')
        print('')
        print ('Standard deviation, variable ' + str(j+1) +' = ' + str(np.std(erroari)) + ' (' + str(np.std(erroper)) + '%)')
        print('')
        print ('Biggest absolute point difference, variable ' + str(j+1) +' = ' + str(np.max(abs(erroari))) + ' ('  + str(np.max(abs(erroper))) + '%)' )
        print('')

        conta=0
        for i in range(0,numdata):
            if abs(erroari[i]) <= 0.1:
                conta=conta+1
        result = 100*conta/numdata
        print('------ Only for classification 0 or 1 -----')
        print('')
        print('Number of hits for a maximum difference of 10% = ' + str(result) + '%' )
        print('')



#Make basic comparative statistics between two sets of data
def Statistics02(Calculated, Targeted, opt):

    if np.ndim(Calculated) == 1: #ajusta caso for um vetor e não uma matriz de uma coluna com n linhas
        Calculated = np.reshape(Calculated, (-1, 1))
    if np.ndim(Targeted) == 1:
        Targeted = np.reshape(Targeted, (-1, 1))
    
    numdata,numevar = Calculated.shape

    erromedio = np.zeros((numevar))
    desviopad = np.zeros((numevar))
    maxerro = np.zeros((numevar))
    coefcorrelacao = np.zeros((numevar))
    erromedioquad = np.zeros((numevar))
         
    for j in range(0,numevar):
        
        erroari = Calculated[:,j] - Targeted[:,j]
        erroquad = (Calculated[:,j] - Targeted[:,j])**2
        
        erromedio[j] = np.mean(erroari) #Mean difference, variable
        desviopad[j] = np.std(erroari) #Standard deviation, variable         
        maxerro[j] = np.max(abs(erroari)) #Biggest absolute point difference, variable
        coefcorrelacao[j] = np.corrcoef(Targeted[:,j], Calculated[:,j])[1][0] #Correlation coefficient between Calculated and Target, variable
        erromedioquad[j] = 0.5*np.mean(erroquad) #Mean square difference, variable
        
    if (opt==1):
        return erromedio
    if (opt==2):
        return desviopad
    if (opt==3):
        return maxerro
    if (opt==4):
        return coefcorrelacao
    if (opt==5):
        return erromedioquad



###############################################################
###############################################################
#########  Auxliar function to graphs   #######################
###############################################################
###############################################################



#Plot two variables ifferences in a sequential series
def PlotComparative(Calculated, Targeted):

    if np.ndim(Calculated) == 1: #ajusta caso for um vetor e não uma matriz de uma coluna com n linhas
        Calculated = np.reshape(Calculated, (-1, 1))
    if np.ndim(Targeted) == 1:
        Targeted = np.reshape(Targeted, (-1, 1))

    numdata,numevar = Calculated.shape
    eixoX = np.arange(0, numdata, dtype=int)

    for j in range(0,numevar):    
        eixoY1= Targeted[:,j]
        eixoY2= Calculated[:,j]
    
        plt.figure(figsize=(12, 5))
        plt.title('Comparison calculated variable vs target')
        plt.xlabel('Sequence of events')
        plt.ylabel('Target and predicted variable ' + str(j+1))
        plt.plot(eixoX, eixoY1, marker = '', label='Target')  
        plt.plot(eixoX, eixoY2, marker = '', label='Calculated')
        #plt.plot(eixoX, eixoY2, c='black', marker = '.', label='Calculated', alpha=0.33)
        plt.legend(loc = "upper left")
        plt.show()





#Plot 3 variables ifferences in a sequential series, min, max, target
def PlotComparativeB3(CalculatedMin, CalculatedMax, Targeted):

    if np.ndim(CalculatedMin) == 1: #ajusta caso for um vetor e não uma matriz de uma coluna com n linhas
        CalculatedMin = np.reshape(CalculatedMin, (-1, 1))
    if np.ndim(CalculatedMax) == 1: 
        CalculatedMax = np.reshape(CalculatedMax, (-1, 1))        
    if np.ndim(Targeted) == 1:
        Targeted = np.reshape(Targeted, (-1, 1))

    numdata,numevar = Targeted.shape
    eixoX = np.arange(0, numdata, dtype=int)

    for j in range(0,numevar):    
        eixoY1= Targeted[:,j]
        eixoY2= CalculatedMin[:,j]
        eixoY3= CalculatedMax[:,j]
        #eixoMed = 0.5*(eixoY2 + eixoY3)
    
        plt.figure(figsize=(12, 5))
        plt.title('Comparison calculated variable range vs target')
        plt.xlabel('Sequence of events')
        plt.ylabel('Target and predicted variable ' + str(j+1))
        
        plt.plot(eixoX, eixoY1, marker = '', label='Target', c='red', alpha=0.7)
        
        #plt.plot(eixoX, eixoY2, marker = '', label='Calculated min', c='black', alpha=0.5)
        #plt.plot(eixoX, eixoY3, marker = '', label='Calculated max', c='black', alpha=0.5)
        plt.fill_between(np.arange(len(eixoY1)), eixoY2, eixoY3, color='gray', alpha=0.7, label='Calculated')
        
        #plt.plot(eixoX, eixoMed, marker = '', label='Calculated', c='black', alpha=0.11)                
        
        plt.legend(loc = "upper left")
        plt.show()
        






#Plot the differences of two variables in a sequential series
def PlotComparative2(Calculated, Targeted, window_size=10):

    if np.ndim(Calculated) == 1: #ajusta caso for um vetor e não uma matriz de uma coluna com n linhas
        Calculated = np.reshape(Calculated, (-1, 1))
    if np.ndim(Targeted) == 1:
        Targeted = np.reshape(Targeted, (-1, 1))

    numdata,numevar = Calculated.shape
    eixoX = np.arange(0, numdata, dtype=int)
            
    for j in range(0,numevar):    
        eixoY1= Targeted[:,j]
        eixoY2= Calculated[:,j]
        
        eixoY3 = eixoY2 - eixoY1

        # preparação para a média móvel
        rolling_mean = pd.Series(eixoY3).rolling(window_size).mean()

        plt.figure(figsize=(12, 5))
        plt.title('Comparison calculated variable vs target')
        plt.xlabel('Sequence of events')
        plt.ylabel('Error, Calculated - Target ' + str(j+1))
        plt.plot(eixoX, eixoY3, marker = '', color = 'darkblue', label='Target')
        # plota a med movel
        plt.plot(eixoX, rolling_mean, marker='', color = mcolors.to_hex((1, 0, 0)), label='Rolling mean', linestyle='dashed') 

        plt.legend(loc = "upper left")
        plt.show()







#Plot two variables ifferences in a sequential series com as faixas de erro conf desvio padrão
def PlotComparative3(Calculated, Targeted):

    if np.ndim(Calculated) == 1: #ajusta caso for um vetor e não uma matriz de uma coluna com n linhas
        Calculated = np.reshape(Calculated, (-1, 1))
    if np.ndim(Targeted) == 1:
        Targeted = np.reshape(Targeted, (-1, 1))
        
    numdata,numevar = Calculated.shape
    eixoX = np.arange(0, numdata, dtype=int)

    for j in range(0,numevar):    
        eixoY1= Targeted[:,j]
        eixoY2= Calculated[:,j]

        # Cálculo do erro médio e desvio padrão
        erro_medio = np.mean(eixoY2 - eixoY1)
        sigma = np.std(eixoY2 - eixoY1)
    
        plt.figure(figsize=(12, 5))
        plt.title('Calculated variable vs target, sigmas range about error = calculated-target')
        plt.xlabel('Sequence of events')
        plt.ylabel('Target and predicted variable ' + str(j+1))
        plt.plot(eixoX, eixoY1, marker = '',  label='Target')  
        plt.plot(eixoX, eixoY2, linestyle='none', c='black', marker = '.', label='Calculated', alpha=0.33)
        plt.legend(loc = "upper right")

        # Preenchendo a área entre as curvas
        plt.fill_between(np.arange(len(eixoY1)), eixoY1 + erro_medio - sigma, eixoY1 + erro_medio + sigma, color='gray', alpha=0.3)
        plt.fill_between(np.arange(len(eixoY1)), eixoY1 + erro_medio - 2*sigma, eixoY1 + erro_medio + 2*sigma, color='gray', alpha=0.2)
        plt.fill_between(np.arange(len(eixoY1)), eixoY1 + erro_medio - 3*sigma, eixoY1 + erro_medio + 3*sigma, color='gray', alpha=0.1)

        # Adicionando o valor do desvio padrão ao canto superior esquerdo do gráfico
        plt.text(0.025, 0.95, "sigma = {:.3f}".format(sigma) + ", average = {:.3f}".format(erro_medio), transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
        
        plt.show()








#Plot 2 sigma lines
def PlotComparative4(Calculated, Targeted):

    if np.ndim(Calculated) == 1: #ajusta caso for um vetor e não uma matriz de uma coluna com n linhas
        Calculated = np.reshape(Calculated, (-1, 1))
    if np.ndim(Targeted) == 1:
        Targeted = np.reshape(Targeted, (-1, 1))
        
    numdata,numevar = Calculated.shape
    eixoX = np.arange(0, numdata, dtype=int)

    for j in range(0,numevar):    
        eixoY1= Targeted[:,j]
        eixoY2= Calculated[:,j]

        # Cálculo do erro médio e desvio padrão
        erro_medio = np.mean(eixoY2 - eixoY1)
        sigma = np.std(eixoY2 - eixoY1)
    
        plt.figure(figsize=(12, 5))
        plt.title('Calculated variable vs target, sigmas range about error = calculated-target')
        plt.xlabel('Sequence of events')
        plt.ylabel('Target and predicted variable ' + str(j+1))
        plt.plot(eixoX, eixoY1, marker = '',  label='Target')

        plt.plot(eixoX, eixoY1 + erro_medio - 2*sigma, marker = '', c='black', alpha=0.5, linestyle='dashed', label='Expected minimum, -2S')
        plt.plot(eixoX, eixoY1 + erro_medio + 2*sigma, marker = '', c='black', alpha=0.5, linestyle='dashed', label='Expected maximum, +2S')
        plt.fill_between(np.arange(len(eixoY1)), eixoY1 + erro_medio - 2*sigma, eixoY1 + erro_medio + 2*sigma, color='gray', alpha=0.1)
                
        #plt.plot(eixoX, eixoY2, linestyle='none', c='black', marker = '.', label='Calculated', alpha=0.33)
        plt.legend(loc = "upper right")

        # Adicionando o valor do desvio padrão ao canto superior esquerdo do gráfico
        plt.text(0.025, 0.95, "sigma = {:.3f}".format(sigma) + ", average = {:.3f}".format(erro_medio), transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
        
        plt.show()


        





#Plot 2 sigma lines of proportion
def PlotComparative5(Calculated, Targeted):

    if np.ndim(Calculated) == 1: #ajusta caso for um vetor e não uma matriz de uma coluna com n linhas
        Calculated = np.reshape(Calculated, (-1, 1))
    if np.ndim(Targeted) == 1:
        Targeted = np.reshape(Targeted, (-1, 1))
        
    numdata,numevar = Calculated.shape
    eixoX = np.arange(0, numdata, dtype=int)

    for j in range(0,numevar):    
        eixoY1= Targeted[:,j]
        eixoY2= Calculated[:,j]

        # Cálculo do erro médio e desvio padrão
        erro_medio = np.mean(eixoY2 / eixoY1)
        sigma = np.std(eixoY2 / eixoY1)
    
        plt.figure(figsize=(12, 5))
        plt.title('Calculated variable vs target, sigmas range about proportional error = calculated/target')
        plt.xlabel('Sequence of events')
        plt.ylabel('Target and predicted variable ' + str(j+1))
        plt.plot(eixoX, eixoY1, marker = '',  label='Target')

        plt.plot(eixoX, eixoY1*erro_medio - 2*sigma*eixoY1, marker = '', c='black', alpha=0.5, linestyle='dashed', label='Expected minimum, -2S')
        plt.plot(eixoX, eixoY1*erro_medio + 2*sigma*eixoY1, marker = '', c='black', alpha=0.5, linestyle='dashed', label='Expected maximum, +2S')
        plt.fill_between(np.arange(len(eixoY1)),eixoY1*erro_medio - 2*sigma*eixoY1, eixoY1*erro_medio + 2*sigma*eixoY1, color='gray', alpha=0.1)
                
        #plt.plot(eixoX, eixoY2, linestyle='none', c='black', marker = '.', label='Calculated', alpha=0.33)
        plt.legend(loc = "upper right")

        # Adicionando o valor do desvio padrão ao canto superior esquerdo do gráfico
        plt.text(0.025, 0.95, "sigma = {:.3f}".format(sigma) + ", average = {:.3f}".format(erro_medio), transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
        
        plt.show()







#Plot correlation between calculated variables and objectives
def PlotCorrelation(Calculated, Targeted):

    if np.ndim(Calculated) == 1: #ajusta caso for um vetor e não uma matriz de uma coluna com n linhas
        Calculated = np.reshape(Calculated, (-1, 1))
    if np.ndim(Targeted) == 1:
        Targeted = np.reshape(Targeted, (-1, 1))
        
    numdata,numevar = Calculated.shape
    eixoX = np.arange(0, numdata, dtype=int)

    for j in range(0,numevar):    
        eixoY1= Targeted[:,j]
        eixoY2= Calculated[:,j]        
        coefcorrelacao = np.corrcoef(eixoY1,eixoY2)[1][0]
        plt.title('Correlation coefficient variable '+ str(j+1)+' = ' + str(coefcorrelacao))
        plt.scatter(eixoY1,eixoY2,color='blue',s=15,edgecolor='red') #grafico de correlação entre as variaveis procuradas e alvo---
        plt.xlabel('Target')
        plt.ylabel('Calculated')    
        plt.show()







#Plot correlation between calculated variables and objectives, com desvio padrão
def PlotCorrelation2(Calculated, Targeted):

    if np.ndim(Calculated) == 1: #ajusta caso for um vetor e não uma matriz de uma coluna com n linhas
        Calculated = np.reshape(Calculated, (-1, 1))
    if np.ndim(Targeted) == 1:
        Targeted = np.reshape(Targeted, (-1, 1))
        
    numdata,numevar = Calculated.shape
    eixoX = np.arange(0, numdata, dtype=int)

    for j in range(0,numevar):    
        eixoY1= Targeted[:,j]
        eixoY2= Calculated[:,j]        
        coefcorrelacao = np.corrcoef(eixoY1,eixoY2)[1][0]
        erro_medio = np.mean(eixoY2 - eixoY1)
        sigma = np.std(eixoY2 - eixoY1)
        valormax = np.max(eixoY1)
        valormin = np.min(eixoY1)
        
        plt.title('Correlation coefficient variable '+ str(j+1)+' = ' + str(coefcorrelacao))
        plt.scatter(eixoY1,eixoY2,color='blue',s=15,edgecolor='red') #grafico de correlação entre as variaveis procuradas e alvo---
        plt.xlabel('Target')
        plt.ylabel('Calculated')    

        plt.plot([valormin,valormax], [valormin,valormax], color='black', alpha=0.9)
        
        plt.plot([valormin,valormax], [valormin+erro_medio-sigma,valormax+erro_medio-sigma], color='red', linestyle='dashed', alpha=0.5)
        plt.plot([valormin,valormax], [valormin+erro_medio+sigma,valormax+erro_medio+sigma], color='red', linestyle='dashed', alpha=0.5)
        
        plt.plot([valormin,valormax], [valormin+erro_medio-2*sigma,valormax+erro_medio-2*sigma], color='green', linestyle='dashed', alpha=0.5)
        plt.plot([valormin,valormax], [valormin+erro_medio+2*sigma,valormax+erro_medio+2*sigma], color='green', linestyle='dashed', alpha=0.5)

        plt.plot([valormin,valormax], [valormin+erro_medio-3*sigma,valormax+erro_medio-3*sigma], color='blue', linestyle='dashed', alpha=0.5)
        plt.plot([valormin,valormax], [valormin+erro_medio+3*sigma,valormax+erro_medio+3*sigma], color='blue', linestyle='dashed', alpha=0.5)
        
        plt.show()












#Plota o erro em relação ao alvo,que é o centro do grafico
def PlotDispe(Calculated, Targeted):

    if np.ndim(Calculated) == 1: #ajusta caso for um vetor e não uma matriz de uma coluna com n linhas
        Calculated = np.reshape(Calculated, (-1, 1))
    if np.ndim(Targeted) == 1:
        Targeted = np.reshape(Targeted, (-1, 1))
        
    numdata,numevar = Calculated.shape
    eixoX = np.arange(0, numdata, dtype=int)

    for j in range(0,numevar):    
        eixoY1 = Targeted[:,j]
        eixoY2 = Calculated[:,j]     
        erro = eixoY2 - eixoY1
        
        erro_medio = np.mean(eixoY2 - eixoY1)
        sigma = np.std(eixoY2 - eixoY1)
        
        valormax = np.max(eixoY1)
        valormin = np.min(eixoY1)
        volormed =(valormin+valormax)/2
        eixoY1norma = (eixoY1 - volormed)/(valormax - volormed)                        

        plt.figure(figsize=(15, 5))
        
        plt.scatter(eixoY1norma,erro,color='blue', s=15, edgecolor='red')
        
        plt.plot([-1,1], [0,0], color='black', alpha=0.9, linestyle='dashed')                

        # Preenchendo a área entre as curvas
        plt.fill_between((-1,1), erro_medio - sigma, erro_medio + sigma, color='gray', alpha=0.3)
        plt.fill_between((-1,1), erro_medio - 2*sigma, erro_medio + 2*sigma, color='gray', alpha=0.2)
        plt.fill_between((-1,1), erro_medio - 3*sigma, erro_medio + 3*sigma, color='gray', alpha=0.1)
        
        plt.title('Dispersion plot, 3 sigma gray gradients, variable '+ str(j+1))
        plt.xlabel('Variable normalized: -1,1')
        plt.ylabel('Variable error = calculated-target')
        
        plt.show()







#Plota o erro em relação ao alvo,que é o centro do grafico
def PlotDispe2(Calculated, Targeted):

    if np.ndim(Calculated) == 1: #ajusta caso for um vetor e não uma matriz de uma coluna com n linhas
        Calculated = np.reshape(Calculated, (-1, 1))
    if np.ndim(Targeted) == 1:
        Targeted = np.reshape(Targeted, (-1, 1))
        
    numdata,numevar = Calculated.shape
    eixoX = np.arange(0, numdata, dtype=int)

    for j in range(0,numevar):    
        eixoY1 = Targeted[:,j]
        eixoY2 = Calculated[:,j]
        
        erro = eixoY2 / eixoY1        
        erro_medio = np.mean(eixoY2 / eixoY1)
        sigma = np.std(eixoY2 / eixoY1)

        valormax = np.max(eixoY1)
        valormin = np.min(eixoY1)
        volormed =(valormin+valormax)/2
        eixoY1norma = (eixoY1 - volormed)/(valormax - volormed)
        
        plt.figure(figsize=(15, 5))
        
        plt.scatter(eixoY1norma, erro ,color='blue', s=15, edgecolor='red')
        
        plt.plot([-1,1], [1,1], color='black', alpha=0.9, linestyle='dashed')                

        # Preenchendo a área entre as curvas
        plt.fill_between((-1,1), erro_medio - sigma, erro_medio + sigma, color='gray', alpha=0.3)
        plt.fill_between((-1,1), erro_medio - 2*sigma, erro_medio + 2*sigma, color='gray', alpha=0.2)
        plt.fill_between((-1,1), erro_medio - 3*sigma, erro_medio + 3*sigma, color='gray', alpha=0.1) 
        
        
        plt.title('Dispersion plot, 3 sigma gray gradients, variable '+ str(j+1))
        plt.xlabel('Variable normalized: -1,1')
        plt.ylabel('Variable proportional error = calculated/target')
        
        plt.show()






#Plota o erro em relação ao alvo,que é o centro do grafico
def PlotDispe3(Calculated, Targeted, minx=0, maxx=0, miny=0, maxy=0):

    if np.ndim(Calculated) == 1: #ajusta caso for um vetor e não uma matriz de uma coluna com n linhas
        Calculated = np.reshape(Calculated, (-1, 1))
    if np.ndim(Targeted) == 1:
        Targeted = np.reshape(Targeted, (-1, 1))
        
    numdata,numevar = Calculated.shape
    eixoX = np.arange(0, numdata, dtype=int)

    for j in range(0,numevar):    
        eixoY1 = Targeted[:,j]
        eixoY2 = Calculated[:,j]

        razao=  eixoY2/eixoY1
        
        eixoY3 = eixoY2 - eixoY1        
        erro_medio = np.mean(eixoY2 - eixoY1)
        sigma = np.std(eixoY2 - eixoY1)
        eixoY4 = (erro_medio/sigma) + eixoY3/sigma
                                
        plt.title('Accuracy Trend Graph, variable '+ str(j+1))
        plt.scatter(eixoY4,razao,color='red', s=15 , marker = '.', alpha=0.1) #grafico de correlação entre as variaveis procuradas e alvo---
        plt.xlabel('Standard deviation sigma')
        plt.ylabel('Proportion error = calculated/target')
        
        if (maxx!=0) or (minx!=0):# Definindo os limites dos eixos x e y se o usuario entrar
            plt.xlim(minx, maxx)
            plt.ylim(miny, maxy)

        plt.plot([-1,1], [1,1], color='black', alpha=0.9, linestyle='dashed')
        plt.plot([0,0], [1-(np.max(razao)-1)*0.5,1+(np.max(razao)-1)*0.5], color='black', alpha=0.9, linestyle='dashed')
        
        plt.show()








#Plota histograma do erro %
def PlotHisto(Calculated, Targeted):

    if np.ndim(Calculated) == 1: #ajusta caso for um vetor e não uma matriz de uma coluna com n linhas
        Calculated = np.reshape(Calculated, (-1, 1))
    if np.ndim(Targeted) == 1:
        Targeted = np.reshape(Targeted, (-1, 1))
    numdata,numevar = Calculated.shape

    for j in range(0,numevar):    
        eixoY1= Targeted[:,j]
        eixoY2= Calculated[:,j]
        
        eixoY3 = eixoY2 - eixoY1 #erro

        fig, ax = plt.subplots()
        
        desviopad = np.std(eixoY3) #devio padrão do erro
        erromedio = np.mean(eixoY3) #erro medio
        
        textstr = '\n'.join((r'$\mathrm{average}=%.3f$' % (erromedio, ),r'$\sigma=%.3f$' % (desviopad, )))

        ax.hist(eixoY3, bins=20, rwidth=0.9, color='blue', alpha=0.7, edgecolor='black')
        # these are matplotlib.patch.Patch properties
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

        # place a text box in upper left in axes coords
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=props)

        plt.title('Error histogram', fontsize=15)
        plt.xlabel('Variable ' + str(j+1) , fontsize=12)
        plt.ylabel('Frequency', fontsize=12)

        plt.show()




###############################################################
###############################################################
#########  Neural network   ###################################
###############################################################
###############################################################



#Neural network 4 layers--------------------------------------------------------------------------------------------------------------------
class nnet4:

    #global variables-------------------------------------------------------------------------
    def __init__ (self, norma=1, coef=0, normout=1, nn1c=1, nn2c=5, nn3c=5, nn4c=1, rate=0.01, epochs=1000, fa2c=5, fa3c=5, fa4c=0, cost=0, regu=0, namenet='', shift=1, iteconv=0, conv=0, sbw=1, c1=2, txt=0, sdnoise=0):
        
        self.nn1c=nn1c
        self.nn2c=nn2c
        self.nn3c=nn3c
        self.nn4c=nn4c
        self.rate=rate
        self.epochs=epochs
        self.fa2c=fa2c
        self.fa3c=fa3c
        self.fa4c=fa4c
        self.norma=norma
        self.coef=coef
        self.normout=normout
        self.cost=cost
        self.regu=regu
        self.namenet=namenet
        self.shift=shift
        self.iteconv=iteconv
        self.conv=conv
        self.sbw=sbw
        self.c1=c1
        self.txt=txt
        self.sdnoise=sdnoise



###############################################################
###############################################################
#########  Auxliar function to normalization   ################
###############################################################
###############################################################



    #data normalization by calculating maximums and minimums-----------------------------------------------
    def Normalize(self, data, maxiname, mininame, medianame, desvioname):          

        #=-1, standardization
        #=0, do anything
        #=1, between 0 and 1
        #=2, between -1 and 1 
        #=3, log(x+coef)
        #=4, log(x+coef)  between 0 and 1
        #=5, log(x+coef)  between -1 and 1
        #=6, log(x+coef)  and standardization

        if (self.norma>=3): 
            data = np.log(data + self.coef)
        normalized = data*1
        
        vetormax = np.max(data,0) 
        vetormin = np.min(data,0)
        if self.shift>1: #aplica o esticamento se tiver
            vetormax=np.where(vetormax < 0, vetormax*(1/self.shift), vetormax*self.shift)
            vetormin=np.where(vetormin < 0, vetormin*self.shift, vetormin*(1/self.shift))

        vetormed = (vetormax+vetormin)/2
        media = np.mean(data,0)
        desvio = np.std(data,0)        
                                    
        if (self.norma==1) or (self.norma==4):  
            normalized = (data - vetormin) / (vetormax - vetormin)
            
        if (self.norma==2) or (self.norma==5):    
            normalized = (data - vetormed) / (vetormax - vetormed)

        if (self.norma==6) or (self.norma==-1):
            normalized = (data - media)/desvio

        np.save(maxiname, vetormax)
        np.save(mininame, vetormin)
        np.save(medianame, media)
        np.save(desvioname, desvio)
        
        return normalized






    #normalizing the data by entering maximums and minimums-----------------------------------------------
    def Normalize2(self, data, maxiname, mininame, medianame, desvioname):         

        vetormax = np.load(maxiname) 
        vetormin = np.load(mininame) 
        vetormed = (vetormax+vetormin)/2
        media = np.load(medianame)
        desvio = np.load(desvioname)  

        if (self.norma>=3): 
            data = np.log(data + self.coef)
        normalized = data*1
                                                
        if (self.norma==1) or (self.norma==4):  
            normalized = (data - vetormin) / (vetormax - vetormin)
            
        if (self.norma==2) or (self.norma==5):    
            normalized = (data - vetormed) / (vetormax - vetormed)                                 

        if (self.norma==6) or (self.norma==-1):
            normalized = (data - media)/desvio
            
        return normalized







    #data denormalization-------------------------------------------------------------------
    def DesNormalize(self, normalized, maxiname, mininame, medianame, desvioname):         

        vetormax = np.load(maxiname) 
        vetormin = np.load(mininame) 
        vetormed = (vetormax+vetormin)/2
        media = np.load(medianame)
        desvio = np.load(desvioname) 
        
        desnorma = normalized*1
                            
        if (self.norma==1) or (self.norma==4):  
            desnorma = normalized * (vetormax - vetormin) + vetormin
            
        if (self.norma==2) or (self.norma==5):  
            desnorma = normalized * (vetormax - vetormed) + vetormed

        if (self.norma==6) or (self.norma==-1):          
            desnorma = normalized*desvio + media

        if (self.norma>=3): 
            desnorma = np.exp(desnorma) - self.coef
                               
        return desnorma




###############################################################
###############################################################
################ Activation functions   #######################
###############################################################
###############################################################



    #Definition of activation functions---------------------------------------------------------
    def Activation(self, typee, x):

        if (typee==0): #linear (-inf,inf)
            y = x
            return y
    
        if (typee==1): #Sigmoide (0,1)
            y = 1/(1+np.exp(-x))
            return y

        if (typee==2): #softpluss (0,inf)
            y = np.log(1+np.exp(x)) #log é na base natural
            return y

        if (typee==3): #gaussinana (0,1)
            y = np.exp(-1*(x**2)) 
            return y

        if (typee==4): #ReLU (0,inf)
            y=np.where(x < 1e-8, 1e-8, x)       
            return y

        if (typee==5): #tanh (-1,1)
            y = (np.exp(x)-np.exp(-x))/(np.exp(x)+np.exp(-x))
            return y

        if (typee==6): #LReLU (-inf,inf)
            y=np.where(x <= 0, x*0.01, x)
            return y
        
        if (typee==7): #arctan (-inf, inf)
            y = np.arctan(x)
            return y

        if (typee==8): #exp (-inf, inf)
            y = np.exp(x)
            return y
    
        if (typee==9): #seno (-inf, inf)
            y = np.sin(x)
            return y

        if (typee==10): #swish (0, inf)
            y = x/(1+np.exp(-x))
            return y

        if (typee==11): #selu (-1, inf)
            y=np.where(x >= 0, x, np.exp(x)-1)
            return y
      
        if (typee==12): #logsigmoide (0,1)
            y = np.log( 1/(1+np.exp(-x)) )
            return y

        if (typee==13): #x^n (inf,inf)
            y = (abs(x))**self.c1
            return y

        if (typee==14): #ELU (-1,inf)
            y=np.where(x <= 0, 1e-8 + 0.1*(np.exp(x)-1), x)
            return y

        if (typee==15): # GoldRelU (inf,inf)
            y = np.where(x > 0, x*1.61803398, x*0.61803398)
            return y

        if (typee==16): # Metallic mean (inf,inf)
            y = (x + (x**2 + 4)**0.5)/2
            return y

        if (typee==17): #NoiseReLU (0,inf)            
            y=np.where(x < 1e-8, 1e-8, x + np.random.normal(0,0.1) )
            return y

        if (typee==18): #ReLUquad (-inf,inf)            
            y=np.where(x <= 0, x, x*x )
            return y


    def DeActivation(self, typee,x):

        if (typee==0): #linear (-inf,inf)
            y = 1
            return y    
    
        if (typee==1): #Sigmoide (0,1)
            w = 1/(1+np.exp(-x))
            y = w*(1-w)
            return y

        if (typee==2): #softpluss (0,inf)
            y = 1/(1 + np.exp(-x))
            return y
    
        if (typee==3): #gaussinana (0,1)
            y = -2*x*np.exp(-1*(x**2)) 
            return y

        if (typee==4): #ReLU (0,inf)
            y=np.where(x < 1e-8, 1e-8, 1)       
            return y    

        if (typee==5): #tanh (-1,1)
            w = (np.exp(x)-np.exp(-x))/(np.exp(x)+np.exp(-x))
            y = 1 - w**2
            return y
    
        if (typee==6): #LReLU (-inf,inf)
            y=np.where(x <= 0, 0.01, 1)        
            return y
    
        if (typee==7): #arctan (-inf, inf)
            y = 1/(1+x**2)
            return y

        if (typee==8): #exp (-inf, inf)
            y = np.exp(x)
            return y

        if (typee==9): #seno (-inf, inf)
            y = np.cos(x)
            return y  

        if (typee==10): #swish (0, inf)
            y = (x/(1+np.exp(-x))) + (1/(1+np.exp(-x)))*(1 - (x/(1+np.exp(-x))) )
            return y

        if (typee==11): #selu (-1, inf)
            y = np.where(x >= 0, 1, np.exp(x))        
            return y        

        if (typee==12): #logsigmoide (0,1)
            y = np.exp(-x)/(1+np.exp(-x))
            return y

        if (typee==13): #x^n (inf,inf)
            y = self.c1*((abs(x))**(self.c1-1))
            return y

        if (typee==14): #ELU (inf,inf)
            y=np.where(x <= 0, 0.1*np.exp(x), 1)
            return y

        if (typee==15): # GoldRelU (inf,inf)
            y = np.where(x > 0, 1.61803398, 0.61803398)
            return y

        if (typee==16): # Metallic mean (inf,inf)
            y = 0.5*((x/((x**2 + 4)**0.5))+1)            
            return y

        if (typee==17): #RandReLU (0,inf)
            y=np.where(x < 1e-8, 1e-8, 1)
            return y

        if (typee==18): #ReLUquad (-inf,inf)            
            y=np.where(x <= 0, 1, 2*x )
            return y
        
###############################################################
###############################################################
################ Machine learning   ###########################
###############################################################
###############################################################
        

    #machine learning,  single batch with ADAM accelerator-----------------------------------------------------
    def Fit_ADAM(self, matX, matY, matX2=[0], matY2=[0]):
        
        tinicio = time.time()
        
        #Criação ou leitura da matriz dos pesos--------

        #pesos
        P12 = np.zeros((self.nn1c,self.nn2c))
        P23 = np.zeros((self.nn2c,self.nn3c))
        P34 = np.zeros((self.nn3c,self.nn4c))

        #bias
        B2= np.zeros((self.nn2c))
        B3= np.zeros((self.nn3c))
        B4= np.zeros((self.nn4c))

        #pesos memorizados
        P12m = np.zeros((self.nn1c,self.nn2c))
        P23m = np.zeros((self.nn2c,self.nn3c))
        P34m = np.zeros((self.nn3c,self.nn4c))

        #bias memorizados
        B2m = np.zeros((self.nn2c))
        B3m = np.zeros((self.nn3c))
        B4m = np.zeros((self.nn4c))

        #variaçao pesos
        VP12 = np.zeros((self.nn1c,self.nn2c))
        VP23 = np.zeros((self.nn2c,self.nn3c))
        VP34 = np.zeros((self.nn3c,self.nn4c))

        #variaçao bias
        VB2= np.zeros((self.nn2c))
        VB3= np.zeros((self.nn3c))
        VB4= np.zeros((self.nn4c))

        #velocidade pesos
        veloP12 = np.zeros((self.nn1c,self.nn2c))
        veloP23 = np.zeros((self.nn2c,self.nn3c))
        veloP34 = np.zeros((self.nn3c,self.nn4c))

        #velocidade bias
        veloB2= np.zeros((self.nn2c))
        veloB3= np.zeros((self.nn3c))
        veloB4= np.zeros((self.nn4c))

        #massa pesos
        massaP12 = np.zeros((self.nn1c,self.nn2c))
        massaP23 = np.zeros((self.nn2c,self.nn3c))
        massaP34 = np.zeros((self.nn3c,self.nn4c))

        #massa bias
        massaB2= np.zeros((self.nn2c))
        massaB3= np.zeros((self.nn3c))
        massaB4= np.zeros((self.nn4c))

        #camadas
        c1= np.zeros((self.nn1c))
        c2= np.zeros((self.nn2c))
        c3= np.zeros((self.nn3c))
        c4= np.zeros((self.nn4c))

        #derivadas
        d1= np.zeros((self.nn1c))
        d2= np.zeros((self.nn2c))
        d3= np.zeros((self.nn3c))
        d4= np.zeros((self.nn4c))

        #erros
        e1= np.zeros((self.nn1c))
        e2= np.zeros((self.nn2c))
        e3= np.zeros((self.nn3c))
        e4= np.zeros((self.nn4c))

        #resultados
        R = np.zeros((self.nn4c))


        #ajuste do local de salvamento, se especificado
        if (self.namenet==''):
            nomepasta=''
        else:
            nomepasta = self.namenet + '/'
            if not os.path.exists(self.namenet):
                os.mkdir(self.namenet)



        try: #Inicializa com pesos ja salvos, se existir esses arquivos-------------------------------------

            net02 = np.load(nomepasta + "net.npy")            
            net01 = self.nn1c + self.nn2c*1e3 + self.nn3c*1e6 + self.nn4c*1e9
            if (net01 != net02):
                input('Neural network saves this different from configured network')
                exit()

            net03 = np.load(nomepasta + "netati.npy")            
            net04 = self.fa2c + self.fa3c*1e3 + self.fa4c*1e6
            if (net03 != net04):
                input('Activation functions saves this different from configured network')
                exit()

            net05 = np.load(nomepasta + "norm.npy")            
            net06 = self.norma + self.normout*1e3
            if (net05 != net06):
                input('Normalization saves this different from configured network')
                exit()

            P12 = np.load(nomepasta + "P12.npy")
            P23 = np.load(nomepasta + "P23.npy")            
            P34 = np.load(nomepasta + "P34.npy")             
            B2 = np.load(nomepasta + "B2.npy")
            B3 = np.load(nomepasta + "B3.npy")
            B4 = np.load(nomepasta + "B4.npy")  

        except: #Inicializa randomicamente-------------------------------

            B2 = -0.1 + 2*0.1*(np.random.rand(self.nn2c))
            B3 = -0.1 + 2*0.1*(np.random.rand(self.nn3c))
            B4 = -0.1 + 2*0.1*(np.random.rand(self.nn4c))    
            P12 = -0.1 + 2*0.1*(np.random.rand(self.nn1c,self.nn2c))
            P23 = -0.1 + 2*0.1*(np.random.rand(self.nn2c,self.nn3c))
            P34 = -0.1 + 2*0.1*(np.random.rand(self.nn3c,self.nn4c))


        #Normaliza os parametros-------------------------
        matX = self.Normalize(matX,nomepasta + "vmax_in.npy",nomepasta + "vmin_in.npy",nomepasta + "media_in.npy",nomepasta + "desvio_in.npy")                
        if (self.normout==1):
            matY = self.Normalize(matY,nomepasta + "vmax_out.npy",nomepasta + "vmin_out.npy",nomepasta + "media_out.npy",nomepasta + "desvio_out.npy")

        #Para validacao cruzada, normaliza em função do conjunto padrão de dados de correção dos pesos
        if (len(matX2)>1):
            matX2 = self.Normalize2(matX2,nomepasta + "vmax_in.npy",nomepasta + "vmin_in.npy",nomepasta + "media_in.npy",nomepasta + "desvio_in.npy") 
            if (self.normout==1):
                matY2 = self.Normalize2(matY2,nomepasta + "vmax_in.npy",nomepasta + "vmin_in.npy",nomepasta + "media_in.npy",nomepasta + "desvio_in.npy") 



        #Processo de aprendizado------------------------------------------------------------
                
        VetorErro = [0]
        MenorErro = 999999999
        
        NumdataEstudo = len(matX) #dados de entrada 
        if (len(matX2)==1):
            NumdataEstudo2 = NumdataEstudo
            matXX = matX*1
            matYY = matY*1          
        else:            
            NumdataEstudo2 = len(matX2)
            matXX = matX2*1
            matYY = matY2*1
            
        Calculated = np.zeros((NumdataEstudo2, self.nn4c)) #inicializa a matriz dos resultados 

        monit=0
        iteconv = self.iteconv
        for ite in range(0,self.epochs): #Processo iterativo global, epocas, cada epoca passa por todos os dados de aprendizagem-----------------
            Tempo = ite+1
    
            if ite > (self.epochs*monit/100): #só um monitor de progresso
                print(str(monit) + '%')
                monit=monit+10
           
            if (self.sbw==1): #Calculo do erro-----------------------------------

                regulariza=0
                if (self.regu!=0): #adiciona a regularização se houver                    
                    regulariza = self.regu*( np.sum(P12*P12) + np.sum(P23*P23) + np.sum(P34*P34) + np.sum(B2*B2) + np.sum(B3*B3) + np.sum(B4*B4) )
    
                EMQ = 0
                for caso in range (0, NumdataEstudo2): #Verificação do aprendizado---

                    #Camada 1, data de entrada  
                    c1 = matXX[caso,:self.nn1c]                                               

                    #propagacao sinal
                    c2 = np.dot(c1,P12)- B2        
                    c2 = self.Activation(self.fa2c,c2)

                    c3 = np.dot(c2,P23)- B3
                    c3 = self.Activation(self.fa3c,c3)
        
                    c4 = np.dot(c3,P34)- B4
                    c4 = self.Activation(self.fa4c,c4)

                    Calculated[caso][:] = c4[:] 

                #calculo efetivo do erro ------------ 
                if (self.cost==0):#erro medio quadratico                 
                    EMQ = ( np.sum( 0.5*((Calculated - matYY)**2) + regulariza ) )/(NumdataEstudo2*self.nn4c)                    
                else: #BCE, entropia cruzada binaria
                    EMQ = ( np.sum( (-1*(matYY*np.log(Calculated +1e-10)+(1-matYY)*np.log((1-Calculated) +1e-10)) + regulariza) ) )/(NumdataEstudo2*self.nn4c)
                
                VetorErro.append(EMQ)
                                               

                #memorização dos melhores pesos-----------
                if (EMQ < MenorErro):
                    itememo = ite+1
                    MenorErro = EMQ
                    P12m = P12*1
                    P23m = P23*1
                    P34m = P34*1
                    B2m = B2*1
                    B3m = B3*1
                    B4m = B4*1


                #encerra o processamento se atender o criterio de convergencia apos n iteracoes---------            
                if (self.conv!=0):
                    if (ite>iteconv):          
                        convcalc = VetorErro[ite+1]/VetorErro[ite+1-self.iteconv]                    
                        iteconv  += self.iteconv                    
                        if (convcalc>=self.conv and convcalc<1):                        
                            break


            #começa os ajustes dos pesos-------------------
            regulariza=0
            if (self.regu!=0): #adiciona a regularização se houver                    
                regulariza = 2*self.regu*( np.sum(P12) + np.sum(P23) + np.sum(P34) + np.sum(B2) + np.sum(B3) + np.sum(B4) )


            #Aplica o ruido nos dados de entrada para ajudar a evitar overfiting------------------
            if (self.sdnoise!=0):
                random_matrix = np.random.normal(1, self.sdnoise, size=(NumdataEstudo, self.nn1c))
                matXr = matX*random_matrix                       
            else:
                matXr = matX*1


            for caso in range (0, NumdataEstudo): #varredura em todos os casos de estudo--------

                #Camada 1, data de entrada
                c1 = matXr[caso,:self.nn1c]
                R = matY[caso,:]                        
                
                #propagacao sinal
                c2 = np.dot(c1,P12)- B2
                d2 = self.DeActivation(self.fa2c,c2)
                c2 = self.Activation(self.fa2c,c2)

                c3 = np.dot(c2,P23)- B3
                d3 = self.DeActivation(self.fa3c,c3)
                c3 = self.Activation(self.fa3c,c3)
        
                c4 = np.dot(c3,P34)- B4
                d4 = self.DeActivation(self.fa4c,c4)
                c4 = self.Activation(self.fa4c,c4)          

                #Calcula o erro da ultima camada
                if (self.cost==0):#EMQ
                    e4 = d4 * ( (R - c4) + regulariza )
                else: #BCE
                    e4 = d4 * ( (R/(c4 +1e-7)) - ((1-R)/(1-c4 +1e-7)) + regulariza )
                
                #Propagação do erro para traz, backprop     
                e3 = np.dot(e4, np.transpose(P34))
                e3 = d3 * e3
            
                e2 = np.dot(e3, np.transpose(P23))
                e2 = d2 * e2

                #Calculo da variação acumulativa bruta dos pesos                
                VP12 += np.dot(c1.reshape(-1, 1), e2.reshape(1, -1))                
                VP23 += np.dot(c2.reshape(-1, 1), e3.reshape(1, -1))
                VP34 += np.dot(c3.reshape(-1, 1), e4.reshape(1, -1))
                
                VB2 += - e2         
                VB3 += - e3      
                VB4 += - e4           

        
            #Atualização efetiva dos pesos----------------------------------

            Gd12 = VP12 / NumdataEstudo
            Gd23 = VP23 / NumdataEstudo
            Gd34 = VP34 / NumdataEstudo

            massaP12 = 0.9*massaP12 + (1-0.9)*Gd12
            massaP23 = 0.9*massaP23 + (1-0.9)*Gd23
            massaP34 = 0.9*massaP34 + (1-0.9)*Gd34

            veloP12 = 0.999*veloP12 + (1-0.999)*(Gd12**2)
            veloP23 = 0.999*veloP23 + (1-0.999)*(Gd23**2)
            veloP34 = 0.999*veloP34 + (1-0.999)*(Gd34**2)

            aux1= 1-(0.9**Tempo)
            aux2 = 1 - (0.999**Tempo)
    
            P12 = P12 + self.rate*( (massaP12/aux1) / np.sqrt(veloP12/aux2) )
            P23 = P23 + self.rate*( (massaP23/aux1) / np.sqrt(veloP23/aux2) )
            P34 = P34 + self.rate*( (massaP34/aux1) / np.sqrt(veloP34/aux2) )
       
            Gd2 = VB2 / NumdataEstudo
            Gd3 = VB3 / NumdataEstudo
            Gd4 = VB4 / NumdataEstudo

            massaB2 = 0.9*massaB2 + (1-0.9)*Gd2
            massaB3 = 0.9*massaB3 + (1-0.9)*Gd3
            massaB4 = 0.9*massaB4 + (1-0.9)*Gd4

            veloB2 = 0.999*veloB2 + (1-0.999)*(Gd2**2)
            veloB3 = 0.999*veloB3 + (1-0.999)*(Gd3**2)
            veloB4 = 0.999*veloB4 + (1-0.999)*(Gd4**2) 
    
            B2 = B2 + self.rate*( (massaB2/aux1) / np.sqrt(veloB2/aux2) )
            B3 = B3 + self.rate*( (massaB3/aux1) / np.sqrt(veloB3/aux2) )
            B4 = B4 + self.rate*( (massaB4/aux1) / np.sqrt(veloB4/aux2) )
 
            VP12 = np.zeros((self.nn1c,self.nn2c))
            VP23 = np.zeros((self.nn2c,self.nn3c))
            VP34 = np.zeros((self.nn3c,self.nn4c))
            VB2= np.zeros((self.nn2c))
            VB3= np.zeros((self.nn3c))
            VB4= np.zeros((self.nn4c))


        print('100%')

        if (self.sbw==1): 
            P12 = P12m*1
            P23 = P23m*1
            P34 = P34m*1
            B2 = B2m*1
            B3 = B3m*1
            B4 = B4m*1


        #Salva os pesos e bias em arquivos txt----------------------------------------------------------
        np.save(nomepasta + "net.npy", self.nn1c + self.nn2c*1e3 + self.nn3c*1e6 + self.nn4c*1e9)
        np.save(nomepasta + "netati.npy", self.fa2c + self.fa3c*1e3 + self.fa4c*1e6)
        np.save(nomepasta + "norm.npy", self.norma + self.normout*1e3)
        
        np.save(nomepasta + "P12.npy", P12)
        np.save(nomepasta + "P23.npy", P23)
        np.save(nomepasta + "P34.npy", P34)
        np.save(nomepasta + "B2.npy", B2)
        np.save(nomepasta + "B3.npy", B3)
        np.save(nomepasta + "B4.npy", B4)

        if (self.sbw==1):
            VetorErro[0] = itememo
            np.save(nomepasta + "Convergencia.npy", VetorErro)

        #Salva os pesos para checagem humana
        np.savetxt(nomepasta + "P12.txt", P12)
        np.savetxt(nomepasta + "P23.txt", P23)
        np.savetxt(nomepasta + "P34.txt", P34)
        np.savetxt(nomepasta + "B2.txt", B2)
        np.savetxt(nomepasta + "B3.txt", B3)
        np.savetxt(nomepasta + "B4.txt", B4)        


        tfim = time.time()
        print('runtime(s) = ' , tfim-tinicio)







    #machine learning stochastic case by case------------------------------------------------------
    def Fit_STOC(self, matX, matY, matX2=[0], matY2=[0]):

        tinicio = time.time()
        
        #Criação ou leitura da matriz dos pesos--------

        #pesos
        P12 = np.zeros((self.nn1c,self.nn2c))
        P23 = np.zeros((self.nn2c,self.nn3c))
        P34 = np.zeros((self.nn3c,self.nn4c))

        #bias
        B2= np.zeros((self.nn2c))
        B3= np.zeros((self.nn3c))
        B4= np.zeros((self.nn4c))

        #pesos memorizados
        P12m = np.zeros((self.nn1c,self.nn2c))
        P23m = np.zeros((self.nn2c,self.nn3c))
        P34m = np.zeros((self.nn3c,self.nn4c))

        #bias memorizados
        B2m = np.zeros((self.nn2c))
        B3m = np.zeros((self.nn3c))
        B4m = np.zeros((self.nn4c))

        #camadas
        c1= np.zeros((self.nn1c))
        c2= np.zeros((self.nn2c))
        c3= np.zeros((self.nn3c))
        c4= np.zeros((self.nn4c))

        #derivadas
        d1= np.zeros((self.nn1c))
        d2= np.zeros((self.nn2c))
        d3= np.zeros((self.nn3c))
        d4= np.zeros((self.nn4c))

        #erros
        e1= np.zeros((self.nn1c))
        e2= np.zeros((self.nn2c))
        e3= np.zeros((self.nn3c))
        e4= np.zeros((self.nn4c))

        #resultados
        R = np.zeros((self.nn4c))


        #ajuste do local de salvamento, se especificado
        if (self.namenet==''):
            nomepasta=''
        else:
            nomepasta = self.namenet + '/'
            if not os.path.exists(self.namenet):
                os.mkdir(self.namenet)


        try: #Inicializa com pesos ja salvos, se existir esses arquivos-------------------------------------

            net02 = np.load(nomepasta + "net.npy")            
            net01 = self.nn1c + self.nn2c*1e3 + self.nn3c*1e6 + self.nn4c*1e9
            if (net01 != net02):
                input('Neural network saves this different from configured network')
                exit()

            net03 = np.load(nomepasta + "netati.npy")            
            net04 = self.fa2c + self.fa3c*1e3 + self.fa4c*1e6
            if (net03 != net04):
                input('Activation functions saves this different from configured network')
                exit()

            net05 = np.load(nomepasta + "norm.npy")            
            net06 = self.norma + self.normout*1e3
            if (net05 != net06):
                input('Normalization saves this different from configured network')
                exit()

            P12 = np.load(nomepasta + "P12.npy")
            P23 = np.load(nomepasta + "P23.npy")            
            P34 = np.load(nomepasta + "P34.npy")             
            B2 = np.load(nomepasta + "B2.npy")
            B3 = np.load(nomepasta + "B3.npy")
            B4 = np.load(nomepasta + "B4.npy")  

        except: #Inicializa randomicamente-------------------------------

            B2 = -0.1 + 2*0.1*(np.random.rand(self.nn2c))
            B3 = -0.1 + 2*0.1*(np.random.rand(self.nn3c))
            B4 = -0.1 + 2*0.1*(np.random.rand(self.nn4c))    
            P12 = -0.1 + 2*0.1*(np.random.rand(self.nn1c,self.nn2c))
            P23 = -0.1 + 2*0.1*(np.random.rand(self.nn2c,self.nn3c))
            P34 = -0.1 + 2*0.1*(np.random.rand(self.nn3c,self.nn4c))


        #Normaliza os parametros-------------------------
        matX = self.Normalize(matX,nomepasta + "vmax_in.npy",nomepasta + "vmin_in.npy",nomepasta + "media_in.npy",nomepasta + "desvio_in.npy")                
        if (self.normout==1):
            matY = self.Normalize(matY,nomepasta + "vmax_out.npy",nomepasta + "vmin_out.npy",nomepasta + "media_out.npy",nomepasta + "desvio_out.npy")

        #Para validacao cruzada, normaliza em função do conjunto padrão de dados de correção dos pesos
        if (len(matX2)>1):
            matX2 = self.Normalize2(matX2,nomepasta + "vmax_in.npy",nomepasta + "vmin_in.npy",nomepasta + "media_in.npy",nomepasta + "desvio_in.npy") 
            if (self.normout==1):
                matY2 = self.Normalize2(matY2,nomepasta + "vmax_in.npy",nomepasta + "vmin_in.npy",nomepasta + "media_in.npy",nomepasta + "desvio_in.npy") 




        #Processo de aprendizado------------------------------------------------------------

        VetorErro = [0]
        MenorErro = 999999999

        NumdataEstudo = len(matX) #dados de entrada 
        if (len(matX2)==1):
            NumdataEstudo2 = NumdataEstudo
            matXX = matX*1
            matYY = matY*1          
        else:            
            NumdataEstudo2 = len(matX2)
            matXX = matX2*1
            matYY = matY2*1

        Calculated = np.zeros((NumdataEstudo2, self.nn4c)) #inicializa a matriz dos resultados 

        monit=0
        iteconv = self.iteconv
        for ite in range(0,self.epochs): #Processo iterativo global, epocas, cada epoca passa por todos os dados de aprendizagem-----------------
            Tempo = ite+1
    
            if ite > (self.epochs*monit/100): #só um monitor de progresso
                print(str(monit) + '%')
                monit=monit+10


            if (self.sbw==1): #Calculo do erro-----------------------------------
            
                regulariza=0
                if (self.regu!=0): #adiciona a regularização se houver                    
                    regulariza = self.regu*( np.sum(P12*P12) + np.sum(P23*P23) + np.sum(P34*P34) + np.sum(B2*B2) + np.sum(B3*B3) + np.sum(B4*B4) )

                EMQ = 0
                for caso in range (0, NumdataEstudo2): #Verificação do aprendizado---

                    #Camada 1, data de entrada
                    c1 = matXX[caso,:self.nn1c]           
                
                    #propagacao sinal
                    c2 = np.dot(c1,P12)- B2        
                    c2 = self.Activation(self.fa2c,c2)

                    c3 = np.dot(c2,P23)- B3
                    c3 = self.Activation(self.fa3c,c3)
        
                    c4 = np.dot(c3,P34)- B4
                    c4 = self.Activation(self.fa4c,c4)         

                    Calculated[caso][:] = c4[:] 
               

                #calculo efetivo do erro ------------ 
                if (self.cost==0):#erro medio quadratico                 
                    EMQ = ( np.sum( 0.5*((Calculated - matYY)**2) + regulariza ) )/(NumdataEstudo2*self.nn4c)                    
                else: #BCE, entropia cruzada binaria
                    EMQ = ( np.sum( (-1*(matYY*np.log(Calculated +1e-10)+(1-matYY)*np.log((1-Calculated) +1e-10)) + regulariza) ) )/(NumdataEstudo2*self.nn4c)
                
                VetorErro.append(EMQ)
                      
 
                #memorização dos melhores pesos------------
                if (EMQ < MenorErro):
                    itememo = ite+1
                    MenorErro = EMQ
                    P12m = P12*1
                    P23m = P23*1
                    P34m = P34*1
                    B2m = B2*1
                    B3m = B3*1
                    B4m = B4*1


                #encerra o processamento se atender o criterio de convergencia apos n iteracoes---------            
                if (self.conv!=0):
                    if (ite>iteconv):          
                        convcalc = VetorErro[ite+1]/VetorErro[ite+1-self.iteconv]                    
                        iteconv  += self.iteconv                    
                        if (convcalc>=self.conv and convcalc<1):                        
                            break


            #Aplica o ruido nos dados de entrada para ajudar a evitar overfiting------------------
            if (self.sdnoise!=0):
                random_matrix = np.random.normal(1, self.sdnoise, size=(NumdataEstudo, self.nn1c))
                matXr = matX*random_matrix                       
            else:
                matXr = matX*1


            for caso in range (0, NumdataEstudo): #varredura em todos os casos, mas no estocastico, atualiza os pesos caso a caso---

                #Camada 1, data de entrada
                c1 = matXr[caso,:self.nn1c]
                R = matY[caso,:]                        
                
                #propagacao sinal
                c2 = np.dot(c1,P12)- B2
                d2 = self.DeActivation(self.fa2c,c2)
                c2 = self.Activation(self.fa2c,c2)

                c3 = np.dot(c2,P23)- B3
                d3 = self.DeActivation(self.fa3c,c3)
                c3 = self.Activation(self.fa3c,c3)
        
                c4 = np.dot(c3,P34)- B4
                d4 = self.DeActivation(self.fa4c,c4)
                c4 = self.Activation(self.fa4c,c4)          

                regulariza=0
                if (self.regu!=0): #adiciona a regularização se houver                    
                    regulariza = 2*self.regu*( np.sum(P12) + np.sum(P23) + np.sum(P34) + np.sum(B2) + np.sum(B3) + np.sum(B4) )

                #Calcula o erro da ultima camada
                if (self.cost==0):#EMQ
                    e4 = d4 * ( (R - c4) + regulariza )
                else: #BCE
                    e4 = d4 * ( (R/(c4 +1e-7)) - ((1-R)/(1-c4 +1e-7)) + regulariza )
                 
                #Propagação do erro para traz, backprop     
                e3 = np.dot(e4, np.transpose(P34))
                e3 = d3 * e3
            
                e2 = np.dot(e3, np.transpose(P23))
                e2 = d2 * e2

                #Atualização dos pesos
                P12 += self.rate*(np.dot(c1.reshape(-1, 1), e2.reshape(1, -1)))
                P23 += self.rate*(np.dot(c2.reshape(-1, 1), e3.reshape(1, -1)))
                P34 += self.rate*(np.dot(c3.reshape(-1, 1), e4.reshape(1, -1)))                
                B2 += - self.rate * e2
                B3 += - self.rate * e3
                B4 += - self.rate * e4
        

        print('100%')

        if (self.sbw==1):
            P12 = P12m*1
            P23 = P23m*1
            P34 = P34m*1
            B2 = B2m*1
            B3 = B3m*1
            B4 = B4m*1


        #Salva os pesos e bias em arquivos txt----------------------------------------------------------
        np.save(nomepasta + "net.npy", self.nn1c + self.nn2c*1e3 + self.nn3c*1e6 + self.nn4c*1e9)
        np.save(nomepasta + "netati.npy", self.fa2c + self.fa3c*1e3 + self.fa4c*1e6)
        np.save(nomepasta + "norm.npy", self.norma + self.normout*1e3)
        
        np.save(nomepasta + "P12.npy", P12)
        np.save(nomepasta + "P23.npy", P23)
        np.save(nomepasta + "P34.npy", P34)
        np.save(nomepasta + "B2.npy", B2)
        np.save(nomepasta + "B3.npy", B3)
        np.save(nomepasta + "B4.npy", B4)

        if (self.sbw==1):
            VetorErro[0] = itememo
            np.save(nomepasta + "Convergencia.npy", VetorErro)

        #Salva os pesos para checagem humana
        np.savetxt(nomepasta + "P12.txt", P12)
        np.savetxt(nomepasta + "P23.txt", P23)
        np.savetxt(nomepasta + "P34.txt", P34)
        np.savetxt(nomepasta + "B2.txt", B2)
        np.savetxt(nomepasta + "B3.txt", B3)
        np.savetxt(nomepasta + "B4.txt", B4)       

        tfim = time.time()
        print('runtime(s) = ' , tfim-tinicio)








    #machine learning,  single batch with ADAM accelerator-----------------------------------------------------
    def Fit_STOC_ADAM(self, matX, matY, matX2=[0], matY2=[0]):

        tinicio = time.time()
        
        #Criação ou leitura da matriz dos pesos--------

        #pesos
        P12 = np.zeros((self.nn1c,self.nn2c))
        P23 = np.zeros((self.nn2c,self.nn3c))
        P34 = np.zeros((self.nn3c,self.nn4c))

        #bias
        B2= np.zeros((self.nn2c))
        B3= np.zeros((self.nn3c))
        B4= np.zeros((self.nn4c))

        #pesos memorizados
        P12m = np.zeros((self.nn1c,self.nn2c))
        P23m = np.zeros((self.nn2c,self.nn3c))
        P34m = np.zeros((self.nn3c,self.nn4c))

        #bias memorizados
        B2m = np.zeros((self.nn2c))
        B3m = np.zeros((self.nn3c))
        B4m = np.zeros((self.nn4c))

        #variaçao pesos
        VP12 = np.zeros((self.nn1c,self.nn2c))
        VP23 = np.zeros((self.nn2c,self.nn3c))
        VP34 = np.zeros((self.nn3c,self.nn4c))

        #variaçao bias
        VB2= np.zeros((self.nn2c))
        VB3= np.zeros((self.nn3c))
        VB4= np.zeros((self.nn4c))

        #velocidade pesos
        veloP12 = np.zeros((self.nn1c,self.nn2c))
        veloP23 = np.zeros((self.nn2c,self.nn3c))
        veloP34 = np.zeros((self.nn3c,self.nn4c))

        #velocidade bias
        veloB2= np.zeros((self.nn2c))
        veloB3= np.zeros((self.nn3c))
        veloB4= np.zeros((self.nn4c))

        #massa pesos
        massaP12 = np.zeros((self.nn1c,self.nn2c))
        massaP23 = np.zeros((self.nn2c,self.nn3c))
        massaP34 = np.zeros((self.nn3c,self.nn4c))

        #massa bias
        massaB2= np.zeros((self.nn2c))
        massaB3= np.zeros((self.nn3c))
        massaB4= np.zeros((self.nn4c))

        #camadas
        c1= np.zeros((self.nn1c))
        c2= np.zeros((self.nn2c))
        c3= np.zeros((self.nn3c))
        c4= np.zeros((self.nn4c))

        #derivadas
        d1= np.zeros((self.nn1c))
        d2= np.zeros((self.nn2c))
        d3= np.zeros((self.nn3c))
        d4= np.zeros((self.nn4c))

        #erros
        e1= np.zeros((self.nn1c))
        e2= np.zeros((self.nn2c))
        e3= np.zeros((self.nn3c))
        e4= np.zeros((self.nn4c))

        #resultados
        R = np.zeros((self.nn4c))


        #ajuste do local de salvamento, se especificado
        if (self.namenet==''):
            nomepasta=''
        else:
            nomepasta = self.namenet + '/'
            if not os.path.exists(self.namenet):
                os.mkdir(self.namenet)



        try: #Inicializa com pesos ja salvos, se existir esses arquivos-------------------------------------

            net02 = np.load(nomepasta + "net.npy")            
            net01 = self.nn1c + self.nn2c*1e3 + self.nn3c*1e6 + self.nn4c*1e9
            if (net01 != net02):
                input('Neural network saves this different from configured network')
                exit()

            net03 = np.load(nomepasta + "netati.npy")            
            net04 = self.fa2c + self.fa3c*1e3 + self.fa4c*1e6
            if (net03 != net04):
                input('Activation functions saves this different from configured network')
                exit()

            net05 = np.load(nomepasta + "norm.npy")            
            net06 = self.norma + self.normout*1e3
            if (net05 != net06):
                input('Normalization saves this different from configured network')
                exit()

            P12 = np.load(nomepasta + "P12.npy")
            P23 = np.load(nomepasta + "P23.npy")            
            P34 = np.load(nomepasta + "P34.npy")             
            B2 = np.load(nomepasta + "B2.npy")
            B3 = np.load(nomepasta + "B3.npy")
            B4 = np.load(nomepasta + "B4.npy")  

        except: #Inicializa randomicamente-------------------------------

            B2 = -0.1 + 2*0.1*(np.random.rand(self.nn2c))
            B3 = -0.1 + 2*0.1*(np.random.rand(self.nn3c))
            B4 = -0.1 + 2*0.1*(np.random.rand(self.nn4c))    
            P12 = -0.1 + 2*0.1*(np.random.rand(self.nn1c,self.nn2c))
            P23 = -0.1 + 2*0.1*(np.random.rand(self.nn2c,self.nn3c))
            P34 = -0.1 + 2*0.1*(np.random.rand(self.nn3c,self.nn4c))


        #Normaliza os parametros-------------------------
        matX = self.Normalize(matX,nomepasta + "vmax_in.npy",nomepasta + "vmin_in.npy",nomepasta + "media_in.npy",nomepasta + "desvio_in.npy")                
        if (self.normout==1):
            matY = self.Normalize(matY,nomepasta + "vmax_out.npy",nomepasta + "vmin_out.npy",nomepasta + "media_out.npy",nomepasta + "desvio_out.npy")

        #Para validacao cruzada, normaliza em função do conjunto padrão de dados de correção dos pesos
        if (len(matX2)>1):
            matX2 = self.Normalize2(matX2,nomepasta + "vmax_in.npy",nomepasta + "vmin_in.npy",nomepasta + "media_in.npy",nomepasta + "desvio_in.npy") 
            if (self.normout==1):
                matY2 = self.Normalize2(matY2,nomepasta + "vmax_out.npy",nomepasta + "vmin_out.npy",nomepasta + "media_out.npy",nomepasta + "desvio_out.npy")



        #Processo de aprendizado------------------------------------------------------------

        VetorErro = [0]
        MenorErro = 999999999

        NumdataEstudo = len(matX) #dados de entrada 
        if (len(matX2)==1):
            NumdataEstudo2 = NumdataEstudo
            matXX = matX*1
            matYY = matY*1          
        else:            
            NumdataEstudo2 = len(matX2)
            matXX = matX2*1
            matYY = matY2*1

        Calculated = np.zeros((NumdataEstudo2, self.nn4c)) #inicializa a matriz dos resultados 

        monit=0
        iteconv = self.iteconv
        for ite in range(0,self.epochs): #Processo iterativo global, epocas, cada epoca passa por todos os dados de aprendizagem-----------------
            Tempo = ite+1
    
            if ite > (self.epochs*monit/100): #só um monitor de progresso
                print(str(monit) + '%')
                monit=monit+10


            if (self.sbw==1): #Calculo do erro-----------------------------------
            
                regulariza=0
                if (self.regu!=0): #adiciona a regularização se houver                    
                    regulariza = self.regu*( np.sum(P12*P12) + np.sum(P23*P23) + np.sum(P34*P34) + np.sum(B2*B2) + np.sum(B3*B3) + np.sum(B4*B4) )

                EMQ = 0
                for caso in range (0, NumdataEstudo2): #Verificação do aprendizado---

                    #Camada 1, data de entrada  
                    c1 = matXX[caso,:self.nn1c]               
                
                    #propagacao sinal
                    c2 = np.dot(c1,P12)- B2        
                    c2 = self.Activation(self.fa2c,c2)

                    c3 = np.dot(c2,P23)- B3
                    c3 = self.Activation(self.fa3c,c3)
        
                    c4 = np.dot(c3,P34)- B4
                    c4 = self.Activation(self.fa4c,c4)

                    Calculated[caso][:] = c4[:] 


                #calculo efetivo do erro ------------ 
                if (self.cost==0):#erro medio quadratico                 
                    EMQ = ( np.sum( 0.5*((Calculated - matYY)**2) + regulariza ) )/(NumdataEstudo2*self.nn4c)                    
                else: #BCE, entropia cruzada binaria
                    EMQ = ( np.sum( (-1*(matYY*np.log(Calculated +1e-10)+(1-matYY)*np.log((1-Calculated) +1e-10)) + regulariza) ) )/(NumdataEstudo2*self.nn4c)
                
                VetorErro.append(EMQ)


                #memorização dos melhores pesos-----------
                if (EMQ < MenorErro):
                    itememo = ite+1
                    MenorErro = EMQ
                    P12m = P12*1
                    P23m = P23*1
                    P34m = P34*1
                    B2m = B2*1
                    B3m = B3*1
                    B4m = B4*1


                #encerra o processamento se atender o criterio de convergencia apos n iteracoes---------            
                if (self.conv!=0):
                    if (ite>iteconv):          
                        convcalc = VetorErro[ite+1]/VetorErro[ite+1-self.iteconv]                    
                        iteconv  += self.iteconv                    
                        if (convcalc>=self.conv and convcalc<1):                        
                            break


            #Aplica o ruido nos dados de entrada para ajudar a evitar overfiting------------------
            if (self.sdnoise!=0):
                random_matrix = np.random.normal(1, self.sdnoise, size=(NumdataEstudo, self.nn1c))
                matXr = matX*random_matrix                       
            else:
                matXr = matX*1


            for caso in range (0, NumdataEstudo): #varredura em todos os casos de estudo--------

                #Camada 1, data de entrada
                c1 = matXr[caso,:self.nn1c]
                R = matY[caso,:]                        
                
                #propagacao sinal
                c2 = np.dot(c1,P12)- B2
                d2 = self.DeActivation(self.fa2c,c2)
                c2 = self.Activation(self.fa2c,c2)

                c3 = np.dot(c2,P23)- B3
                d3 = self.DeActivation(self.fa3c,c3)
                c3 = self.Activation(self.fa3c,c3)
        
                c4 = np.dot(c3,P34)- B4
                d4 = self.DeActivation(self.fa4c,c4)
                c4 = self.Activation(self.fa4c,c4)          

                regulariza=0
                if (self.regu!=0): #adiciona a regularização se houver                    
                    regulariza = 2*self.regu*( np.sum(P12) + np.sum(P23) + np.sum(P34) + np.sum(B2) + np.sum(B3) + np.sum(B4) )

                #Calcula o erro da ultima camada
                if (self.cost==0):#EMQ
                    e4 = d4 * ( (R - c4) + regulariza )
                else: #BCE
                    e4 = d4 * ( (R/(c4 +1e-7)) - ((1-R)/(1-c4 +1e-7)) + regulariza )
                
                #Propagação do erro para traz, backprop     
                e3 = np.dot(e4, np.transpose(P34))
                e3 = d3 * e3
            
                e2 = np.dot(e3, np.transpose(P23))
                e2 = d2 * e2
                                     
        
                #Atualização efetiva dos pesos----------------------------------

                Gd12 = np.dot(c1.reshape(-1, 1), e2.reshape(1, -1))  
                Gd23 = np.dot(c2.reshape(-1, 1), e3.reshape(1, -1)) 
                Gd34 = np.dot(c3.reshape(-1, 1), e4.reshape(1, -1))

                massaP12 = 0.9*massaP12 + (1-0.9)*Gd12
                massaP23 = 0.9*massaP23 + (1-0.9)*Gd23
                massaP34 = 0.9*massaP34 + (1-0.9)*Gd34

                veloP12 = 0.999*veloP12 + (1-0.999)*(Gd12**2)
                veloP23 = 0.999*veloP23 + (1-0.999)*(Gd23**2)
                veloP34 = 0.999*veloP34 + (1-0.999)*(Gd34**2)

                aux1= 1-(0.9**Tempo)
                aux2 = 1 - (0.999**Tempo)
    
                P12 = P12 + self.rate*( (massaP12/aux1) / np.sqrt(veloP12/aux2) )
                P23 = P23 + self.rate*( (massaP23/aux1) / np.sqrt(veloP23/aux2) )
                P34 = P34 + self.rate*( (massaP34/aux1) / np.sqrt(veloP34/aux2) )
       
                Gd2 = - e2 
                Gd3 = - e3 
                Gd4 = - e4 

                massaB2 = 0.9*massaB2 + (1-0.9)*Gd2
                massaB3 = 0.9*massaB3 + (1-0.9)*Gd3
                massaB4 = 0.9*massaB4 + (1-0.9)*Gd4

                veloB2 = 0.999*veloB2 + (1-0.999)*(Gd2**2)
                veloB3 = 0.999*veloB3 + (1-0.999)*(Gd3**2)
                veloB4 = 0.999*veloB4 + (1-0.999)*(Gd4**2) 
    
                B2 = B2 + self.rate*( (massaB2/aux1) / np.sqrt(veloB2/aux2) )
                B3 = B3 + self.rate*( (massaB3/aux1) / np.sqrt(veloB3/aux2) )
                B4 = B4 + self.rate*( (massaB4/aux1) / np.sqrt(veloB4/aux2) )
 

        print('100%')

        if (self.sbw==1):            
            P12 = P12m*1
            P23 = P23m*1
            P34 = P34m*1
            B2 = B2m*1
            B3 = B3m*1
            B4 = B4m*1


        #Salva os pesos e bias em arquivos txt----------------------------------------------------------
        np.save(nomepasta + "net.npy", self.nn1c + self.nn2c*1e3 + self.nn3c*1e6 + self.nn4c*1e9)
        np.save(nomepasta + "netati.npy", self.fa2c + self.fa3c*1e3 + self.fa4c*1e6)
        np.save(nomepasta + "norm.npy", self.norma + self.normout*1e3)

        np.save(nomepasta + "P12.npy", P12)
        np.save(nomepasta + "P23.npy", P23)
        np.save(nomepasta + "P34.npy", P34)
        np.save(nomepasta + "B2.npy", B2)
        np.save(nomepasta + "B3.npy", B3)
        np.save(nomepasta + "B4.npy", B4)

        if (self.sbw==1):
            VetorErro[0] = itememo
            np.save(nomepasta + "Convergencia.npy", VetorErro)

        #Salva os pesos para checagem humana
        np.savetxt(nomepasta + "P12.txt", P12)
        np.savetxt(nomepasta + "P23.txt", P23)
        np.savetxt(nomepasta + "P34.txt", P34)
        np.savetxt(nomepasta + "B2.txt", B2)
        np.savetxt(nomepasta + "B3.txt", B3)
        np.savetxt(nomepasta + "B4.txt", B4)       

        tfim = time.time()
        print('runtime(s) = ' , tfim-tinicio)







###############################################################
###############################################################
################ Aplication of NN   ###########################
###############################################################
###############################################################




    #make prediction----------------------------------------------------------
    def Predict(self, matX):
        
        #pesos
        P12 = np.zeros((self.nn1c,self.nn2c))
        P23 = np.zeros((self.nn2c,self.nn3c))
        P34 = np.zeros((self.nn3c,self.nn4c))
        #bias
        B2= np.zeros((self.nn2c))
        B3= np.zeros((self.nn3c))
        B4= np.zeros((self.nn4c))
        #camadas
        c1= np.zeros((self.nn1c))
        c2= np.zeros((self.nn2c))
        c3= np.zeros((self.nn3c))
        c4= np.zeros((self.nn4c))


        #ajuste do local de salvamento, se especificado
        if (self.namenet==''):
            nomepasta=''
        else:
            nomepasta = self.namenet + '/'
            

        try: #Inicializa com pesos ja salvos, se existir esses arquivos-------------------------------------

            net02 = np.load(nomepasta + "net.npy")            
            net01 = self.nn1c + self.nn2c*1e3 + self.nn3c*1e6 + self.nn4c*1e9
            if (net01 != net02):
                input('Neural network saves this different from configured network')
                exit()

            net03 = np.load(nomepasta + "netati.npy")            
            net04 = self.fa2c + self.fa3c*1e3 + self.fa4c*1e6
            if (net03 != net04):
                input('Activation functions saves this different from configured network')
                exit()

            net05 = np.load(nomepasta + "norm.npy")            
            net06 = self.norma + self.normout*1e3
            if (net05 != net06):
                input('Normalization saves this different from configured network')
                exit()

            P12 = np.load(nomepasta + "P12.npy")
            P23 = np.load(nomepasta + "P23.npy")            
            P34 = np.load(nomepasta + "P34.npy")             
            B2 = np.load(nomepasta + "B2.npy")
            B3 = np.load(nomepasta + "B3.npy")
            B4 = np.load(nomepasta + "B4.npy")  
                
        except: #se nao tem pesos salvos encerra o programa-------------------------------

           input('No saved weight files')
           exit()

        #Normaliza a entrada de data----------------------
        matX = self.Normalize2(matX,nomepasta + "vmax_in.npy",nomepasta + "vmin_in.npy",nomepasta + "media_in.npy",nomepasta + "desvio_in.npy") 

        
        #Predição----------------------------
        numdata = len(matX)
        Calculated = np.zeros((numdata, self.nn4c)) #inicializa a matriz dos resultados Calculated
        
        for caso in range (0, numdata):

            #Camada 1, data de entrada
            c1 = matX[caso,:self.nn1c]                     
                
            #propagacao sinal
            c2 = np.dot(c1,P12)- B2     
            c2 = self.Activation(self.fa2c,c2)

            c3 = np.dot(c2,P23)- B3
            c3 = self.Activation(self.fa3c,c3)
        
            c4 = np.dot(c3,P34)- B4
            c4 = self.Activation(self.fa4c,c4)         

            # saida----------------------------
            Calculated[caso][:] = c4[:]

        if (self.normout==1):            
            Calculated = self.DesNormalize(Calculated, nomepasta + "vmax_out.npy", nomepasta + "vmin_out.npy",nomepasta + "media_out.npy",nomepasta + "desvio_out.npy") 

        if (self.txt!=0): #print txt out data
             np.savetxt(nomepasta + "out.txt", Calculated)

        return Calculated







###############################################################
###############################################################
################ Auxliliar plot   #############################
###############################################################
###############################################################




    #Plota a convergencia ----------------------------------------------------------
    def Plotconv(self):

        if (self.sbw==1):
            
            #ajuste do local de salvamento, se especificado
            if (self.namenet==''):
                nomepasta=''
            else:
                nomepasta = self.namenet + '/'

            
            #grafico da convergencia
            Conve = np.load(nomepasta + "Convergencia.npy")
            tamanho = len(Conve)
        
            MenorErro = np.min(Conve)
            itemenorerro = Conve[0]

            eixoX = np.zeros((tamanho-1)) 
            eixoY = np.zeros((tamanho-1))

            eixoX = np.arange(0, tamanho-1, dtype=int)
            eixoY = Conve[1:tamanho]
    
            plt.figure(figsize=(12, 5))
            plt.title('Mean squared error = ' + str(MenorErro) + ', iteration number = ' + str(itemenorerro))
            plt.xlabel('Study data')
            plt.ylabel('Error, mse')
            plt.plot(eixoX, eixoY, marker = '', color = 'darkblue')  
            plt.show()





###############################################################
###############################################################
################ Auxliliar calculation   ######################
###############################################################
###############################################################


    #Mean squared error  ----------------------------------------------------------
    def MSE(self):

        if (self.sbw==1):
            
            #ajuste do local de salvamento, se especificado
            if (self.namenet==''):
                nomepasta=''
            else:
                nomepasta = self.namenet + '/'

            
            #grafico da convergencia
            Conve = np.load(nomepasta + "Convergencia.npy")
            tamanho = len(Conve)
        
            MenorErro = np.min(Conve)
            itemenorerro = Conve[0]

            return MenorErro


        
