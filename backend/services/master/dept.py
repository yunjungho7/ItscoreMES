"""부서 서비스"""
from services.base_service import BaseCrudService

dept_service = BaseCrudService(
    mapper_path='sql/master/dept.xml',
    pk_columns=['DEPTCD'],
    table_name='TBL_COM_DEPT'
)
