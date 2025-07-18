import pytest

from base.client_v2_base import TestMilvusClientV2Base
from utils.util_log import test_log as log
from common import common_func as cf
from common import common_type as ct
from common.common_type import CaseLabel, CheckTasks
from utils.util_pymilvus import *

prefix = "client_insert"
epsilon = ct.epsilon
default_nb = ct.default_nb
default_nb_medium = ct.default_nb_medium
default_nq = ct.default_nq
default_dim = ct.default_dim
default_limit = ct.default_limit
default_search_exp = "id >= 0"
exp_res = "exp_res"
default_search_string_exp = "varchar >= \"0\""
default_search_mix_exp = "int64 >= 0 && varchar >= \"0\""
default_invaild_string_exp = "varchar >= 0"
default_json_search_exp = "json_field[\"number\"] >= 0"
perfix_expr = 'varchar like "0%"'
default_search_field = ct.default_float_vec_field_name
default_search_params = ct.default_search_params
default_primary_key_field_name = "id"
default_vector_field_name = "vector"
default_dynamic_field_name = "field_new"
default_float_field_name = ct.default_float_field_name
default_bool_field_name = ct.default_bool_field_name
default_string_field_name = ct.default_string_field_name
default_int32_array_field_name = ct.default_int32_array_field_name
default_string_array_field_name = ct.default_string_array_field_name


