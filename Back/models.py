from sqlalchemy import Column, Integer, String, Boolean, Numeric, BigInteger, Date, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String, unique=True, nullable=False)
    apps = relationship("App", back_populates="category")


class Developer(Base):
    __tablename__ = "developers"
    developer_id = Column(Integer, primary_key=True, index=True)
    developer_name = Column(String, nullable=False)
    developer_website = Column(String)
    developer_email = Column(String)
    apps = relationship("App", back_populates="developer")


class App(Base):
    __tablename__ = "apps"
    app_id = Column(Integer, primary_key=True, index=True)
    app_name = Column(String, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey(
        "categories.category_id"), nullable=False, index=True)
    rating = Column(Numeric(3, 2), index=True)
    rating_count = Column(Integer)
    installs = Column(BigInteger, index=True)
    minimum_installs = Column(BigInteger)
    maximum_installs = Column(BigInteger)
    is_free = Column(Boolean, nullable=False, index=True)
    price = Column(Numeric(10, 2))
    currency = Column(String(3))
    size = Column(Numeric)
    minimum_android_version = Column(String)
    developer_id = Column(Integer, ForeignKey(
        "developers.developer_id"), nullable=False, index=True)
    released = Column(Date, index=True)
    last_updated = Column(Date, index=True)
    content_rating = Column(String)
    ad_supported = Column(Boolean)
    in_app_purchases = Column(Boolean)
    editors_choice = Column(Boolean)
    scraped_time = Column(TIMESTAMP)

    category = relationship("Category", back_populates="apps")
    developer = relationship("Developer", back_populates="apps")
