"""Location 서비스"""
from services.base_service import BaseCrudService

location_service = BaseCrudService(
    mapper_path='sql/master/location.xml',
    pk_columns=['LOCATIONCODE']
)
