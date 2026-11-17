import os
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
import ssl
import certifi

##FOR WINDOWS TRANKIT
def fix_certifi_ssl_context():
    # 1. Environment variables fallback
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

    # 2. Hard-override the context creation to never look at the Windows Store
    def crash_proof_create_default_context(purpose=ssl.Purpose.SERVER_AUTH, *args, **kwargs):
        # Create a raw, completely empty context for the given protocol
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT if purpose == ssl.Purpose.SERVER_AUTH else ssl.PROTOCOL_TLS_SERVER)
        
        # Manually configure the secure defaults usually handled by create_default_context
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1
        
        # Load ONLY certifi's clean, verified bundle, bypassing the Windows OS store entirely
        context.load_verify_locations(cafile=certifi.where())
        return context

    # Replace the native function with our safe version
    ssl.create_default_context = crash_proof_create_default_context




import random
import numpy as np
import torch

from src.constants import RANDOM_SEED

def set_seed(seed=RANDOM_SEED):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True 
    torch.backends.cudnn.benchmark = False      
    torch.use_deterministic_algorithms(True)