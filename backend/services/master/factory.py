"""공장 서비스 (채번 로직 포함)"""
from services.base_service import BaseCrudService


class FactoryService(BaseCrudService):
    """공장 서비스 - 사업장별 다음 공장코드 채번 기능 추가"""

    def get_next_code(self, plant_cd: str) -> str:
        """사업장코드 기반으로 다음 공장코드를 자동 생성 (예: P01-F001, P01-F002 ...)"""
        rows = self._execute_select('selectLastCode', {'plant_cd': plant_cd})
        if rows:
            last_code = rows[0].get('FACTORYCD', '')
            try:
                seq_part = last_code.split('-F')[-1]
                next_seq = int(seq_part) + 1
            except (ValueError, IndexError):
                next_seq = 1
        else:
            next_seq = 1
        return f"{plant_cd}-F{next_seq:03d}"


factory_service = FactoryService(
    mapper_path='sql/master/factory.xml',
    pk_columns=['FACTORYCD']
)
