<b>----------------------------------------------------------------</b> <br> 
Fully connected four-layer neural network <br>
Solves a huge number of cases, classification and regression <br>
Fast, robust and very simple to use, <i> this is the way </i> <br>
(As long as python exists this project will exist) <br>
<b>----------------------------------------------------------------</b> <br> 
<br>
<br>
#Manual = https://www.mediafire.com/file/xygt3o9zf7iw3id/Manual_Tupa123.pdf <br>
<br>
#Quick Guide = https://www.mediafire.com/file/a0db7fb3lfsxvaj/Guia_Rapido.pdf <br>
<br>
#Excel example data = https://www.mediafire.com/file/o2nzsmnvweh8w1a/ALETAS.xlsx<br>
#Excel example (old version) = https://www.mediafire.com/file/0xmx5quakd21txu/ALETAS.xls <br>
<br>
<br>
<br>
#-----FILE TO MACHINE LEARNING----------------------------- <br>
<br>
import tupa123 as tu <br>
<br>
X = tu.ExcelMatrix('ALETAS.xlsx', 'Plan1', Lineini=2, Columini=1, columnquantity=5, linesquantity=300) <br>
y = tu.ExcelMatrix('ALETAS.xlsx', 'Plan1', Lineini=2, Columini=6, columnquantity=2, linesquantity=300) <br>
<br>
model = tu.nnet4(nn1c=5, nn2c=7, nn3c=5, nn4c=2, namenet='tupa01') <br>
model.Fit_ADAM(X, y) <br>
model.Plotconv() <br>
<br>
input('end') <br>
<br>
#-----FILE TO APPLICATION OF MACHINE LEARNING-------------- <br>
<br>
import tupa123 as tu <br>
<br>
model = tu.nnet4(nn1c=5, nn2c=7, nn3c=5, nn4c=2, namenet='tupa01') <br>
X_new = tu.ExcelMatrix('ALETAS.xlsx', 'Plan1', Lineini=2, Columini=1, columnquantity=5, linesquantity=1000) <br>
y_resposta = tu.ExcelMatrix('ALETAS.xlsx', 'Plan1', Lineini=2, Columini=6, columnquantity=2, linesquantity=1000) <br>
y_pred = model.Predict(X_new) <br>
<br>
tu.Statistics(y_pred, y_resposta) <br>
tu.PlotCorrelation(y_pred, y_resposta) <br>
tu.PlotComparative(y_pred, y_resposta) <br>
input('end') <br>
<br>