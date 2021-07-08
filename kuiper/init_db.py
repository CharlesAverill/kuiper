from yaml import load, FullLoader

from .models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
import pathlib


def init_db():
    path = pathlib.Path(os.path.dirname(__file__)).parents[0] / "config.yaml"

    with open(path, "r") as cfg_stream:
        cfg = load(cfg_stream, FullLoader)

    engine = create_engine("sqlite:///" + cfg["db_path"])
    Base.metadata.create_all(engine)

    sess = sessionmaker(engine)

    return sess()
