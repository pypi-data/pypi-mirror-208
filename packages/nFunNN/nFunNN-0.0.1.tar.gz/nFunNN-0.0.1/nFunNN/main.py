import numpy as np
import pandas as pd
from skfda.misc import inner_product_matrix
from skfda import FDataGrid
import skfda.representation.basis as basis
import torch
import torch.nn as nn

def nFunNNmodel(X_ob, t_grid_est, l_FPCA, l_smooth, hidden_size1, bottleneck_size, hidden_size2, lr, batch_size, n_epoch):
    
    m = X_ob.shape[1]
    t_grid = np.linspace(0, 1, num = m)
    
    X_fd = FDataGrid(X_ob, t_grid)
    X_fd_basis = X_fd.to_basis(basis.BSplineBasis(n_basis = l_FPCA))
    X_fd_smooth = X_fd.to_basis(basis.BSplineBasis(n_basis = l_smooth))

    input_data = inner_product_matrix(X_fd_basis, basis.BSplineBasis(n_basis = l_FPCA))
    BS_eval = basis.BSplineBasis(n_basis = l_FPCA).evaluate(t_grid_est)[:, :, 0].T
    response = X_fd_smooth.evaluate(t_grid_est)[:, :, 0]

    input_data = pd.DataFrame(input_data)
    BS_eval = pd.DataFrame(BS_eval)
    response = pd.DataFrame(response)

    response=torch.tensor(response.values,dtype=torch.float)
    input_data=torch.tensor(input_data.values,dtype=torch.float)
    BS_eval=torch.tensor(BS_eval.values,dtype=torch.float)
    
    ####################Model Definition####################
    class NLPCA_Net(nn.Module):
        def __init__(self,input_size,hidden_size1,bottleneck_size,hidden_size2,basis_eval):
            super(NLPCA_Net,self).__init__()

            #Basis eval input
            self.basis_eval=basis_eval.t()

            #First fully connected layer
            self.fc1=nn.Linear(input_size,hidden_size1)

            #Activation Function
            self.Sigmoid=nn.Sigmoid()
            self.ReLU=nn.ReLU()

            #Second fully connected layer
            self.fc2=nn.Linear(hidden_size1,bottleneck_size)
            
            self.fcsupp = nn.Linear(bottleneck_size, hidden_size2)

            #Submodel parallel fully connected layers
            self.fc2_sub = nn.Linear(bottleneck_size, input_size * hidden_size2)

            # Linear output layer
            self.weights=nn.Parameter(torch.randn((hidden_size2,1),
                                                  requires_grad = True))
            
            # Parameter
            # self.submodel_number=submodel_number
            self.hidden_size2=hidden_size2
            
        def forward(self, x):
            out = self.fc1(x)
            out1 = self.ReLU(out)
            out2 = self.fc2(out1)
            
            out2_sub = self.fc2_sub(out2)
            
            out2_sub_basis = torch.matmul(out2_sub.reshape([out2_sub.shape[0], self.hidden_size2, self.basis_eval.shape[0]]), self.basis_eval)
            out2_sub_basis_activation = self.ReLU(out2_sub_basis)
            
            out_final = (out2_sub_basis_activation * self.weights.reshape([1, self.hidden_size2, 1])).sum(axis = 1)
            
            return out_final
    
    ###################Model Realization#######################
    model=NLPCA_Net(input_size = l_FPCA, hidden_size1 = hidden_size1,
                    bottleneck_size = bottleneck_size, hidden_size2 = hidden_size2,
                    basis_eval = BS_eval)
    
    ####################Basis Set######################
    optimizer=torch.optim.Adam(model.parameters(),lr=lr)
    losses=[]
    y=input_data

    for i in range(n_epoch):
        batch_loss=[]
        #Mini-Batch方法进行训练
        for start in range(0,len(y),batch_size):
            end=start+batch_size if start+batch_size<len(y) else len(y)
            xx=y[start:end]
            yy=response[start:end]
            prediction=model(xx)
            loss = ((prediction[:, 1:] - yy[:, 1:]) ** 2).mean()
            optimizer.zero_grad()
            loss.backward(retain_graph=True)
            optimizer.step()
            batch_loss.append(loss.data.numpy())
        losses.append(np.mean(batch_loss))
    
    return model


def nFunNN_CR(model, X_ob, l_FPCA):
    
    m = X_ob.shape[1]
    t_grid = np.linspace(0, 1, num = m)
    
    X_fd = FDataGrid(X_ob, t_grid)
    X_fd_basis = X_fd.to_basis(basis.BSplineBasis(n_basis = l_FPCA))
    input_data = inner_product_matrix(X_fd_basis, basis.BSplineBasis(n_basis = l_FPCA))
    input_data = pd.DataFrame(input_data)
    input_data=torch.tensor(input_data.values,dtype=torch.float)
    
    X_est = model(input_data)
    
    return X_est

