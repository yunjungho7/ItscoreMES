"""라인 서비스"""
from services.base_service import BaseCrudService

line_service = BaseCrudService(
    mapper_path='sql/master/line.xml',
    pk_columns=['LINECD'],
    table_name='TBL_COM_LINE'
)
