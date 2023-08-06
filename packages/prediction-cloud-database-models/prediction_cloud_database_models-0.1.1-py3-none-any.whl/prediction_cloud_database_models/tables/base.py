from sqlalchemy.ext.declarative import declarative_base

declarative_class_registry = {}
Base = declarative_base(class_registry=declarative_class_registry)
