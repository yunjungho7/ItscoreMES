"""공정 서비스"""
from services.base_service import BaseCrudService

process_service = BaseCrudService(
    mapper_path='sql/master/process.xml',
    pk_columns=['PROCESSCD'],
    table_name='TBL_COM_PROCESS'
)
