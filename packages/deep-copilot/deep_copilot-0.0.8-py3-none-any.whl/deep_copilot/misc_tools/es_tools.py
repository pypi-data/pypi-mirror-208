#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 xiaomi.com, Inc. All Rights Reserved
#
# @file     : es.py
# @author   : chengyunlai
# @time     : 2020/09/04 14:27:23
#
from elasticsearch import Elasticsearch


class ElasticSearchUtil:
    """ ElasticSearchUtil """

    def __init__(self, _host):
        self.host = _host if isinstance(_host, (list, tuple)) else [_host]
        self.conn = Elasticsearch(self.host, http_auth=("mi_es_public", "d47e47676d79c6d6"), timeout=120, maxsize=25,
                                  # sniff_on_start=True,    # 连接前测试
                                  # sniff_on_connection_fail=True,  # 节点无响应时刷新节点
                                  # sniffer_timeout=10    # 设置超时时间
                                  )
        # self.conn = Elasticsearch(self.host, http_auth=("xiaomi", "xiaomi"), timeout=120, maxsize=25,
                                  # sniff_on_start=True,    # 连接前测试
                                  # sniff_on_connection_fail=True,  # 节点无响应时刷新节点
                                  # sniffer_timeout=10    # 设置超时时间
                                  # )

    def __del__(self):
        self.close()

    def check(self):
        """
        输出当前系统的ES信息
        :return:
        """
        return self.conn.info()

    def insertDocument(self, index, _type, body, _id=None):
        """
        插入一条数据body到指定的index、指定的type下;可指定Id,若不指定,ES会自动生成
        :param index: 待插入的index值
        :param _type: 待插入的type值
        :param body: 待插入的数据 -> dict型
        :param _id: 自定义Id值
        :return:
        """
        return self.conn.index(index=index, doc_type=_type, body=body, id=_id)

    def insertDataFrame(self, index, _type, data):
        """
        批量插入接口;
        bulk接口所要求的数据列表结构为:[{{optionType}: {Condition}}, {data}]
        其中optionType可为index、delete、update
        Condition可设置每条数据所对应的index值和type值
        data为具体要插入/更新的单条数据
        :param index: 默认插入的index值
        :param _type: 默认插入的type值
        :param data: 待插入数据集
        :return:
        """
        # dataList = dataFrame.to_dict(orient='records')
        # insertHeadInfoList = [{"index": {}} for i in range(len(dataList))]
        # temp = [dict] * (len(dataList) * 2)
        # temp[::2] = insertHeadInfoList
        # temp[1::2] = dataList
        # print "--temp-----",temp
        try:
            return self.conn.bulk(index=index, doc_type=_type, body=data)
        except Exception as e:
            return str(e)

    def deleteDocById(self, index, type, id):
        """
        删除指定index、type、id对应的数据
        :param index:
        :param type:
        :param id:
        :return:
        """
        return self.conn.delete(index=index, doc_type=type, id=id)

    def deleteDocByQuery(self, index, query, type=None):
        """
        删除idnex下符合条件query的所有数据
        :param index:
        :param query: 满足DSL语法格式
        :param type:
        :return:
        """
        return self.conn.delete_by_query(index=index, body=query, doc_type=type)

    def deleteAllDocByIndex(self, index, _type=None):
        """
        删除指定index下的所有数据
        """
        try:
            query = {'query': {'match_all': {}}}
            return self.conn.delete_by_query(index=index, body=query, doc_type=_type)
        except Exception as e:
            return str(e) + ' -> ' + index

    def searchDoc(self, index=None, _type=None, body=None):
        """
        查找index下所有符合条件的数据
        :param index:
        :param _type:
        :param body: 筛选语句,符合DSL语法格式
        :return:
        """
        return self.conn.search(index=index, doc_type=_type, body=body)

    def getDocById(self, index, _type, _id):
        """
        获取指定index、type、id对应的数据
        :param index:
        :param _type:
        :param _id:
        :return:
        """
        return self.conn.get(index=index, doc_type=_type, id=_id)

    def updateDocById(self, index, _type, _id, body=None):
        """
        更新指定index、type、id所对应的数据
        :param index:
        :param _type:
        :param _id:
        :param body: 待更新的值
        :return:
        """
        return self.conn.update(index=index, doc_type=_type, id=_id, body=body)

    def close(self):
        if self.conn is not None:
            try:
                self.conn.close()
            except (Exception,):
                pass
            finally:
                self.conn = None


class ElasticSearchFactory(object):
    repo = {}

    @classmethod
    def get_or_create(cls, _host) -> ElasticSearchUtil:
        try:
            cls.repo[_host]
        except:
            es = ElasticSearchUtil(_host)
            cls.repo[_host] = es
        return cls.repo[_host]