class TestMilvusClientInsertInvalid(TestMilvusClientV2Base):
    """ Test case of search interface """

    @pytest.fixture(scope="function", params=[False, True])
    def auto_id(self, request):
        yield request.param

    @pytest.fixture(scope="function", params=["COSINE", "L2"])
    def metric_type(self, request):
        yield request.param

    """
    ******************************************************************
    #  The following are invalid base cases
    ******************************************************************
    """

    @pytest.mark.tags(CaseLabel.L1)
    @pytest.mark.skip(reason="pymilvus issue 1883")
    def test_milvus_client_insert_column_data(self):
        """
        target: test insert column data
        method: create connection, collection, insert and search
        expected: raise error
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim)
        # 2. insert
        vectors = [[random.random() for _ in range(default_dim)] for _ in range(default_nb)]
        data = [[i for i in range(default_nb)], vectors]
        error = {ct.err_code: 1, ct.err_msg: "Unexpected error, message=<'list' object has no attribute 'items'"}
        self.insert(client, collection_name, data,
                    check_task=CheckTasks.err_res, check_items=error)
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_insert_empty_collection_name(self):
        """
        target: test high level api: client.create_collection
        method: create collection with invalid primary field
        expected: Raise exception
        """
        client = self._client()
        collection_name = ""
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 1, ct.err_msg: f"`collection_name` value {collection_name} is illegal"}
        self.insert(client, collection_name, rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    @pytest.mark.parametrize("collection_name", ["12-s", "12 s", "(mn)", "中文", "%$#"])
    def test_milvus_client_insert_invalid_collection_name(self, collection_name):
        """
        target: test high level api: client.create_collection
        method: create collection with invalid primary field
        expected: Raise exception
        """
        client = self._client()
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 1100, ct.err_msg: f"Invalid collection name: {collection_name}. the first character of a "
                                                f"collection name must be an underscore or letter: invalid parameter"}
        self.insert(client, collection_name, rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_insert_collection_name_over_max_length(self):
        """
        target: test high level api: client.create_collection
        method: create collection with invalid primary field
        expected: Raise exception
        """
        client = self._client()
        collection_name = "a".join("a" for i in range(256))
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 1100, ct.err_msg: f"the length of a collection name must be less than 255 characters"}
        self.insert(client, collection_name, rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_insert_not_exist_collection_name(self):
        """
        target: test high level api: client.create_collection
        method: create collection with invalid primary field
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str("insert_not_exist")
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 100, ct.err_msg: f"can't find collection[database=default][collection={collection_name}]"}
        self.insert(client, collection_name, rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L2)
    @pytest.mark.parametrize("data", ["12-s", "12 s", "(mn)", "中文", "%$#", " ", ""])
    def test_milvus_client_insert_data_invalid_type(self, data):
        """
        target: test high level api: client.create_collection
        method: create collection with invalid primary field
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        # 2. insert
        error = {ct.err_code: 999,
                 ct.err_msg: "wrong type of argument 'data',expected 'Dict' or list of 'Dict', got 'str'"}
        self.insert(client, collection_name, data,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_insert_data_vector_field_missing(self):
        """
        target: test high level api: client.create_collection
        method: create collection with invalid primary field
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i,
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 1,
                 ct.err_msg: f"Insert missed an field `vector` to collection "
                             f"without set nullable==true or set default_value"}
        self.insert(client, collection_name, data=rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_insert_data_id_field_missing(self):
        """
        target: test high level api: client.create_collection
        method: create collection with invalid primary field
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 1,
                 ct.err_msg: f"Insert missed an field `id` to collection without set nullable==true or set default_value"}
        self.insert(client, collection_name, data=rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_insert_data_extra_field(self):
        """
        target: test milvus client: insert extra field than schema
        method: insert extra field than schema when enable_dynamic_field is False
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, enable_dynamic_field=False)
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 1,
                 ct.err_msg: f"Attempt to insert an unexpected field `float` to collection without enabling dynamic field"}
        self.insert(client, collection_name, data=rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_insert_data_dim_not_match(self):
        """
        target: test milvus client: insert extra field than schema
        method: insert extra field than schema when enable_dynamic_field is False
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim)
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [
            {default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim + 1))[0]),
             default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 65536, ct.err_msg: f"of float data should divide the dim({default_dim})"}
        self.insert(client, collection_name, data=rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_insert_not_matched_data(self):
        """
        target: test milvus client: insert not matched data then defined
        method: insert string to int primary field
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim)
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [
            {default_primary_key_field_name: str(i), default_vector_field_name: list(rng.random((1, default_dim))[0]),
             default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 1,
                 ct.err_msg: f"The Input data type is inconsistent with defined schema, "
                             f"{{id}} field should be a int64"}
        self.insert(client, collection_name, data=rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    @pytest.mark.parametrize("partition_name", ["12 s", "(mn)", "中文", "%$#", " "])
    def test_milvus_client_insert_invalid_partition_name(self, partition_name):
        """
        target: test milvus client: insert extra field than schema
        method: insert extra field than schema when enable_dynamic_field is False
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim)
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 65535, ct.err_msg: f"Invalid partition name: {partition_name}."}
        if partition_name == " ":
            error = {ct.err_code: 1, ct.err_msg: f"Invalid partition name: . Partition name should not be empty."}
        self.insert(client, collection_name, data=rows, partition_name=partition_name,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_insert_not_exist_partition_name(self):
        """
        target: test milvus client: insert extra field than schema
        method: insert extra field than schema when enable_dynamic_field is False
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim)
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        partition_name = cf.gen_unique_str("partition_not_exist")
        error = {ct.err_code: 200, ct.err_msg: f"partition not found[partition={partition_name}]"}
        self.insert(client, collection_name, data=rows, partition_name=partition_name,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L2)
    def test_milvus_client_insert_collection_partition_not_match(self):
        """
        target: test milvus client: insert extra field than schema
        method: insert extra field than schema when enable_dynamic_field is False
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        another_collection_name = cf.gen_unique_str(prefix + "another")
        partition_name = cf.gen_unique_str("partition")
        # 1. create collection
        self.create_collection(client, collection_name, default_dim)
        self.create_collection(client, another_collection_name, default_dim)
        self.create_partition(client, another_collection_name, partition_name)
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 200, ct.err_msg: f"partition not found[partition={partition_name}]"}
        self.insert(client, collection_name, data=rows, partition_name=partition_name,
                    check_task=CheckTasks.err_res, check_items=error)


class TestMilvusClientInsertValid(TestMilvusClientV2Base):
    """ Test case of search interface """

    @pytest.fixture(scope="function", params=[False, True])
    def auto_id(self, request):
        yield request.param

    @pytest.fixture(scope="function", params=["COSINE", "L2"])
    def metric_type(self, request):
        yield request.param

    @pytest.fixture(scope="function", params=[True, False])
    def nullable(self, request):
        yield request.param

    @pytest.fixture(scope="function", params=[DataType.FLOAT_VECTOR, DataType.FLOAT16_VECTOR,
                                              DataType.BFLOAT16_VECTOR, DataType.INT8_VECTOR])
    def vector_type(self, request):
        yield request.param

    """
    ******************************************************************
    #  The following are valid base cases
    ******************************************************************
    """

    @pytest.mark.tags(CaseLabel.L0)
    def test_milvus_client_insert_default(self, vector_type, nullable):
        """
        target: test search (high level api) normal case
        method: create connection, collection, insert and search
        expected: search/query successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        dim = 8
        # 1. create collection
        schema = self.create_schema(client, enable_dynamic_field=False)[0]
        schema.add_field(default_primary_key_field_name, DataType.INT64, max_length=64, is_primary=True, auto_id=False)
        schema.add_field(default_vector_field_name, vector_type, dim=dim)
        schema.add_field(default_string_field_name, DataType.VARCHAR, max_length=64, is_partition_key=True)
        schema.add_field(default_float_field_name, DataType.FLOAT, nullable=nullable)
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(default_vector_field_name, metric_type="COSINE")
        self.create_collection(client, collection_name, dimension=dim, schema=schema, index_params=index_params)
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        vectors = cf.gen_vectors(default_nb, dim, vector_data_type=vector_type)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: vectors[i],
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        results = self.insert(client, collection_name, rows)[0]
        assert results['insert_count'] == default_nb
        # 3. search
        vectors_to_search = [vectors[0]]
        insert_ids = [i for i in range(default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit,
                                 "pk_name": default_primary_key_field_name})
        # 4. query
        self.query(client, collection_name, filter=default_search_exp,
                   check_task=CheckTasks.check_query_results,
                   check_items={exp_res: rows,
                                "with_vec": True,
                                "pk_name": default_primary_key_field_name,
                                "vector_type": vector_type})
        self.release_collection(client, collection_name)
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L2)
    def test_milvus_client_insert_different_fields(self):
        """
        target: test search (high level api) normal case
        method: create connection, collection, insert and search
        expected: search/query successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        collections = self.list_collections(client)[0]
        assert collection_name in collections
        self.describe_collection(client, collection_name,
                                 check_task=CheckTasks.check_describe_collection_property,
                                 check_items={"collection_name": collection_name,
                                              "dim": default_dim,
                                              "consistency_level": 0})
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        results = self.insert(client, collection_name, rows)[0]
        assert results['insert_count'] == default_nb
        # 3. insert diff fields
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, "new_diff_str_field": str(i)} for i in range(default_nb)]
        results = self.insert(client, collection_name, rows)[0]
        assert results['insert_count'] == default_nb
        # 3. search
        vectors_to_search = rng.random((1, default_dim))
        insert_ids = [i for i in range(default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit,
                                 "pk_name": default_primary_key_field_name})
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L2)
    def test_milvus_client_insert_empty_data(self):
        """
        target: test search (high level api) normal case
        method: create connection, collection, insert and search
        expected: search/query successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        # 2. insert
        rows = []
        results = self.insert(client, collection_name, rows)[0]
        assert results['insert_count'] == 0
        # 3. search
        rng = np.random.default_rng(seed=19530)
        vectors_to_search = rng.random((1, default_dim))
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": [],
                                 "pk_name": default_primary_key_field_name,
                                 "limit": 0})
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_insert_partition(self):
        """
        target: test fast create collection normal case
        method: create collection
        expected: create collection with default schema, index, and load successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        partition_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        # 2. create partition
        self.create_partition(client, collection_name, partition_name)
        partitions = self.list_partitions(client, collection_name)[0]
        assert partition_name in partitions
        index = self.list_indexes(client, collection_name)[0]
        assert index == ['vector']
        # load_state = self.get_load_state(collection_name)[0]
        # 3. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        results = self.insert(client, collection_name, rows, partition_name=partition_name)[0]
        assert results['insert_count'] == default_nb
        # 3. search
        vectors_to_search = rng.random((1, default_dim))
        insert_ids = [i for i in range(default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit,
                                 "pk_name": default_primary_key_field_name})
        # partition_number = self.get_partition_stats(client, collection_name, "_default")[0]
        # assert partition_number == default_nb
        # partition_number = self.get_partition_stats(client, collection_name, partition_name)[0]
        # assert partition_number[0]['value'] == 0
        if self.has_partition(client, collection_name, partition_name)[0]:
            self.release_partitions(client, collection_name, partition_name)
            self.drop_partition(client, collection_name, partition_name)
        if self.has_collection(client, collection_name)[0]:
            self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L2)
    @pytest.mark.parametrize("default_value", ["a" * 64, "aa"])
    def test_milvus_client_insert_with_added_field(self, default_value):
        """
        target: test search (high level api) normal case
        method: create connection, collection, insert, add field, insert and search
        expected: search/query successfully
        """
        client = self._client()
        collection_name = cf.gen_collection_name_by_testcase_name()
        dim = 8
        # 1. create collection
        schema = self.create_schema(client, enable_dynamic_field=False)[0]
        schema.add_field(default_primary_key_field_name, DataType.INT64, max_length=64, is_primary=True, auto_id=False)
        schema.add_field(default_vector_field_name, DataType.FLOAT_VECTOR, dim=dim)
        schema.add_field(default_string_field_name, DataType.VARCHAR, max_length=64, is_partition_key=True)
        schema.add_field(default_float_field_name, DataType.FLOAT, nullable=True)
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(default_vector_field_name, metric_type="COSINE")
        self.create_collection(client, collection_name, dimension=dim, schema=schema, index_params=index_params)
        # 2. insert before add field
        vectors = cf.gen_vectors(default_nb * 2, dim, vector_data_type=DataType.FLOAT_VECTOR)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: vectors[i],
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        results = self.insert(client, collection_name, rows)[0]
        assert results['insert_count'] == default_nb
        # 3. add new field
        self.add_collection_field(client, collection_name, field_name="field_new", data_type=DataType.VARCHAR,
                                  nullable=True, default_value=default_value, max_length=64)
        vectors_to_search = [vectors[0]]
        insert_ids = [i for i in range(default_nb)]
        # 4. check old dynamic data search is not impacted after add new field
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "pk_name": default_primary_key_field_name,
                                 "limit": default_limit})
        # 5. insert data(old + new field)
        rows_t = [{default_primary_key_field_name: i, default_vector_field_name: vectors[i],
                  default_float_field_name: i * 1.0, default_string_field_name: str(i),
                  "field_new": "field_new"} for i in range(default_nb, default_nb * 2)]
        results = self.insert(client, collection_name, rows_t)[0]
        assert results['insert_count'] == default_nb
        insert_ids_after_add_field = [i for i in range(default_nb, default_nb * 2)]
        # 6. search filtered with the new field
        self.search(client, collection_name, vectors_to_search,
                    filter=f'field_new=="{default_value}"',
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "pk_name": default_primary_key_field_name,
                                 "limit": default_limit})
        self.search(client, collection_name, vectors_to_search,
                    filter=f"field_new=='field_new'",
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids_after_add_field,
                                 "pk_name": default_primary_key_field_name,
                                 "limit": default_limit})
        self.release_collection(client, collection_name)
        self.drop_collection(client, collection_name)


class TestMilvusClientUpsertInvalid(TestMilvusClientV2Base):
    """ Test case of search interface """

    @pytest.fixture(scope="function", params=[False, True])
    def auto_id(self, request):
        yield request.param

    @pytest.fixture(scope="function", params=["COSINE", "L2"])
    def metric_type(self, request):
        yield request.param

    """
    ******************************************************************
    #  The following are invalid base cases
    ******************************************************************
    """

    @pytest.mark.tags(CaseLabel.L1)
    @pytest.mark.skip(reason="pymilvus issue 1883")
    def test_milvus_client_upsert_column_data(self):
        """
        target: test insert column data
        method: create connection, collection, insert and search
        expected: raise error
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim)
        # 2. insert
        vectors = [[random.random() for _ in range(default_dim)] for _ in range(default_nb)]
        data = [[i for i in range(default_nb)], vectors]
        error = {ct.err_code: 1, ct.err_msg: "Unexpected error, message=<'list' object has no attribute 'items'"}
        self.upsert(client, collection_name, data,
                    check_task=CheckTasks.err_res, check_items=error)
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_upsert_empty_collection_name(self):
        """
        target: test high level api: client.create_collection
        method: create collection with invalid primary field
        expected: Raise exception
        """
        client = self._client()
        collection_name = ""
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 1, ct.err_msg: f"`collection_name` value {collection_name} is illegal"}
        self.upsert(client, collection_name, rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    @pytest.mark.parametrize("collection_name", ["12-s", "12 s", "(mn)", "中文", "%$#"])
    def test_milvus_client_upsert_invalid_collection_name(self, collection_name):
        """
        target: test high level api: client.create_collection
        method: create collection with invalid primary field
        expected: Raise exception
        """
        client = self._client()
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 1100, ct.err_msg: f"Invalid collection name: {collection_name}. the first character of a "
                                                f"collection name must be an underscore or letter: invalid parameter"}
        self.upsert(client, collection_name, rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_upsert_collection_name_over_max_length(self):
        """
        target: test high level api: client.create_collection
        method: create collection with invalid primary field
        expected: Raise exception
        """
        client = self._client()
        collection_name = "a".join("a" for i in range(256))
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 1100, ct.err_msg: f"the length of a collection name must be less than 255 characters"}
        self.upsert(client, collection_name, rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_upsert_not_exist_collection_name(self):
        """
        target: test high level api: client.create_collection
        method: create collection with invalid primary field
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str("insert_not_exist")
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 100, ct.err_msg: f"can't find collection[database=default][collection={collection_name}]"}
        self.upsert(client, collection_name, rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    @pytest.mark.parametrize("data", ["12-s", "12 s", "(mn)", "中文", "%$#", " "])
    def test_milvus_client_upsert_data_invalid_type(self, data):
        """
        target: test high level api: client.create_collection
        method: create collection with invalid primary field
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        # 2. insert
        error = {ct.err_code: 1, ct.err_msg: f"wrong type of argument 'data',expected 'Dict' or list of 'Dict'"}
        self.upsert(client, collection_name, data,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_upsert_data_empty(self):
        """
        target: test high level api: client.create_collection
        method: create collection with invalid primary field
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        # 2. insert
        error = {ct.err_code: 1, ct.err_msg: f"wrong type of argument 'data',expected 'Dict' or list of 'Dict'"}
        self.upsert(client, collection_name, data="",
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_upsert_data_vector_field_missing(self):
        """
        target: test high level api: client.create_collection
        method: create collection with invalid primary field
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i,
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(10)]
        error = {ct.err_code: 1,
                 ct.err_msg: "Insert missed an field `vector` to collection without set nullable==true or set default_value"}
        self.upsert(client, collection_name, data=rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_upsert_data_id_field_missing(self):
        """
        target: test high level api: client.create_collection
        method: create collection with invalid primary field
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(20)]
        error = {ct.err_code: 1,
                 ct.err_msg: f"Insert missed an field `id` to collection without set nullable==true or set default_value"}
        self.upsert(client, collection_name, data=rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_upsert_data_extra_field(self):
        """
        target: test milvus client: insert extra field than schema
        method: insert extra field than schema when enable_dynamic_field is False
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        dim = 32
        self.create_collection(client, collection_name, dim, enable_dynamic_field=False)
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(10)]
        error = {ct.err_code: 1,
                 ct.err_msg: f"Attempt to insert an unexpected field `float` to collection without enabling dynamic field"}
        self.upsert(client, collection_name, data=rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_upsert_data_dim_not_match(self):
        """
        target: test milvus client: insert extra field than schema
        method: insert extra field than schema when enable_dynamic_field is False
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim)
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [
            {default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim + 1))[0]),
             default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 65536, ct.err_msg: f"of float data should divide the dim({default_dim})"}
        self.upsert(client, collection_name, data=rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_upsert_not_matched_data(self):
        """
        target: test milvus client: insert not matched data then defined
        method: insert string to int primary field
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim)
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [
            {default_primary_key_field_name: str(i), default_vector_field_name: list(rng.random((1, default_dim))[0]),
             default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 1,
                 ct.err_msg: "The Input data type is inconsistent with defined schema, {id} field should be a int64"}
        self.upsert(client, collection_name, data=rows,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    @pytest.mark.parametrize("partition_name", ["12 s", "(mn)", "中文", "%$#", " "])
    def test_milvus_client_upsert_invalid_partition_name(self, partition_name):
        """
        target: test milvus client: insert extra field than schema
        method: insert extra field than schema when enable_dynamic_field is False
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim)
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 65535, ct.err_msg: f"Invalid partition name: {partition_name}"}
        if partition_name == " ":
            error = {ct.err_code: 1, ct.err_msg: f"Invalid partition name: . Partition name should not be empty."}
        self.upsert(client, collection_name, data=rows, partition_name=partition_name,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_upsert_not_exist_partition_name(self):
        """
        target: test milvus client: insert extra field than schema
        method: insert extra field than schema when enable_dynamic_field is False
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim)
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        partition_name = cf.gen_unique_str("partition_not_exist")
        error = {ct.err_code: 200, ct.err_msg: f"partition not found[partition={partition_name}]"}
        self.upsert(client, collection_name, data=rows, partition_name=partition_name,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L2)
    def test_milvus_client_upsert_collection_partition_not_match(self):
        """
        target: test milvus client: insert extra field than schema
        method: insert extra field than schema when enable_dynamic_field is False
        expected: Raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        another_collection_name = cf.gen_unique_str(prefix + "another")
        partition_name = cf.gen_unique_str("partition")
        # 1. create collection
        self.create_collection(client, collection_name, default_dim)
        self.create_collection(client, another_collection_name, default_dim)
        self.create_partition(client, another_collection_name, partition_name)
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        error = {ct.err_code: 200, ct.err_msg: f"partition not found[partition={partition_name}]"}
        self.upsert(client, collection_name, data=rows, partition_name=partition_name,
                    check_task=CheckTasks.err_res, check_items=error)

    @pytest.mark.tags(CaseLabel.L1)
    @pytest.mark.parametrize("nullable", [True, False])
    def test_milvus_client_insert_array_element_null(self, nullable):
        """
        target: test search with null expression on each key of json
        method: create connection, collection, insert and search
        expected: raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        dim = 5
        # 1. create collection
        nullable_field_name = "nullable_field"
        schema = self.create_schema(client, enable_dynamic_field=False)[0]
        schema.add_field(default_primary_key_field_name, DataType.VARCHAR, max_length=64, is_primary=True,
                         auto_id=False)
        schema.add_field(default_vector_field_name, DataType.FLOAT_VECTOR, dim=dim)
        schema.add_field(nullable_field_name, DataType.ARRAY, element_type=DataType.INT64, max_capacity=12,
                         max_length=64, nullable=nullable)
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(default_vector_field_name, metric_type="COSINE")
        self.create_collection(client, collection_name, dimension=dim, schema=schema, index_params=index_params)
        # 2. insert
        vectors = cf.gen_vectors(default_nb, dim)
        rows = [{default_primary_key_field_name: str(i), default_vector_field_name: vectors[i],
                 nullable_field_name: [None, 2, 3]} for i in range(default_nb)]
        error = {ct.err_code: 1,
                 ct.err_msg: "The Input data type is inconsistent with defined schema, {nullable_field} field "
                             "should be a array, but got a {<class 'list'>} instead."}
        self.insert(client, collection_name, rows,
                    check_task=CheckTasks.err_res,
                    check_items=error)


class TestMilvusClientUpsertValid(TestMilvusClientV2Base):
    """ Test case of search interface """

    @pytest.fixture(scope="function", params=[False, True])
    def auto_id(self, request):
        yield request.param

    @pytest.fixture(scope="function", params=["COSINE", "L2"])
    def metric_type(self, request):
        yield request.param

    """
    ******************************************************************
    #  The following are valid base cases
    ******************************************************************
    """

    @pytest.mark.tags(CaseLabel.L0)
    def test_milvus_client_upsert_default(self):
        """
        target: test search (high level api) normal case
        method: create connection, collection, insert and search
        expected: search/query successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        collections = self.list_collections(client)[0]
        assert collection_name in collections
        self.describe_collection(client, collection_name,
                                 check_task=CheckTasks.check_describe_collection_property,
                                 check_items={"collection_name": collection_name,
                                              "dim": default_dim,
                                              "consistency_level": 0})
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        results = self.upsert(client, collection_name, rows)[0]
        assert results['upsert_count'] == default_nb
        # 3. search
        vectors_to_search = rng.random((1, default_dim))
        insert_ids = [i for i in range(default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit,
                                 "pk_name": default_primary_key_field_name})
        # 4. query
        self.query(client, collection_name, filter=default_search_exp,
                   check_task=CheckTasks.check_query_results,
                   check_items={exp_res: rows,
                                "with_vec": True,
                                "pk_name": default_primary_key_field_name})
        self.release_collection(client, collection_name)
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L2)
    def test_milvus_client_upsert_empty_data(self):
        """
        target: test search (high level api) normal case
        method: create connection, collection, insert and search
        expected: search/query successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        # 2. insert
        rows = []
        results = self.upsert(client, collection_name, rows)[0]
        assert results['upsert_count'] == 0
        # 3. search
        rng = np.random.default_rng(seed=19530)
        vectors_to_search = rng.random((1, default_dim))
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": [],
                                 "pk_name": default_primary_key_field_name,
                                 "limit": 0})
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L2)
    def test_milvus_client_upsert_partition(self):
        """
        target: test fast create collection normal case
        method: create collection
        expected: create collection with default schema, index, and load successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        partition_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        # 2. create partition
        self.create_partition(client, collection_name, partition_name)
        partitions = self.list_partitions(client, collection_name)[0]
        assert partition_name in partitions
        index = self.list_indexes(client, collection_name)[0]
        assert index == ['vector']
        # load_state = self.get_load_state(collection_name)[0]
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        # 3. upsert to default partition
        results = self.upsert(client, collection_name, rows, partition_name=partitions[0])[0]
        assert results['upsert_count'] == default_nb
        # 4. upsert to non-default partition
        results = self.upsert(client, collection_name, rows, partition_name=partition_name)[0]
        assert results['upsert_count'] == default_nb
        # 5. search
        vectors_to_search = rng.random((1, default_dim))
        insert_ids = [i for i in range(default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit,
                                 "pk_name": default_primary_key_field_name})
        # partition_number = self.get_partition_stats(client, collection_name, "_default")[0]
        # assert partition_number == default_nb
        # partition_number = self.get_partition_stats(client, collection_name, partition_name)[0]
        # assert partition_number[0]['value'] == 0
        if self.has_partition(client, collection_name, partition_name)[0]:
            self.release_partitions(client, collection_name, partition_name)
            self.drop_partition(client, collection_name, partition_name)
        if self.has_collection(client, collection_name)[0]:
            self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_insert_upsert(self):
        """
        target: test fast create collection normal case
        method: create collection
        expected: create collection with default schema, index, and load successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        partition_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        # 2. create partition
        self.create_partition(client, collection_name, partition_name)
        partitions = self.list_partitions(client, collection_name)[0]
        assert partition_name in partitions
        index = self.list_indexes(client, collection_name)[0]
        assert index == ['vector']
        # load_state = self.get_load_state(collection_name)[0]
        # 3. insert and upsert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        results = self.insert(client, collection_name, rows, partition_name=partition_name)[0]
        assert results['insert_count'] == default_nb
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, "new_diff_str_field": str(i)} for i in range(default_nb)]
        results = self.upsert(client, collection_name, rows, partition_name=partition_name)[0]
        assert results['upsert_count'] == default_nb
        # 3. search
        vectors_to_search = rng.random((1, default_dim))
        insert_ids = [i for i in range(default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit,
                                 "pk_name": default_primary_key_field_name})
        if self.has_partition(client, collection_name, partition_name)[0]:
            self.release_partitions(client, collection_name, partition_name)
            self.drop_partition(client, collection_name, partition_name)
        if self.has_collection(client, collection_name)[0]:
            self.drop_collection(client, collection_name)


