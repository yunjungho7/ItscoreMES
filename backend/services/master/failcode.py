"""불량코드 서비스"""
from services.base_service import BaseCrudService

failcode_service = BaseCrudService(
    mapper_path='sql/master/failcode.xml',
    pk_columns=['FAILCD']
)
