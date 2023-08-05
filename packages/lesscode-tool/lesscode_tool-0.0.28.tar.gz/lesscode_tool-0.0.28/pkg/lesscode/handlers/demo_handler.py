# -*- coding: utf-8 -*-
from sqlalchemy import NVARCHAR, Column
#from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declarative_base
from lesscode.db.sqlalchemy.sqlalchemy_helper import SqlAlchemyHelper, result_to_json, result_page
from lesscode.web.base_handler import BaseHandler
from lesscode.web.router_mapping import Handler, GetMapping, PostMapping

Base = declarative_base()


class LcAuthUser(Base):
    __tablename__ = "lc_auth_user"
    id = Column(NVARCHAR, primary_key=True)
    username = Column()
    account_status = Column()
    password = Column()
    phone_no = Column()
    display_name = Column()
    create_time = Column()


@Handler("/sqlalchemy")
class SqlAlchemyHandler(BaseHandler):

    @PostMapping("/test")
    def test(self):
        with SqlAlchemyHelper("auth_engine").make_session() as session:
            params = [LcAuthUser.id, LcAuthUser.username, LcAuthUser.phone_no]
            al = session.query(*params).all()
            return result_to_json(al)
