from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId

class MongoCRUD():
    def __init__(self, location, collection, port = 27017):
        self.client = MongoClient(location, port)
        self.db = self.client[collection]
        
    def insert(self,table,value):
        try:
            collection = self.db[table]
            _id = collection.insert_one(value).inserted_id
            return _id
        except Exception as e:
            return None
        
    def insert_or_update(self,table, idvalue, value, is_objectid = True):
        try:
            _id = self.update_one(table, idvalue, value, is_objectid)
            if _id == None:
                value['_id'] = idvalue
                _id = self.insert(table, value)
            return _id
        except Exception as e:
            print(e)
            return None
    
    def insert_list(self, table, listvalues):
        try:
            if(isinstance(listvalues,dict)):
                return self.insert(table,listvalues)
            collection = self.db[table]
            _ids = collection.insert_many(listvalues).inserted_ids
            return _ids
        except Exception as e:
            return []
    
    def select_one(self, table, query, columns=None):
        try:
            collection = self.db[table]
            if columns:
                values = collection.find_one(query,columns)
            else:
                values = collection.find_one(query)
            return values
        except Exception as e:
            return None
        
    def select_by_id(self, table, id, columns=None, is_objectid=True):
        try:
            collection = self.db[table]
            query = {"_id": ObjectId(id) if is_objectid else id}
            if not columns:
                c = collection.find_one(query)
            else:
                c = collection.find_one(query, columns)
            return c
        except Exception as e:
            return None
        
    def select(self, table, query={}, columns=None, orderby=None, direction = pymongo.DESCENDING, limit=None):
        try:
            collection = self.db[table]
            if not columns:
                c = collection.find(query)
            else:
                c = collection.find(query, columns)
            if orderby:
                c = c.sort(orderby, direction)
            if limit:
                c = c.limit(limit)
            return list(c)
        except Exception as e:
            return None
    
    def update_one(self, table, id, value, is_objectid=True):
        try:
            collection = self.db[table]
            _id = collection.find_one_and_replace({"_id": ObjectId(id) if is_objectid else id}, value)
            return _id
        except Exception as e:
            return None
    
    def delete(self, table, query):
        try:
            collection = self.db[table]
            res = collection.delete_many(query)
            return res.deleted_count
        except Exception as e:
            print(e)
            return None
    
    def delete_by_id(self, table, id, is_objectid=True):
        try:
            collection = self.db[table]
            res = collection.delete_one({"_id": ObjectId(id) if is_objectid else id})
            return res.deleted_count
        except Exception as e:
            print(e)
            return None
        
    def getTables(self):
        try:
            return self.db.list_collection_names()
        except Exception as e:
            return None