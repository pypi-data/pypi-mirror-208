from kolibri.backend.bn.parameters import parameter_learning
from kolibri.backend.bn.bnlearn import print_CPD


def learn_parameters(model_structure, data, methodtype='maximumlikelihood'):
     model_mle=  parameter_learning.fit(model_structure, data, methodtype=methodtype)
#     print_CPD(model_mle)
     return model_mle



def update_parameters(model_structure, data):
     model_mle=  parameter_learning.fit_update(model_structure, data)
     print_CPD(model_mle)
     return model_mle