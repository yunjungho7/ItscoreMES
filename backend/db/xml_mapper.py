"""
MyBatis-style XML Mapper
- #{param} → ? 파라미터 바인딩
- <if test="..."> 조건부 SQL
- <where> 자동 WHERE 절
- <set> 자동 SET 절 (UPDATE용)
"""
import defusedxml.ElementTree as ET
import re
import os


class XMLMapper:
    def __init__(self, xml_path):
        self.xml_path = xml_path
        with open(xml_path, 'r', encoding='utf-8') as f:
            self.tree = ET.parse(f)
        self.root = self.tree.getroot()
        self.namespace = self.root.attrib.get('namespace', '')
        self.elements = {}
        for child in self.root:
            if child.tag in ('select', 'insert', 'update', 'delete', 'sql'):
                query_id = child.attrib.get('id')
                if query_id:
                    self.elements[query_id] = child

    def get_query(self, query_id, params=None):
        """
        주어진 id에 해당하는 쿼리를 동적으로 빌드하여 반환
        Returns: {'query': '...', 'params': [...]} or None
        """
        element = self.elements.get(query_id)
        if element is None:
            return None
        if params is None:
            params = {}
        raw_sql = self._process_element(element, params)
        # #{param} 추출
        param_names = re.findall(r'#\{([^}]+)\}', raw_sql)
        # #{param} → %s
        formatted_query = re.sub(r'#\{[^}]+\}', '%s', raw_sql)
        # 공백 정리
        formatted_query = re.sub(r'\s+', ' ', formatted_query).strip()
        return {
            'query': formatted_query,
            'params': param_names
        }

    # ── 내부 처리 메서드 ──

    def _process_element(self, element, params):
        """엘리먼트의 텍스트와 자식 엘리먼트를 재귀적으로 처리"""
        parts = []
        # 엘리먼트 직접 텍스트
        if element.text:
            parts.append(element.text)
        # 자식 엘리먼트 처리
        for child in element:
            tag = child.tag
            if tag == 'if':
                if self._eval_test(child.attrib.get('test', ''), params):
                    parts.append(self._process_element(child, params))
            elif tag == 'where':
                where_sql = self._process_where(child, params)
                if where_sql:
                    parts.append(' WHERE ' + where_sql)
            elif tag == 'set':
                set_sql = self._process_set(child, params)
                if set_sql:
                    parts.append(' SET ' + set_sql)
            elif tag == 'include':
                refid = child.attrib.get('refid')
                if refid and refid in self.elements:
                    parts.append(self._process_element(self.elements[refid], params))
            # tail 텍스트 (자식 태그 뒤의 텍스트)
            if child.tail:
                parts.append(child.tail)
        return ''.join(parts)

    def _process_where(self, element, params):
        """<where> 블록 처리: 조건이 있으면 WHERE 절 생성, 선행 AND/OR 제거"""
        parts = []
        if element.text and element.text.strip():
            parts.append(element.text)
        for child in element:
            if child.tag == 'if':
                if self._eval_test(child.attrib.get('test', ''), params):
                    parts.append(self._process_element(child, params))
            if child.tail and child.tail.strip():
                parts.append(child.tail)
        content = ' '.join(p.strip() for p in parts if p.strip())
        if not content:
            return ''
        # 선행 AND / OR 제거
        content = re.sub(r'^\s*(AND|OR)\s+', '', content, flags=re.IGNORECASE)
        return content

    def _process_set(self, element, params):
        """<set> 블록 처리: 조건부 SET 절 생성, 후행 콤마 제거"""
        parts = []
        if element.text and element.text.strip():
            parts.append(element.text)
        for child in element:
            if child.tag == 'if':
                if self._eval_test(child.attrib.get('test', ''), params):
                    parts.append(self._process_element(child, params))
            if child.tail and child.tail.strip():
                parts.append(child.tail)
        content = ''.join(parts).strip()
        if not content:
            return ''
        # 후행 콤마 제거
        content = content.rstrip(',').rstrip().rstrip(',')
        return content

    def _eval_test(self, test_expr, params):
        """테스트 표현식 평가 (예: 'param != null', 'param == value')"""
        test_expr = test_expr.strip()
        if not test_expr:
            return False
        # param != null
        m = re.match(r"(\w+)\s*!=\s*null", test_expr, re.IGNORECASE)
        if m:
            key = m.group(1)
            return key in params and params[key] is not None
        # param == null
        m = re.match(r"(\w+)\s*==\s*null", test_expr, re.IGNORECASE)
        if m:
            key = m.group(1)
            return key not in params or params[key] is None
        # param == 'value'
        m = re.match(r"(\w+)\s*==\s*'([^']*)'", test_expr)
        if m:
            return params.get(m.group(1)) == m.group(2)
        # param != 'value'
        m = re.match(r"(\w+)\s*!=\s*'([^']*)'", test_expr)
        if m:
            return params.get(m.group(1)) != m.group(2)
        return False
