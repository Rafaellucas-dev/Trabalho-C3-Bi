import subprocess
import logging
import time
import sys
import os

# Configuração do Logging (Requisito da C3: "Documentar log de execução e tratamento de erros")
log_file = r'c:\Users\Rafael\Desktop\trabalho final\etl_execution.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

scripts_dir = r'c:\Users\Rafael\Desktop\trabalho final\parte da C2\Codigos_Python'
scripts = [
    '01_create_schema.py',
    '02_load_staging.py',
    '03_popula_dim_tempo.py',
    '04_etl_dimensoes.py',
    '05_load_fato.py'
]

def run_script(script_name):
    script_path = os.path.join(scripts_dir, script_name)
    logging.info(f"--- Iniciando a execução do script: {script_name} ---")
    try:
        start_time = time.time()
        # Executa o script e captura o output
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, check=True)
        # Loga o output padrao
        for line in result.stdout.splitlines():
            if line.strip():
                logging.info(f"[{script_name}] {line.strip()}")
                
        elapsed = time.time() - start_time
        logging.info(f"--- Sucesso: {script_name} finalizado em {elapsed:.2f}s ---\n")
    except subprocess.CalledProcessError as e:
        logging.error(f"!!! Erro fatal ao executar {script_name} !!!")
        logging.error(f"Código de retorno: {e.returncode}")
        logging.error(f"Erro detalhado:\n{e.stderr}")
        raise
    except Exception as ex:
        logging.error(f"Erro inesperado no script {script_name}: {str(ex)}")
        raise

if __name__ == "__main__":
    logging.info("==================================================")
    logging.info("INÍCIO DO PIPELINE ETL - PROJETO C3")
    logging.info("==================================================")
    
    total_start = time.time()
    
    try:
        for s in scripts:
            run_script(s)
            
        total_elapsed = time.time() - total_start
        logging.info("==================================================")
        logging.info(f"PIPELINE ETL CONCLUÍDO COM SUCESSO! Tempo total: {total_elapsed:.2f}s")
        logging.info("==================================================")
        
    except Exception as e:
        logging.critical("Pipeline ETL abortado devido a erros.")
        sys.exit(1)
