from .Denoising import DenoiseNet
from .NRRN import NRRN


def getDenoisinNetwork(NET_TYPE: str, nbBlocks: int, FeatureMaps: int=64, BatchNormalization=None, DropOut=0.0):
    if NET_TYPE.lower() == 'nrrn':
        print("Creating NRRN model... ", end='')
        return NRRN(nbBlocks, FeatureMaps), 3, "NRRN"
    elif NET_TYPE.lower() == "denoisenet":
        print("Creating DenoiseNet model... ", end='')
        return DenoiseNet(Depth=nbBlocks, FeatureMaps=FeatureMaps, BatchNormalization=BatchNormalization,
                        DropOut=DropOut), 1, "DenoiseNet"
    else:
        return None, None, ""
        #raise Exception("Unknown denoiser model: '" + NET_TYPE + "'. Accepted: NRRN and DenoiseNet.")