class TestMilvusClientInsertJsonPathIndexValid(TestMilvusClientV2Base):
    """ Test case of insert interface """

    @pytest.fixture(scope="function", params=["INVERTED"])
    def supported_varchar_scalar_index(self, request):
        yield request.param

    @pytest.fixture(scope="function", params=["BOOL", "Double", "Varchar", "json"])
    def supported_json_cast_type(self, request):
        yield request.param

    """
    ******************************************************************
    #  The following are valid base cases
    ******************************************************************
    """

    @pytest.mark.tags(CaseLabel.L1)
    @pytest.mark.parametrize("enable_dynamic_field", [True, False])
    def test_milvus_client_insert_before_json_path_index(self, enable_dynamic_field, supported_json_cast_type,
                                                         supported_varchar_scalar_index):
        """
        target: test insert and then create json path index
        method: create json path index after insert
        steps: 1. create schema
               2. create collection
               3. insert
               4. prepare json path index params with parameter "json_cast_type" and "json_path"
               5. create index
        expected: insert and create json path index successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        json_field_name = "my_json"
        schema = self.create_schema(client, enable_dynamic_field=enable_dynamic_field)[0]
        schema.add_field(default_primary_key_field_name, DataType.INT64, is_primary=True, auto_id=False)
        schema.add_field(default_vector_field_name, DataType.FLOAT_VECTOR, dim=default_dim)
        schema.add_field(default_string_field_name, DataType.VARCHAR, max_length=64)
        if not enable_dynamic_field:
            schema.add_field(json_field_name, DataType.JSON)
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(default_vector_field_name, metric_type="COSINE")
        self.create_collection(client, collection_name, schema=schema, index_params=index_params)
        # 2. insert with different data distribution
        vectors = cf.gen_vectors(default_nb+50, default_dim)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: vectors[i],
                 default_string_field_name: str(i), json_field_name: {'a': {"b": i}}} for i in
                range(default_nb)]
        self.insert(client, collection_name, rows)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: vectors[i],
                 default_string_field_name: str(i), json_field_name: i} for i in
                range(default_nb, default_nb+10)]
        self.insert(client, collection_name, rows)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: vectors[i],
                 default_string_field_name: str(i), json_field_name: {}} for i in
                range(default_nb+10, default_nb+20)]
        self.insert(client, collection_name, rows)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: vectors[i],
                 default_string_field_name: str(i), json_field_name: {'a': [1, 2, 3]}} for i in
                range(default_nb + 20, default_nb + 30)]
        self.insert(client, collection_name, rows)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: vectors[i],
                 default_string_field_name: str(i), json_field_name: {'a': [{'b': 1}, 2, 3]}} for i in
                range(default_nb + 20, default_nb + 30)]
        self.insert(client, collection_name, rows)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: vectors[i],
                 default_string_field_name: str(i), json_field_name: {'a': [{'b': None}, 2, 3]}} for i in
                range(default_nb + 30, default_nb + 40)]
        self.insert(client, collection_name, rows)
        # 2. prepare index params
        index_name = "json_index"
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name=default_vector_field_name, index_type="AUTOINDEX", metric_type="COSINE")
        index_params.add_index(field_name=json_field_name, index_name=index_name, index_type=supported_varchar_scalar_index,
                               params={"json_cast_type": supported_json_cast_type, "json_path": f"{json_field_name}['a']['b']"})
        index_params.add_index(field_name=json_field_name, index_name=index_name + '1',
                               index_type=supported_varchar_scalar_index,
                               params={"json_cast_type": supported_json_cast_type,
                                       "json_path": f"{json_field_name}['a']"})
        index_params.add_index(field_name=json_field_name, index_name=index_name + '2',
                               index_type=supported_varchar_scalar_index,
                               params={"json_cast_type": supported_json_cast_type,
                                       "json_path": f"{json_field_name}"})
        index_params.add_index(field_name=json_field_name, index_name=index_name + '3',
                               index_type=supported_varchar_scalar_index,
                               params={"json_cast_type": supported_json_cast_type,
                                       "json_path": f"{json_field_name}['a'][0]['b']"})
        index_params.add_index(field_name=json_field_name, index_name=index_name + '4',
                               index_type=supported_varchar_scalar_index,
                               params={"json_cast_type": supported_json_cast_type,
                                       "json_path": f"{json_field_name}['a'][0]"})
        # 3. create index
        self.create_index(client, collection_name, index_params)
        self.describe_index(client, collection_name, index_name,
                            check_task=CheckTasks.check_describe_index_property,
                            check_items={
                                "json_cast_type": supported_json_cast_type,
                                "json_path": f"{json_field_name}['a']['b']",
                                "index_type": supported_varchar_scalar_index,
                                "field_name": json_field_name,
                                "index_name": index_name})
        self.describe_index(client, collection_name, index_name + '1',
                            check_task=CheckTasks.check_describe_index_property,
                            check_items={
                                "json_cast_type": supported_json_cast_type,
                                "json_path": f"{json_field_name}['a']",
                                "index_type": supported_varchar_scalar_index,
                                "field_name": json_field_name,
                                "index_name": index_name + '1'})
        self.describe_index(client, collection_name, index_name +'2',
                            check_task=CheckTasks.check_describe_index_property,
                            check_items={
                                "json_cast_type": supported_json_cast_type,
                                "json_path": f"{json_field_name}",
                                "index_type": supported_varchar_scalar_index,
                                "field_name": json_field_name,
                                "index_name": index_name + '2'})
        self.describe_index(client, collection_name, index_name + '3',
                            check_task=CheckTasks.check_describe_index_property,
                            check_items={
                                "json_cast_type": supported_json_cast_type,
                                "json_path": f"{json_field_name}['a'][0]['b']",
                                "index_type": supported_varchar_scalar_index,
                                "field_name": json_field_name,
                                "index_name": index_name + '3'})
        self.describe_index(client, collection_name, index_name + '4',
                            check_task=CheckTasks.check_describe_index_property,
                            check_items={
                                "json_cast_type": supported_json_cast_type,
                                "json_path": f"{json_field_name}['a'][0]",
                                "index_type": supported_varchar_scalar_index,
                                "field_name": json_field_name,
                                "index_name": index_name + '4'})

    @pytest.mark.tags(CaseLabel.L1)
    @pytest.mark.parametrize("enable_dynamic_field", [True, False])
    def test_milvus_client_insert_after_json_path_index(self, enable_dynamic_field, supported_json_cast_type,
                                                         supported_varchar_scalar_index):
        """
        target: test insert after create json path index
        method: create json path index after insert
        steps: 1. create schema
               2. create all the index parameters including json path index
               3. create collection with schema and index params
               4. insert
               5. check the index
        expected: insert successfully after create json path index
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection with schema and all the index parameters
        json_field_name = "my_json"
        schema = self.create_schema(client, enable_dynamic_field=enable_dynamic_field)[0]
        schema.add_field(default_primary_key_field_name, DataType.INT64, is_primary=True, auto_id=False)
        schema.add_field(default_vector_field_name, DataType.FLOAT_VECTOR, dim=default_dim)
        schema.add_field(default_string_field_name, DataType.VARCHAR, max_length=64)
        if not enable_dynamic_field:
            schema.add_field(json_field_name, DataType.JSON)
        index_name = "json_index"
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(default_vector_field_name, metric_type="COSINE")
        index_params.add_index(field_name=json_field_name, index_name=index_name, index_type=supported_varchar_scalar_index,
                               params={"json_cast_type": supported_json_cast_type, "json_path": f"{json_field_name}['a']['b']"})
        index_params.add_index(field_name=json_field_name, index_name=index_name + '1',
                               index_type=supported_varchar_scalar_index,
                               params={"json_cast_type": supported_json_cast_type,
                                       "json_path": f"{json_field_name}['a']"})
        index_params.add_index(field_name=json_field_name, index_name=index_name + '2',
                               index_type=supported_varchar_scalar_index,
                               params={"json_cast_type": supported_json_cast_type,
                                       "json_path": f"{json_field_name}"})
        index_params.add_index(field_name=json_field_name, index_name=index_name + '3',
                               index_type=supported_varchar_scalar_index,
                               params={"json_cast_type": supported_json_cast_type,
                                       "json_path": f"{json_field_name}['a'][0]['b']"})
        index_params.add_index(field_name=json_field_name, index_name=index_name + '4',
                               index_type=supported_varchar_scalar_index,
                               params={"json_cast_type": supported_json_cast_type,
                                       "json_path": f"{json_field_name}['a'][0]"})
        self.create_collection(client, collection_name, schema=schema, index_params=index_params)
        # 2. insert with different data distribution
        vectors = cf.gen_vectors(default_nb+50, default_dim)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: vectors[i],
                 default_string_field_name: str(i), json_field_name: {'a': {"b": i}}} for i in
                range(default_nb)]
        self.insert(client, collection_name, rows)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: vectors[i],
                 default_string_field_name: str(i), json_field_name: i} for i in
                range(default_nb, default_nb+10)]
        self.insert(client, collection_name, rows)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: vectors[i],
                 default_string_field_name: str(i), json_field_name: {}} for i in
                range(default_nb+10, default_nb+20)]
        self.insert(client, collection_name, rows)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: vectors[i],
                 default_string_field_name: str(i), json_field_name: {'a': [1, 2, 3]}} for i in
                range(default_nb + 20, default_nb + 30)]
        self.insert(client, collection_name, rows)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: vectors[i],
                 default_string_field_name: str(i), json_field_name: {'a': [{'b': 1}, 2, 3]}} for i in
                range(default_nb + 20, default_nb + 30)]
        self.insert(client, collection_name, rows)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: vectors[i],
                 default_string_field_name: str(i), json_field_name: {'a': [{'b': None}, 2, 3]}} for i in
                range(default_nb + 30, default_nb + 40)]
        self.insert(client, collection_name, rows)
        # 3. check the json path index
        self.describe_index(client, collection_name, index_name,
                            check_task=CheckTasks.check_describe_index_property,
                            check_items={
                                "json_cast_type": supported_json_cast_type,
                                "json_path": f"{json_field_name}['a']['b']",
                                "index_type": supported_varchar_scalar_index,
                                "field_name": json_field_name,
                                "index_name": index_name})
        self.describe_index(client, collection_name, index_name + '1',
                            check_task=CheckTasks.check_describe_index_property,
                            check_items={
                                "json_cast_type": supported_json_cast_type,
                                "json_path": f"{json_field_name}['a']",
                                "index_type": supported_varchar_scalar_index,
                                "field_name": json_field_name,
                                "index_name": index_name + '1'})
        self.describe_index(client, collection_name, index_name +'2',
                            check_task=CheckTasks.check_describe_index_property,
                            check_items={
                                "json_cast_type": supported_json_cast_type,
                                "json_path": f"{json_field_name}",
                                "index_type": supported_varchar_scalar_index,
                                "field_name": json_field_name,
                                "index_name": index_name + '2'})
        self.describe_index(client, collection_name, index_name + '3',
                            check_task=CheckTasks.check_describe_index_property,
                            check_items={
                                "json_cast_type": supported_json_cast_type,
                                "json_path": f"{json_field_name}['a'][0]['b']",
                                "index_type": supported_varchar_scalar_index,
                                "field_name": json_field_name,
                                "index_name": index_name + '3'})
        self.describe_index(client, collection_name, index_name + '4',
                            check_task=CheckTasks.check_describe_index_property,
                            check_items={
                                "json_cast_type": supported_json_cast_type,
                                "json_path": f"{json_field_name}['a'][0]",
                                "index_type": supported_varchar_scalar_index,
                                "field_name": json_field_name,
                                "index_name": index_name + '4'})




