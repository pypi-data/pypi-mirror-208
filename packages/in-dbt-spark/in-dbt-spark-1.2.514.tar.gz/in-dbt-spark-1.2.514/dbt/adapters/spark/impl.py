import re
from concurrent.futures import Future
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union, Callable
from typing_extensions import TypeAlias
from dbt.contracts.graph.manifest import Manifest

import agate
from agate import Table

from dbt.contracts.relation import RelationType

import dbt
import dbt.exceptions

from dbt.adapters.base import AdapterConfig
from dbt.adapters.base.impl import catch_as_completed
from dbt.adapters.sql import SQLAdapter
from dbt.adapters.spark import SparkConnectionManager
from dbt.adapters.spark import SparkRelation
from dbt.adapters.spark import SparkColumn
from dbt.adapters.base import BaseRelation, available
from dbt.clients.agate_helper import DEFAULT_TYPE_TESTER
from dbt.events import AdapterLogger
from dbt.utils import executor, AttrDict
from dbt.dataclass_schema import dbtClassMixin, ValidationError

logger = AdapterLogger("Spark")

GET_COLUMNS_IN_RELATION_RAW_MACRO_NAME = "get_columns_in_relation_raw"
LIST_SCHEMAS_MACRO_NAME = "list_schemas"
LIST_RELATIONS_MACRO_NAME = "list_relations_without_caching"
LIST_RELATIONS_SHOW_TABLES_MACRO_NAME = "list_relations_show_tables_without_caching"
DESCRIBE_TABLE_EXTENDED_MACRO_NAME = "describe_table_extended_without_caching"
DROP_RELATION_MACRO_NAME = "drop_relation"
FETCH_TBL_PROPERTIES_MACRO_NAME = "fetch_tbl_properties"

CURRENT_CATALOG_MACRO_NAME = "current_catalog"
USE_CATALOG_MACRO_NAME = "use_catalog"

KEY_TABLE_OWNER = "Owner"
KEY_TABLE_STATISTICS = "Statistics"
KEY_TABLE_TYPE = "Type"
KEY_TABLE_PROVIDER = "Provider"

TABLE_OR_VIEW_NOT_FOUND_MESSAGES = (
    "[TABLE_OR_VIEW_NOT_FOUND]",
    "Table or view not found",
    "NoSuchTableException",
)


@dataclass
class PartitionConfig(dbtClassMixin):
    field: str
    data_type: str
    granularity: Optional[str] = None

    @classmethod
    def parse(cls, partition_by) -> Optional["PartitionConfig"]:

        if partition_by is None:
            return None
        try:
            cls.validate(partition_by)
            return cls.from_dict(partition_by)
        except ValidationError as exc:
            raise dbt.exceptions.ValidationException("Could not parse partition config") from exc
        except TypeError:
            raise dbt.exceptions.CompilationError(
                f"Invalid partition_by config:\n"
                f"  Got: {partition_by}\n"
                f'  Expected a dictionary with "field" and "data_type" keys'
            )


@dataclass
class SparkConfig(AdapterConfig):
    file_format: str = "openhouse"
    location_root: Optional[str] = None
    partition_by: Optional[Union[List[Dict[str, str]], Dict[str, str]]] = None
    retention_period: Optional[str] = None
    clustered_by: Optional[Union[List[str], str]] = None
    buckets: Optional[int] = None
    options: Optional[Dict[str, str]] = None
    merge_update_columns: Optional[str] = None


