"""거래처 서비스"""
from services.base_service import BaseCrudService

company_service = BaseCrudService(
    mapper_path='sql/master/company.xml',
    pk_columns=['COMPANYCD']
)
