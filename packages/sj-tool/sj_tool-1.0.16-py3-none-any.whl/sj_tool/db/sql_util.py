from playhouse.pool import PooledMySQLDatabase


# 定义数据库连接池
def manual_connect(database, user, password, host, port=3306, max_connections=8, stale_timeout=300, **kwargs):
    return PooledMySQLDatabase(
        database,
        user=user,
        password=password,
        host=host,
        port=port,
        max_connections=max_connections,
        stale_timeout=stale_timeout,
        **kwargs
    )


def init_config(database, user, password, host, port=3306):
    return {
        "database": database,
        # "engine": "peewee.MySQLDatabase",
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "charset": "utf8",
    }


# 定义通用增删改查函数
def create_record(db, model_class, **kwargs):
    with db.atomic():
        record = model_class.create(**kwargs)
        return record.id


def update_record(db, model_class, record_id, **kwargs):
    with db.atomic():
        query = model_class.update(**kwargs).where(model_class.id == record_id)
        return query.execute()


def delete_record(db, model_class, record_id):
    with db.atomic():
        query = model_class.delete().where(model_class.id == record_id)
        return query.execute()


def get_records(db, model_class, *select_fields, **where):
    query = model_class.select(*select_fields)
    for key, value in where.items():
        query = query.where(getattr(model_class, key) == value)
    return query
