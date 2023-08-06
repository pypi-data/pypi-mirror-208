import pymongo
from pymongo import database
from pymongo.results import InsertOneResult, InsertManyResult, UpdateResult, DeleteResult
from typing import List, Dict
from flask_pymongo import PyMongo


class MongoUtil:
    def __init__(self, client: PyMongo = None):
        self.client = client

    def init_client(self, client):
        self.client = client

    def insert_one_doc(self, collection: str, doc: Dict) -> InsertOneResult:
        """
        向 MongoDB 集合中插入一条文档

        Args:
            collection: str类型，代表要插入文档的 MongoDB 集合名字
            doc: 要插入的文档数据，一个 Python 字典对象

        Returns:
            返回 InsertOneResult 对象，代表插入操作的结果
        """
        return self.client.db[collection].insert_one(doc)

    def insert_many_docs(self, collection: str, docs: List[Dict]) -> InsertManyResult:
        """
        向 MongoDB 集合中插入多条文档

        Args:
            collection: str 对象，代表要插入文档的 MongoDB 集合
            docs: 要插入的多个文档数据，一个 Python 字典对象的列表

        Returns:
            返回 results.InsertManyResult 对象，代表插入操作的结果
        """
        return self.client.db[collection].insert_many(docs)

    def find_one_doc(self, collection: str) -> Dict:
        """
        查询 MongoDB 集合中的一条文档

        Args:
            collection: str 对象，代表要查询的 MongoDB 集合

        Returns:
            返回一个 Python 字典对象，代表查询到的 MongoDB 文档数据
        """
        return self.client.db[collection].find_one()

    def find_all_docs(self, collection: str) -> pymongo.cursor.Cursor:
        """
        查询 MongoDB 集合中的所有文档

        Args:
            collection: str 对象，代表要查询的 MongoDB 集合

        Returns:
            返回一个 pymongo.cursor.Cursor 对象，代表查询到的 MongoDB 文档的游标
        """
        return self.client.db[collection].find()

    def find_docs_by_query(self, collection: str, query: Dict) -> pymongo.cursor.Cursor:
        """
        根据查询条件查询 MongoDB 集合中的文档

        Args:
            collection: str 对象，代表要查询的 MongoDB 集合
            query: 查询条件，一个 Python 字典对象，例如 {"age": 30}

        Returns:
            返回一个 pymongo.cursor.Cursor 对象，代表
        """
        return self.client.db[collection].find(query)

    def delete_one_doc(self, collection: str, query: Dict) -> DeleteResult:
        """
        从 MongoDB 集合中删除一条文档

        Args:
            collection: str 对象，代表要删除文档的 MongoDB 集合
            query: 删除条件，一个 Python 字典对象，例如 {"name": "John"}

        Returns:
            返回 DeleteResult 对象，代表删除操作的结果
        """
        return self.client.db[collection].delete_one(query)

    def delete_many_docs(self, collection: str, query: Dict) -> DeleteResult:
        """
        从 MongoDB 集合中删除多条文档

        Args:
            collection: str 对象，代表要删除文档的 MongoDB 集合
            query: 删除条件，一个 Python 字典对象，例如 {"age": {"$gt": 25}}，若为{}，则删除所有文档

        Returns:
            返回 DeleteResult 对象，代表删除操作的结果
        """
        return self.client.db[collection].delete_many(query)

    def update_one_doc(self, collection: str, query: Dict, update: Dict) -> UpdateResult:
        """
        更新 MongoDB 集合中的一条文档

        Args:
            collection: str 对象，代表要更新文档的 MongoDB 集合
            query: 更新条件，一个 Python 字典对象，例如 {"name": "John"}
            update: 要更新的文档数据，一个 Python 字典对象，例如 {"$set": {"age": 25}}

        Returns:
            返回 UpdateResult 对象，代表更新操作的结果
        """
        return self.client.db[collection].update_one(query, update)

    def update_many_docs(self, collection: str, query: Dict, update: Dict) -> UpdateResult:
        """
        更新 MongoDB 集合中的多条文档

        Args:
            collection: str 对象，代表要更新文档的 MongoDB 集合
            query: 更新条件，一个 Python 字典对象，例如 {"age": {"$lt": 30}}
            update: 要更新的文档数据，一个 Python 字典对象，例如 {"$set": {"age": 30}}

        Returns:
            返回 UpdateResult 对象，代表更新操作的结果
        """
        return self.client.db[collection].update_many(query, update)
