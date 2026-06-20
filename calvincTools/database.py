from typing import List, Dict, Any

##########################################################
###################    REPOSITORIES    ###################
##########################################################

from sqlalchemy import (
    select, insert, update, delete, 
    )   # pylint: disable=unused-import
from sqlalchemy.exc import SQLAlchemyError
from typing import Generic, Sequence, TypeVar, Type     # pylint: disable=unused-import

T = TypeVar("T")  # entity type

class Repository(Generic[T]):
    def __init__(self, session_factory, model: Type[T]):
        self._session_factory = session_factory
        self._model = model
    # __init__

    def get_all(
        self,
        whereclause=None,
        order_by=None
    ) -> list[T]:    # | list[tuple]:
        """
        Retrieve records with optional fields, filter, and ordering.

        :param fields: list/tuple of columns or ORM attributes (default: whole model)
            # fields is deprecated - get_all needs to always return an ORM instance - have the caller build a dict instead
        :param whereclause: SQLAlchemy expression for filtering
        :param order_by: column(s) or ORM attributes for ordering
        """

        # Build select
        stmt = select(self._model)

        if whereclause is not None:
            stmt = stmt.where(whereclause)

        if order_by is not None:
            if isinstance(order_by, (list, tuple)):
                stmt = stmt.order_by(*order_by)
            else:
                stmt = stmt.order_by(order_by)

        with self._session_factory() as session:
            rs = session.execute(stmt)

            # Full model objects
            results = rs.scalars().all()
            for row in results:
                session.expunge(row)

        return results
    # get_all
    
    def get_by_id(self, id_: int, newifnotfound: bool = False) -> T | None:
        with self._session_factory() as session:
            obj = session.get(self._model, id_)
            if obj:
                session.expunge(obj)
            elif newifnotfound:
                obj = self._model(id=id_) # type: ignore
            return obj
    # get_by_id

    def add(self, entity: T) -> T:
        with self._session_factory() as session:
            session.add(entity)
            session.commit()
            session.refresh(entity)
            session.expunge(entity)
        return entity
    # add
    def bulk_add_from_listofdict(self, entities: List[Dict]) -> Any:
        """
        Bulk insert from a list of dictionaries.
        """
        retval = None
        with self._session_factory() as session:
            # Execute the bulk insert
            try:
                session.execute(insert(self._model), entities)
                session.commit()
                retval = True
            except SQLAlchemyError as e:
                session.rollback()
                retval = ('database', e)
            except Exception as e:
                session.rollback()
                retval = ('other', e)
        return retval
    #addmultiple ??

    def remove(self, entity: T) -> None:
        with self._session_factory() as session:
            obj = session.merge(entity)  # reattach if detached
            session.delete(obj)
            session.commit()
        # endwith
    # remove
    def removewhere(self, whereclause) -> int:
        with self._session_factory() as session:
            stmt = delete(self._model).where(whereclause)
            rs = session.execute(stmt)
            deleted_count = rs.rowcount    # Get the count of affected rows
            session.commit()
        # endwith
        return deleted_count
        # endwith
    # removewhere

    def update(self, entity: T) -> T:
        with self._session_factory() as session:
            obj = session.merge(entity)  # reattach if detached
            session.commit()
            session.expunge(obj)
        return obj
    # update
    def updatewhere(self, whereclause, values: dict) -> int:
        with self._session_factory() as session:
            stmt = update(self._model) \
                .where(whereclause) \
                .values(**values)
            rs = session.execute(stmt)
            updated_count = rs.rowcount    # Get the count of affected rows
            session.commit()
        # endwith
        return updated_count
    #updatewhere
    
# Repository
    def end_of_class(self):
        pass
