from kolibri.backend.bn.inference import inference


def predict(model, variables, evidence):

    return inference.fit(model, variables=variables, evidence=evidence)