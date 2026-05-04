"""사업장 서비스"""
from services.base_service import BaseCrudService

plant_service = BaseCrudService(
    mapper_path='sql/master/plant.xml',
    pk_columns=['PLANTCD'],
    table_name='TBL_COM_PLANT'
)
