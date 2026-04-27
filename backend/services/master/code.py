"""공통코드 서비스"""
from services.base_service import BaseCrudService

code_service = BaseCrudService(
    mapper_path='sql/master/code.xml',
    pk_columns=['CODECD']
)