class SparkAdapter(SQLAdapter):
    COLUMN_NAMES = (
        "table_database",
        "table_schema",
        "table_name",
        "table_type",
        "table_comment",
        "table_owner",
        "column_name",
        "column_index",
        "column_type",
        "column_comment",
        "stats:bytes:label",
        "stats:bytes:value",
        "stats:bytes:description",
        "stats:bytes:include",
        "stats:rows:label",
        "stats:rows:value",
        "stats:rows:description",
        "stats:rows:include",
    )
    INFORMATION_COLUMNS_REGEX = re.compile(r"^ \|-- (.*): (.*) \(nullable = (.*)\b", re.MULTILINE)
    INFORMATION_OWNER_REGEX = re.compile(r"^Owner: (.*)$", re.MULTILINE)
    INFORMATION_STATISTICS_REGEX = re.compile(r"^Statistics: (.*)$", re.MULTILINE)
    HUDI_METADATA_COLUMNS = [
        "_hoodie_commit_time",
        "_hoodie_commit_seqno",
        "_hoodie_record_key",
        "_hoodie_partition_path",
        "_hoodie_file_name",
    ]

    Relation: TypeAlias = SparkRelation
    RelationInfo = Tuple[str, str, str, str]
    Column: TypeAlias = SparkColumn
    ConnectionManager: TypeAlias = SparkConnectionManager
    AdapterSpecificConfigs: TypeAlias = SparkConfig

    @classmethod
    def date_function(cls) -> str:
        return "current_timestamp()"

    @classmethod
    def convert_text_type(cls, agate_table, col_idx):
        return "string"

    @classmethod
    def convert_number_type(cls, agate_table, col_idx):
        decimals = agate_table.aggregate(agate.MaxPrecision(col_idx))
        return "double" if decimals else "bigint"

    @classmethod
    def convert_date_type(cls, agate_table, col_idx):
        return "date"

    @classmethod
    def convert_time_type(cls, agate_table, col_idx):
        return "time"

    @classmethod
    def convert_datetime_type(cls, agate_table, col_idx):
        return "timestamp"

    def quote(self, identifier):
        return "`{}`".format(identifier)

    def add_schema_to_cache(self, schema) -> str:
        """Cache a new schema in dbt. It will show up in `list relations`."""
        if schema is None:
            name = self.nice_connection_name()
            dbt.exceptions.raise_compiler_error(
                "Attempted to cache a null schema for {}".format(name)
            )
        if dbt.flags.USE_CACHE:
            self.cache.add_schema(None, schema)
        # so jinja doesn't render things
        return ""

    def _get_relation_information(
        self, schema_relation: BaseRelation, row: agate.Row
    ) -> RelationInfo:
        """relation info was fetched with SHOW TABLES EXTENDED"""
        try:
            _schema, name, _, information = row
        except ValueError:
            raise dbt.exceptions.RuntimeException(
                f'Invalid value from "show tables extended ...", got {len(row)} values, expected 4'
            )

        return schema_relation.database, _schema, name, information

    def _get_relation_information_using_describe(
        self, schema_relation: BaseRelation, row: agate.Row
    ) -> RelationInfo:
        """Relation info fetched using SHOW TABLES and an auxiliary DESCRIBE statement"""
        try:
            _schema, name = row
        except ValueError:
            raise dbt.exceptions.RuntimeException(
                f'Invalid value from "show tables ...", got {len(row)} values, expected 2'
            )

        is_openhouse = schema_relation.database == "openhouse" or "." in schema_relation.schema

        # database is needed where relations can exist in different catalogs
        table_name = f"{_schema}.{name}"
        if is_openhouse:
            if not table_name.startswith("openhouse."):
                table_name = "openhouse." + table_name
            _schema = "openhouse." + _schema

        try:
            table_results = self.execute_macro(
                DESCRIBE_TABLE_EXTENDED_MACRO_NAME, kwargs={"table_name": table_name}
            )
        except dbt.exceptions.RuntimeException as e:
            logger.debug(f"Error while retrieving information about {table_name}: {e.msg}")
            table_results = AttrDict()

        information = ""
        for info_row in table_results:
            info_type, info_value, _ = info_row
            if not info_type.startswith("#"):
                information += f"{info_type}: {info_value}\n"

        return schema_relation.database, _schema, name, information

    def _build_spark_relation_list(
        self,
        schema_relation: BaseRelation,
        row_list: agate.Table,
        relation_info_func: Callable[[BaseRelation, agate.Row], RelationInfo],
    ) -> List[BaseRelation]:
        """Aggregate relations with format metadata included."""
        relations = []
        for row in row_list:
            database, _schema, name, information = relation_info_func(schema_relation, row)

            rel_type: RelationType = (
                RelationType.View if "Type: VIEW" in information else RelationType.Table
            )
            is_delta: bool = "Provider: delta" in information
            is_hudi: bool = "Provider: hudi" in information
            is_iceberg: bool = "Provider: iceberg" in information
            is_openhouse: bool = "Provider: openhouse" in information

            relation: BaseRelation = self.Relation.create(  # type: ignore
                database=database if database else None,
                schema=_schema,
                identifier=name,
                type=rel_type,
                information=information,
                is_delta=is_delta,
                is_iceberg=is_iceberg,
                is_hudi=is_hudi,
                is_openhouse=is_openhouse,
            )
            relations.append(relation)

        return relations

    def list_relations_without_caching(self, schema_relation: BaseRelation) -> List[BaseRelation]:
        """Distinct Spark compute engines may not support the same SQL featureset. Thus, we must
        try different methods to fetch relation information."""

        kwargs = {"schema_relation": schema_relation}

        is_openhouse = schema_relation.database == "openhouse" or "." in schema_relation.schema

        try:
            if is_openhouse:
                # Iceberg behavior: 3-row result of relations obtained
                show_table_rows = self.execute_macro(
                    LIST_RELATIONS_SHOW_TABLES_MACRO_NAME, kwargs=kwargs
                )
                return self._build_spark_relation_list(
                    schema_relation=schema_relation,
                    row_list=show_table_rows,
                    relation_info_func=self._get_relation_information_using_describe,
                )
            else:
                with self._catalog(schema_relation.database):
                    show_table_extended_rows = self.execute_macro(
                        LIST_RELATIONS_MACRO_NAME, kwargs=kwargs
                    )
                    return self._build_spark_relation_list(
                        schema_relation=schema_relation,
                        row_list=show_table_extended_rows,
                        relation_info_func=self._get_relation_information,
                    )
        except dbt.exceptions.RuntimeException as e:
            errmsg = getattr(e, "msg", "")
            print(errmsg)
            if f"Database '{schema_relation}' not found" in errmsg:
                return []
            # Iceberg compute engine behavior: show table
            elif "SHOW TABLE EXTENDED is not supported for v2 tables" in errmsg:
                # this happens with spark-iceberg with v2 iceberg tables
                # https://issues.apache.org/jira/browse/SPARK-33393
                try:
                    # Iceberg behavior: 3-row result of relations obtained
                    show_table_rows = self.execute_macro(
                        LIST_RELATIONS_SHOW_TABLES_MACRO_NAME, kwargs=kwargs
                    )
                    return self._build_spark_relation_list(
                        schema_relation=schema_relation,
                        row_list=show_table_rows,
                        relation_info_func=self._get_relation_information_using_describe,
                    )
                except dbt.exceptions.RuntimeException as e:
                    description = "Error while retrieving information about"
                    logger.debug(f"{description} {schema_relation}: {e.msg}")
                    return []
            else:
                logger.debug(
                    f"Error while retrieving information about {schema_relation}: {errmsg}"
                )
                return []

    def get_relation(
        self, database: Optional[str], schema: str, identifier: str
    ) -> Optional[BaseRelation]:
        if not self.Relation.include_policy.database:
            database = None
        else:
            database = database if database else None

        return super().get_relation(database, schema, identifier)

    def parse_describe_extended(
        self, relation: Relation, raw_rows: List[agate.Row]
    ) -> List[SparkColumn]:
        # Convert the Row to a dict
        dict_rows = [dict(zip(row._keys, row._values)) for row in raw_rows]
        # Find the separator between the rows and the metadata provided
        # by the DESCRIBE TABLE EXTENDED statement
        pos = self.find_table_information_separator(dict_rows)

        # Remove rows that start with a hash, they are comments
        rows = [row for row in raw_rows[0:pos] if not row["col_name"].startswith("#")]

        metadata = {col["col_name"]: col["data_type"] for col in raw_rows[pos + 1 :]}

        raw_table_stats = metadata.get(KEY_TABLE_STATISTICS)
        table_stats = SparkColumn.convert_table_stats(raw_table_stats)
        return [
            SparkColumn(
                table_database=relation.database,
                table_schema=relation.schema,
                table_name=relation.name,
                table_type=relation.type,
                table_owner=str(metadata.get(KEY_TABLE_OWNER)),
                table_stats=table_stats,
                column=column["col_name"],
                column_index=idx,
                dtype=column["data_type"],
            )
            for idx, column in enumerate(rows)
        ]

    @staticmethod
    def find_table_information_separator(rows: List[dict]) -> int:
        pos = 0
        for row in rows:
            if not row["col_name"] or row["col_name"].startswith("#"):
                break
            pos += 1
        return pos

    def get_columns_in_relation(self, relation: Relation) -> List[SparkColumn]:
        cached_relations = self.cache.get_relations(relation.database, relation.schema)
        cached_relation = next(
            (
                cached_relation
                for cached_relation in cached_relations
                if str(cached_relation) == str(relation)
            ),
            None,
        )
        columns = []
        if cached_relation and cached_relation.information:
            columns = self.parse_columns_from_information(cached_relation)
        if not columns:
            # in open source delta 'show table extended' query output doesnt
            # return relation's schema. if columns are empty from cache,
            # use get_columns_in_relation spark macro
            # which would execute 'describe extended tablename' query
            try:
                rows: List[agate.Row] = self.execute_macro(
                    GET_COLUMNS_IN_RELATION_RAW_MACRO_NAME, kwargs={"relation": relation}
                )
                columns = self.parse_describe_extended(relation, rows)
            except dbt.exceptions.RuntimeException as e:
                # spark would throw error when table doesn't exist, where other
                # CDW would just return and empty list, normalizing the behavior here
                errmsg = getattr(e, "msg", "")
                found_msgs = (msg in errmsg for msg in TABLE_OR_VIEW_NOT_FOUND_MESSAGES)
                if any(found_msgs):
                    pass
                else:
                    raise e

        # strip hudi metadata columns.
        columns = [x for x in columns if x.name not in self.HUDI_METADATA_COLUMNS]
        return columns

    def parse_columns_from_information(self, relation: SparkRelation) -> List[SparkColumn]:
        owner_match = re.findall(self.INFORMATION_OWNER_REGEX, relation.information)
        owner = owner_match[0] if owner_match else None
        matches = re.finditer(self.INFORMATION_COLUMNS_REGEX, relation.information)
        columns = []
        stats_match = re.findall(self.INFORMATION_STATISTICS_REGEX, relation.information)
        raw_table_stats = stats_match[0] if stats_match else None
        table_stats = SparkColumn.convert_table_stats(raw_table_stats)
        for match_num, match in enumerate(matches):
            column_name, column_type, nullable = match.groups()
            column = SparkColumn(
                table_database=relation.database,
                table_schema=relation.schema,
                table_name=relation.table,
                table_type=relation.type,
                column_index=match_num,
                table_owner=owner,
                column=column_name,
                dtype=column_type,
                table_stats=table_stats,
            )
            columns.append(column)
        return columns

    def _get_columns_for_catalog(self, relation: SparkRelation) -> Iterable[Dict[str, Any]]:
        columns = self.parse_columns_from_information(relation)

        for column in columns:
            # convert SparkColumns into catalog dicts
            as_dict = column.to_column_dict()
            as_dict["column_name"] = as_dict.pop("column", None)
            as_dict["column_type"] = as_dict.pop("dtype")
            as_dict["table_database"] = relation.database
            yield as_dict

    def get_properties(self, relation: Relation) -> Dict[str, str]:
        properties = self.execute_macro(
            FETCH_TBL_PROPERTIES_MACRO_NAME, kwargs={"relation": relation}
        )
        return dict(properties)

    def get_catalog(self, manifest: Manifest) -> Tuple[Table, List[Exception]]:
        schema_map = self._get_catalog_schemas(manifest)

        with executor(self.config) as tpe:
            futures: List[Future[Table]] = []
            for info, schemas in schema_map.items():
                for schema in schemas:
                    futures.append(
                        tpe.submit_connected(
                            self, schema, self._get_one_catalog, info, [schema], manifest
                        )
                    )
            catalogs, exceptions = catch_as_completed(futures)
        return catalogs, exceptions

    def _get_one_catalog(
        self,
        information_schema,
        schemas,
        manifest,
    ) -> agate.Table:
        if len(schemas) != 1:
            dbt.exceptions.raise_compiler_error(
                f"Expected only one schema in spark _get_one_catalog, found " f"{schemas}"
            )

        database = information_schema.database
        schema = list(schemas)[0]

        columns: List[Dict[str, Any]] = []
        for relation in self.list_relations(database, schema):
            logger.debug("Getting table schema for relation {}", relation)
            columns.extend(self._get_columns_for_catalog(relation))
        return agate.Table.from_object(columns, column_types=DEFAULT_TYPE_TESTER)

    def list_schemas(self, database: str) -> List[str]:
        connection = self.connections.get_if_exists()
        if connection is not None:
            database = connection.credentials.database
            schema = connection.credentials.schema

        # in case the user is using "openhouse" as a catalog, the format of schema will be 'openhouse.db'.
        # so derive the catalog/database value from schema until we support `openhouse` catalog natively.
        if schema is not None and "." in schema:
            tokens = schema.split(".")
            database = tokens[0]
            schema = tokens[1]

        # The catalog for `show table extended` needs to match the current catalog.
        with self._catalog(database):
            results = self.execute_macro(LIST_SCHEMAS_MACRO_NAME, kwargs={"database": schema})
        schema_list = [row[0] for row in results]
        return schema_list

    def check_schema_exists(self, database, schema):
        # in case the user is using "openhouse" as a catalog, the format of schema will be 'openhouse.db'.
        # so derive the catalog/database value from schema until we support `openhouse` catalog natively.
        if schema is not None and "." in schema:
            tokens = schema.split(".")
            database = tokens[0]
            schema = tokens[1]
        # The catalog for `show table extended` needs to match the current catalog.
        with self._catalog(database):
            results = self.execute_macro(LIST_SCHEMAS_MACRO_NAME, kwargs={"database": schema})
        exists = True if schema in [row[0] for row in results] else False
        return exists

    def get_rows_different_sql(
        self,
        relation_a: BaseRelation,
        relation_b: BaseRelation,
        column_names: Optional[List[str]] = None,
        except_operator: str = "EXCEPT",
    ) -> str:
        """Generate SQL for a query that returns a single row with a two
        columns: the number of rows that are different between the two
        relations and the number of mismatched rows.
        """
        # This method only really exists for test reasons.
        names: List[str]
        if column_names is None:
            columns = self.get_columns_in_relation(relation_a)
            names = sorted((self.quote(c.name) for c in columns))
        else:
            names = sorted((self.quote(n) for n in column_names))
        columns_csv = ", ".join(names)

        sql = COLUMNS_EQUAL_SQL.format(
            columns=columns_csv,
            relation_a=str(relation_a),
            relation_b=str(relation_b),
        )

        return sql

    # This is for use in the test suite
    # Spark doesn't have 'commit' and 'rollback', so this override
    # doesn't include those commands.
    def run_sql_for_tests(self, sql, fetch, conn):
        cursor = conn.handle.cursor()
        try:
            cursor.execute(sql)
            if fetch == "one":
                if hasattr(cursor, "fetchone"):
                    return cursor.fetchone()
                else:
                    # AttributeError: 'PyhiveConnectionWrapper' object has no attribute 'fetchone'
                    return cursor.fetchall()[0]
            elif fetch == "all":
                return cursor.fetchall()
            else:
                return
        except BaseException as e:
            print(sql)
            print(e)
            raise
        finally:
            conn.transaction_open = False

    def standardize_grants_dict(self, grants_table: agate.Table) -> dict:
        grants_dict: Dict[str, List[str]] = {}
        for row in grants_table:
            grantee = row["Principal"]
            privilege = row["ActionType"]
            object_type = row["ObjectType"]

            # we only want to consider grants on this object
            # (view or table both appear as 'TABLE')
            # and we don't want to consider the OWN privilege
            if object_type == "TABLE" and privilege != "OWN":
                if privilege in grants_dict.keys():
                    grants_dict[privilege].append(grantee)
                else:
                    grants_dict.update({privilege: [grantee]})
        return grants_dict

    @contextmanager
    def _catalog(self, catalog: Optional[str]) -> Iterator[None]:
        """
        A context manager to make the operation work in the specified catalog,
        and move back to the current catalog after the operation.
        If `catalog` is None, the operation works in the current catalog.
        """
        current_catalog: Optional[str] = None
        try:
            if catalog is not None:
                current_catalog = self.execute_macro(CURRENT_CATALOG_MACRO_NAME)[0][0]
                if current_catalog is not None:
                    if current_catalog != catalog:
                        self.execute_macro(USE_CATALOG_MACRO_NAME, kwargs=dict(catalog=catalog))
                    else:
                        current_catalog = None
            yield
        finally:
            if current_catalog is not None:
                self.execute_macro(USE_CATALOG_MACRO_NAME, kwargs=dict(catalog=current_catalog))

    @available
    def parse_partition_by(self, raw_partition_by: Any):
        partition_by_list = []
        if raw_partition_by is None:
            return None
        if isinstance(raw_partition_by, dict):
            raw_partition_by = [raw_partition_by]
        for partition_by in raw_partition_by:
            partition_by_list.append(PartitionConfig.parse(partition_by))
        return partition_by_list


# spark does something interesting with joins when both tables have the same
# static values for the join condition and complains that the join condition is
# "trivial". Which is true, though it seems like an unreasonable cause for
# failure! It also doesn't like the `from foo, bar` syntax as opposed to
# `from foo cross join bar`.
COLUMNS_EQUAL_SQL = """
with diff_count as (
    SELECT
        1 as id,
        COUNT(*) as num_missing FROM (
            (SELECT {columns} FROM {relation_a} EXCEPT
             SELECT {columns} FROM {relation_b})
             UNION ALL
            (SELECT {columns} FROM {relation_b} EXCEPT
             SELECT {columns} FROM {relation_a})
        ) as a
), table_a as (
    SELECT COUNT(*) as num_rows FROM {relation_a}
), table_b as (
    SELECT COUNT(*) as num_rows FROM {relation_b}
), row_count_diff as (
    select
        1 as id,
        table_a.num_rows - table_b.num_rows as difference
    from table_a
    cross join table_b
)
select
    row_count_diff.difference as row_count_difference,
    diff_count.num_missing as num_mismatched
from row_count_diff
cross join diff_count
""".strip()
