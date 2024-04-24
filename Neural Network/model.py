####################################################################################################

##       #### ########  ########     ###    ########  #### ########  ######  
##        ##  ##     ## ##     ##   ## ##   ##     ##  ##  ##       ##    ## 
##        ##  ##     ## ##     ##  ##   ##  ##     ##  ##  ##       ##       
##        ##  ########  ########  ##     ## ########   ##  ######    ######  
##        ##  ##     ## ##   ##   ######### ##   ##    ##  ##             ## 
##        ##  ##     ## ##    ##  ##     ## ##    ##   ##  ##       ##    ## 
######## #### ########  ##     ## ##     ## ##     ## #### ########  ######

####################################################################################################

import torch

###################################################################################################

 ######  ##          ###     ######   ######  ########  ######  
##    ## ##         ## ##   ##    ## ##    ## ##       ##    ## 
##       ##        ##   ##  ##       ##       ##       ##       
##       ##       ##     ##  ######   ######  ######    ######  
##       ##       #########       ##       ## ##             ## 
##    ## ##       ##     ## ##    ## ##    ## ##       ##    ## 
 ######  ######## ##     ##  ######   ######  ########  ######

####################################################################################################

class NeuralNetwork(torch.nn.Module):
#
### Initialization
#
    def __init__(self, hidden_nf=150):
        super(NeuralNetwork, self).__init__()

        self.hidden_nf = hidden_nf

        self.fc01 = torch.nn.Sequential(
            torch.nn.Linear(in_features=4, out_features=hidden_nf, bias=True),
            torch.nn.Tanh()
        )

        self.fc02 = torch.nn.Sequential(
            torch.nn.Linear(in_features=hidden_nf, out_features=hidden_nf, bias=True),
            torch.nn.Tanh()
        )

        self.fc03 = torch.nn.Linear(in_features=hidden_nf, out_features=2, bias=True)

        self.apply(initialize)
#
### Forward pass
#
    def forward(self, adjacency):

        x = self.fc01(adjacency)
        x = self.fc02(x)
        x = self.fc03(x)

        return x

#
### Initialize layers
#
def initialize(layer):
    if isinstance(layer, torch.nn.Linear):
        torch.nn.init.kaiming_uniform_(layer.weight.data, nonlinearity="relu")
        torch.nn.init.constant_(layer.bias.data, 0.0)

####################################################################################################

##     ##  #######  ########  ##     ## ##       ########  ######  
###   ### ##     ## ##     ## ##     ## ##       ##       ##    ## 
#### #### ##     ## ##     ## ##     ## ##       ##       ##       
## ### ## ##     ## ##     ## ##     ## ##       ######    ######  
##     ## ##     ## ##     ## ##     ## ##       ##             ## 
##     ## ##     ## ##     ## ##     ## ##       ##       ##    ## 
##     ##  #######  ########   #######  ######## ########  ######

####################################################################################################

def passdata(x=None, y=None, network=None, criterion=None, optimizer=None, train=False):
    if train:
        optimizer.zero_grad()
        output = network(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()

        return output, loss.item()
    
    with torch.no_grad():
        output = network(x)        
        loss = criterion(output, y)

    return output, loss.item()

def batches(data, network=None, criterion=None, optimizer=None, train=False):

    batch_loss = []

    for batch, coordinates in data:
        output, loss = passdata(x=batch, y=coordinates, network=network, criterion=criterion, optimizer=optimizer, train=train)

        batch_loss.append(loss)

    mean_loss = sum(batch_loss)/len(batch_loss)

    return output, mean_loss

####################################################################################################
