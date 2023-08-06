from collections import namedtuple

import pandas as pd
from sqlalchemy import text

from hawa.base.db import DbUtil
from hawa.base.decos import singleton


@singleton
class DataQuery:
    db = DbUtil()

    def query_unit(self, meta_unit_type: str, meta_unit_id: str):
        MetaUnit = namedtuple("MetaUnit", ["id", "name", "short_name"])
        match meta_unit_type:
            case 'school':
                sql = f"select id,name,short_name from schools where id={meta_unit_id};"
                data = self.db.query_by_sql(sql=sql, mode='one')
                meta_unit = MetaUnit(**data)
            case 'district' | 'city' | 'province':
                sql = f"select id,name from locations where id={meta_unit_id};"
                data = self.db.query_by_sql(sql=sql, mode='one')
                meta_unit = MetaUnit(**data, short_name=data['name'])
            case _:
                meta_unit = MetaUnit(id=0, name='全国', short_name='全国')
        return meta_unit

    def query_schools_all(self):
        sql = f"select id, name, short_name, created from schools;"
        return pd.read_sql(text(sql), self.db.engine_conn)

    def query_schools_by_ids(self, school_ids: list[int]):
        if len(school_ids) == 0:
            return []
        elif len(school_ids) == 1:
            sql = f"select id, name, short_name, created from schools where id={school_ids[0]};"
        else:
            sql = f"select id, name, short_name, created from schools where id in {tuple(school_ids)};"
        return pd.read_sql(text(sql), self.db.engine_conn)

    def query_schools_by_startwith(self, startwith: int):
        param_len = len(str(startwith))
        sql = f"select id, name, short_name, created from schools where left(id,{param_len})={startwith};"
        return pd.read_sql(text(sql), self.db.engine_conn)

    def query_papers(self, test_type: str = '', test_types: list[str] = None):
        """优先 test_types"""
        if test_types:
            sql = f"select id, name, grade, test_type, created from papers where test_type in {tuple(test_types)};"
        elif test_type:
            sql = f"select id, name, grade, test_type, created from papers where test_type='{test_type}';"
        else:
            raise
        return pd.read_sql(text(sql), self.db.engine_conn)

    def query_cases(
            self, school_ids: list[int], paper_ids: list[int],
            valid_to_start: str, valid_to_end: str,
    ):
        if len(paper_ids) == 0:
            return pd.DataFrame()
        elif len(paper_ids) == 1:
            paper_sql = f"and c.paper_id={paper_ids[0]}"
        else:
            paper_sql = f"and c.paper_id in {tuple(paper_ids)}"

        if len(school_ids) == 0:
            return pd.DataFrame()
        elif len(school_ids) == 1:
            school_sql = f"and cs.school_id={school_ids[0]}"
        else:
            school_sql = f"and cs.school_id in {tuple(school_ids)}"

        sql = f"select c.id,c.name,c.valid_from,c.valid_to,c.client_id,c.created," \
              f"c.paper_id,c.is_cleared, cp.name project_name, c.project_id " \
              f"from cases c " \
              f"inner join case_schools cs on c.id=cs.case_id " \
              f"inner join case_projects cp on c.project_id=cp.id " \
              f"where  is_cleared=1 and valid_to between '{valid_to_start}' and '{valid_to_end}'" \
              f" {school_sql} {paper_sql};"
        cases = pd.read_sql(text(sql), self.db.engine_conn).drop_duplicates(subset=['id'])
        return cases

    def query_answers(self, case_ids: list[int]):
        answer_cols = "id, student_id, item_id, case_id, answer, score, created, valid"
        if len(case_ids) == 0:
            return []
        elif len(case_ids) == 1:
            sql = f"select {answer_cols} from answers where case_id={case_ids[0]} and valid=1;"
        else:
            sql = f"select {answer_cols} from answers where case_id in {tuple(case_ids)} and valid=1;"
        answers = pd.read_sql(text(sql), self.db.engine_conn).drop_duplicates(
            subset=['case_id', 'student_id', 'item_id'])
        return answers

    def query_students(self, student_ids: list[int]):
        user_cols = "id, username, first_name, last_name, nickname, gender, role, source, created, " \
                    "unit_id, client_id, extra"
        sql = f"select {user_cols} from users where id in {tuple(student_ids)} and length(id)>=18;"
        students = pd.read_sql(text(sql), self.db.engine_conn).drop_duplicates(subset=['id'])
        return students

    def query_items(self, item_ids: list[int]):
        item_cols = "id, item_text, choices, item_key, item_type, grade, test_type, pattern, " \
                    "`source`, created"
        sql = f"select {item_cols} from items where id in {tuple(item_ids)};"
        return pd.read_sql(text(sql), self.db.engine_conn)

    def query_item_codes(self, item_ids: list[int]):
        item_code_sql = f'select ic.item_id,ic.code,ic.category,c.name ' \
                        f'from item_codes ic left join codebook c on ic.code = c.code ' \
                        f'where ic.item_id in {tuple(item_ids)};'
        item_codes = pd.read_sql(text(item_code_sql), self.db.engine_conn)
        return item_codes

    @property
    def conn(self):
        return self.db.conn
