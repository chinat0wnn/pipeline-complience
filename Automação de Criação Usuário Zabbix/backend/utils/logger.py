import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name="provisioning_api"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Console handler for container logs (AKS/Docker)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(ch)
        
    return logger

def setup_audit_logger(name="audit"):
    audit_logger = logging.getLogger(name)
    audit_logger.setLevel(logging.INFO)
    
    # Criar pasta de logs se não existir
    os.makedirs('logs', exist_ok=True)
    
    # Handler de arquivo com rotação (max 5MB por arquivo, guarda os últimos 5)
    fh = RotatingFileHandler('logs/audit.log', maxBytes=5*1024*1024, backupCount=5, encoding='utf-8')
    fh.setLevel(logging.INFO)
    
    # Formato focado em auditoria: Data | IP (se passado na string) | Ação
    formatter = logging.Formatter('%(asctime)s | AUDIT | %(message)s')
    fh.setFormatter(formatter)
    
    if not audit_logger.handlers:
        audit_logger.addHandler(fh)
        
    return audit_logger

logger = setup_logger()
audit_logger = setup_audit_logger()
