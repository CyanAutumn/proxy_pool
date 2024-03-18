import datetime
import copy
from typing import Optional
from sqlalchemy import Column, String, create_engine, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Proxy(Base):
    """数据库对象"""

    __tablename__ = "proxy"

    ip: Mapped[str] = mapped_column(String, primary_key=True, default=None)
    port: Mapped[str] = mapped_column(String, primary_key=True, default=None)
    location: Mapped[str] = mapped_column(String, default=None)  # 代理地点
    type: Mapped[str] = mapped_column(String, default=None)  # 代理类型
    create_date: Mapped[str] = mapped_column(
        DateTime, default=datetime.datetime.now()
    )  # 创建日期
    last_used_date: Mapped[str] = mapped_column(
        DateTime, default=datetime.datetime.now()
    )  # 最后一次使用的时间
    check_date: Mapped[str] = mapped_column(
        DateTime, default=datetime.datetime.now()
    )  # 最后一次检测的时间，和最后一次使用时间分开是因为最后一次使用时间可能是应用网址，而检测用的可能是与应用网址不同的检测网址
    cookies: Mapped[Optional[str]] = mapped_column(
        String, default=None
    )  # 初次检测所存的cookies
    is_checking: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # 是否正在检查队列中


engine = create_engine("sqlite+pysqlite:///database.sqlite")  # sqlite
Base.metadata.create_all(engine)


def init():
    """初始化表格"""
    with Session(engine) as session:
        session.query(Proxy).update(
            {Proxy.is_checking: False}
        )  # 初始化检测队列指示的标志位
        session.commit()


def check_passed(proxy: Proxy):
    """代理有效的时候调用"""
    with Session(engine) as session:
        cmd = select(Proxy).where(Proxy.ip == proxy.ip, proxy.port == proxy.port)
        data = session.scalars(cmd).all()
        if len(data) > 0:
            data[0].is_checking = False
            data[0].check_date = proxy.check_date
            session.commit()
        else:
            create_ip(proxy)


def delete_proxy(proxy: Proxy):
    """删除代理"""
    with Session(engine) as session:
        cmd = delete(Proxy).where(Proxy.ip == proxy.ip, Proxy.port == proxy.port)
        session.execute(cmd)
        session.commit()


def check_ip_in(proxy: Proxy):
    """代理是否已存在"""
    with Session(engine) as session:
        cmd = select(Proxy).where(Proxy.ip == proxy.ip, proxy.port == proxy.port)
        data = session.scalars(cmd).all()
        if len(data) > 0:
            return True
        return False


def create_ip(proxy: Proxy):
    """将代理存放入库"""
    with Session(engine) as session:
        session.add(proxy)
        session.commit()


def get_expired_ip_list():
    """获取一定时间未检测的代理"""
    with Session(engine) as session:
        cmd = select(Proxy).where(
            Proxy.check_date < datetime.datetime.now() - datetime.timedelta(seconds=60),
            Proxy.is_checking == False,
        )
        data_list = session.scalars(cmd).all()
        if len(data_list) > 0:
            for data in data_list:
                data.is_checking = True
            session.commit()
            cmd = select(Proxy).where(Proxy.is_checking == True)
            _ = session.scalars(cmd).all()
            return copy.deepcopy(_)
        else:
            return None


def get_proxy(num: int):
    with Session(engine) as session:
        users = (
            session.query(Proxy)
            .where(
                Proxy.check_date
                < datetime.datetime.now() + datetime.timedelta(seconds=60),
                Proxy.is_checking == False,
            )
            .order_by(func.random())
            .limit(num)
            .all()
        )
        return users
