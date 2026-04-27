"""품목 서비스"""
from services.base_service import BaseCrudService

goods_service = BaseCrudService(
    mapper_path='sql/master/goods.xml',
    pk_columns=['PARTNO']
)
