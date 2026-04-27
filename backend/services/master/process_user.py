"""공정별작업자 서비스"""
from services.base_service import BaseCrudService

process_user_service = BaseCrudService(
    mapper_path='sql/master/process_user.xml',
    pk_columns=['USER_ID', 'PROCESS_ID']
)
