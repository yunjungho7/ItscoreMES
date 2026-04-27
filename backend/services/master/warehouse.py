"""창고 서비스"""
from services.base_service import BaseCrudService

warehouse_service = BaseCrudService(
    mapper_path='sql/master/warehouse.xml',
    pk_columns=['WAREHOUSECODE']
)
