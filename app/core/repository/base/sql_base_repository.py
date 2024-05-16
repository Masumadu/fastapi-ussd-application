from typing import Dict, List, Union

import sqlalchemy as sa
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Query

from app.core.database import Base, get_db_session
from app.core.exceptions import AppException
from app.enums import SortResultEnum

from .crud_repository_interface import CRUDRepositoryInterface


class SQLBaseRepository(CRUDRepositoryInterface):
    model: Base

    def __init__(self):
        """
        Base class to be inherited by all repositories. This class comes with
        base crud functionalities attached

        :param model: base model of the class to be used for queries
        """
        self.table = inspect(self.model)

    def index(self, paginate_data: bool = False, page_params: Params = None) -> [Base]:
        """

        :return: {list} returns a list of objects of type model
        """
        with get_db_session() as db_session:
            query = db_session.query(self.model)
            return self._result(
                query=query, paginated=paginate_data, page_params=page_params
            )

    def create(self, obj_in) -> Base:
        """

        :param obj_in: the data you want to use to create the model
        :return: {object} - Returns an instance object of the model passed
        """
        assert obj_in, "Missing data to be saved"

        with get_db_session() as db_session:
            obj_data = dict(obj_in)
            db_obj = self.model(**obj_data)
            db_session.add(db_obj)
            db_session.commit()
            db_session.refresh(db_obj)
        return db_obj

    def update_by_id(self, obj_id, obj_in) -> Base:
        """
        :param obj_id: {int} id of object to update
        :param obj_in: {dict} update data. This data will be used to update
        any object that matches the id specified
        :return: model_object - Returns an instance object of the model passed
        """
        assert obj_id, "Missing id of object to update"
        assert obj_in, "Missing update data"
        assert isinstance(obj_in, dict), "Update data should be a dictionary"

        db_obj = self.find_by_id(obj_id)
        with get_db_session() as db_session:
            for field in obj_in:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, obj_in[field])
            db_session.add(db_obj)
            db_session.commit()
            db_session.refresh(db_obj)
        return db_obj

    def update(self, filter_params, obj_in):
        """
        :param filter_params: {dict}
        :param obj_in: {dict}
        :return: model_object - Returns an instance object of the model passed
        """
        db_obj = self.find(filter_params)
        with get_db_session() as db_session:
            for field in obj_in:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, obj_in[field])
            db_session.add(db_obj)
            db_session.commit()
            db_session.refresh(db_obj)
        return db_obj

    def delete_by_id(self, obj_id):
        """
        :param obj_id:
        :return:
        """

        db_obj = self.find_by_id(obj_id)
        with get_db_session() as db_session:
            db_session.delete(db_obj)
            db_session.commit()
        return True

    def delete(self, filter_params: dict):
        """
        :param filter_params:
        :return:
        """

        db_obj = self.find(filter_params)
        with get_db_session() as db_session:
            db_session.delete(db_obj)
            db_session.commit()
        return True

    def find_by_id(self, obj_id) -> Base:
        """
        returns an object matching the specified id if it exists in the database
        :param obj_id: id of object to query
        :return: model_object - Returns an instance object of the model passed
        """
        assert obj_id, "Missing id of object for querying"

        with get_db_session() as db_session:
            db_obj = db_session.query(self.model).get(obj_id)
            if not db_obj:
                raise AppException.NotFoundException(error_message=None)
        return db_obj

    def find(self, filter_param: dict) -> Base:
        """
        This method returns the first object that matches the query parameters specified
        :param filter_param {dict}. Parameters to be filtered by
        """
        assert filter_param, "Missing filter parameters"
        assert isinstance(
            filter_param, dict
        ), "Filter parameters should be of type dictionary"

        with get_db_session() as db_session:
            db_obj = db_session.query(self.model).filter_by(**filter_param).first()
            if not db_obj:
                raise AppException.NotFoundException(error_message=None)
        return db_obj

    def find_all(
        self,
        filter_param: dict,
        paginate_data: bool = False,
        page_params: Params = None,
    ) -> Base:
        """
        This method returns all objects that matches the query
        parameters specified
        """
        assert isinstance(
            filter_param, dict
        ), "Filter parameters should be of type dictionary"

        with get_db_session() as db_session:
            filter_query = db_session.query(self.model).filter_by(**filter_param)
            return self._result(
                query=filter_query, paginated=paginate_data, page_params=page_params
            )

    def advance_query(
        self,
        keyword: str = None,
        date_filter: dict = None,
        sort_param: dict = None,
        filter_params: dict = None,
        includes: Dict[str, str] = None,
        contains: Dict[str, List[str]] = None,
        columns: List[str] = None,
        paginate_data: bool = False,
        page_params: Params = None,
        many: bool = True,
    ):
        with get_db_session() as db_session:
            if columns:
                result = (
                    db_session.query(self.model)
                    .with_entities(*self._query_columns(attrs=columns))
                    .filter(*self._colum_contain(contains))
                    .filter(*self._colum_includes(includes))
                    .filter(
                        sa.or_(*self._build_keyword_query(keyword=keyword)),
                        sa.or_(*self._build_date_query(date_filter=date_filter or {})),
                    )
                    .filter_by(**filter_params or {})
                    .order_by(self._get_sort_order(sort_param=sort_param or {}))
                )
            else:
                result = (
                    db_session.query(self.model)
                    .filter(
                        sa.or_(*self._build_keyword_query(keyword=keyword)),
                        sa.or_(*self._build_date_query(date_filter=date_filter or {})),
                    )
                    .filter(*self._colum_contain(contains))
                    .filter(*self._colum_includes(includes))
                    .filter_by(**filter_params or {})
                    .order_by(self._get_sort_order(sort_param=sort_param or {}))
                )
            return self._result(
                query=result,
                paginated=paginate_data,
                page_params=page_params,
                many=many,
            )

    def _build_keyword_query(self, keyword: str) -> set:
        search_query = set()
        for column in self.table.columns:
            try:
                if self._is_string_column(column) and keyword:
                    search_query.add(
                        getattr(self.model, column.name).ilike(f"%{keyword}%")
                    )
                elif self._is_enum_column(column) and keyword:
                    search_query.add(
                        getattr(self.model, column.name)
                        .cast(sa.String)
                        .ilike(f"%{keyword}%")
                    )
                elif self._is_jsonb_column(column) and keyword:
                    search_query.add(
                        getattr(self.model, column.name)
                        .cast(sa.String)
                        .ilike(f"%{keyword}%")
                    )
            except AttributeError:
                continue
        return search_query

    # noinspection PyMethodMayBeStatic
    def _is_string_column(self, column):
        return type(column.type) in [sa.String, sa.Text, sa.Column]

    # noinspection PyMethodMayBeStatic
    def _is_enum_column(self, column):
        return type(column.type) in [sa.Enum]

    # noinspection PyMethodMayBeStatic
    def _is_jsonb_column(self, column):
        return type(column.type) in [JSONB]

    def _build_date_query(self, date_filter: dict) -> set:
        query = set()
        if date_filter.get("column"):
            column = self._is_column_available(
                column_name=date_filter.get("column").strip()
            )
            if self._is_date_column(self.table.columns[column]):
                if date_filter.get("min_date") and date_filter.get("max_date"):
                    query.add(
                        getattr(self.model, column).between(
                            date_filter.get("min_date"), date_filter.get("max_date")
                        )
                    )
                    return query
                elif date_filter.get("min_date"):
                    query.add(
                        getattr(self.model, column) >= date_filter.get("min_date")
                    )
                    return query
                elif date_filter.get("max_date"):
                    query.add(
                        getattr(self.model, column) <= date_filter.get("max_date")
                    )
                    return query
                elif date_filter.get("date"):
                    query.add(
                        sa.cast(getattr(self.model, column), sa.Date)
                        == date_filter.get("date")
                    )
                    return query
            else:
                raise AppException.BadRequestException(
                    error_message=f"column {column} not of type date"
                )
        return query

    # noinspection PyMethodMayBeStatic
    def _is_date_column(self, column):
        return type(column.type) in [sa.DateTime, sa.Date]

    def _get_sort_order(self, sort_param: dict):
        if sort_param.get("column") and sort_param.get("order") == SortResultEnum.asc:
            return sa.asc(
                getattr(
                    self.model,
                    self._is_column_available(
                        column_name=sort_param.get("column").strip()
                    ),
                )
            )
        elif (
            sort_param.get("column") and sort_param.get("order") == SortResultEnum.desc
        ):
            return sa.desc(
                getattr(
                    self.model,
                    self._is_column_available(
                        column_name=sort_param.get("column").strip()
                    ),
                )
            )
        return None

    def _is_column_available(self, column_name: str):
        if column_name in self.table.columns.keys():
            return column_name
        raise AppException.BadRequestException(
            error_message=f"column {column_name} does not exist"
        )

    def _colum_contain(self, contains: Union[Dict[str, List[str]], None]) -> Base:
        in_clause = set()
        contains = contains or {}
        for col, value in contains.items():
            in_clause.add(getattr(self.model, col).in_(value))
        return in_clause

    def _colum_includes(self, includes: dict) -> set:
        _includes = set()
        includes = includes or {}
        for col, value in includes.items():
            if self._is_string_column(col):
                _includes.add(getattr(self.model, col.name).ilike(f"%{value}%"))
        return _includes

    def _query_columns(self, attrs: Union[List[str], None]):
        columns = set()
        attrs = attrs or []
        for attr in attrs:
            self._is_column_available(attr)
            columns.add(getattr(self.model, attr))
        return columns

    # noinspection PyMethodMayBeStatic
    def _result(
        self,
        query: Query,
        paginated: bool = False,
        page_params: Params = None,
        many: bool = True,
    ):
        if paginated and page_params:
            return paginate(query, params=page_params)
        if not many:
            db_obj = query.first()
            if not db_obj:
                raise AppException.NotFoundException(error_message=None)
            return db_obj
        return query.all()
