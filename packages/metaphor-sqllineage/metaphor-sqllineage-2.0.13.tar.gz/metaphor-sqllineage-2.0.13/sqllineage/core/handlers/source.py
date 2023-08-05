import re
from typing import Dict, List, Optional, Set, Union

from sqlparse.sql import (
    Case,
    Function,
    Identifier,
    IdentifierList,
    Operation,
    Parenthesis,
    Token,
)
from sqlparse.tokens import Literal, Wildcard

from sqllineage.core.handlers.base import NextTokenBaseHandler
from sqllineage.core.holders import SubQueryLineageHolder
from sqllineage.core.models import Column, Path, SubQuery, Table, TableMetadata
from sqllineage.exceptions import SQLLineageException
from sqllineage.utils.constant import EdgeType
from sqllineage.utils.entities import ColumnQualifierTuple
from sqllineage.utils.sqlparse import (
    get_subquery_parentheses,
    is_subquery,
    is_values_clause,
)


class SourceHandler(NextTokenBaseHandler):
    """Source Table & Column Handler."""

    SOURCE_TABLE_TOKENS = (
        r"FROM",
        # inspired by https://github.com/andialbrecht/sqlparse/blob/master/sqlparse/keywords.py
        r"((LEFT\s+|RIGHT\s+|FULL\s+)?(INNER\s+|OUTER\s+|STRAIGHT\s+)?|(CROSS\s+|NATURAL\s+)?)?JOIN",
    )

    def __init__(self, table_metadata=TableMetadata()):
        self.column_flag = False
        self.columns = []
        self.tables = []
        self.union_barriers = []
        super().__init__(table_metadata)

    def _indicate(self, token: Token) -> bool:
        if token.normalized in ("UNION", "UNION ALL"):
            self.union_barriers.append((len(self.columns), len(self.tables)))

        if any(re.match(regex, token.normalized) for regex in self.SOURCE_TABLE_TOKENS):
            self.column_flag = False
            return True
        elif token.normalized == "SELECT":
            self.column_flag = True
            return True
        elif token.normalized == "DISTINCT" and self.column_flag:
            return True
        else:
            return False

    def _handle(self, token: Token, holder: SubQueryLineageHolder) -> None:
        if self.column_flag:
            self._handle_column(token)
        else:
            self._handle_table(token, holder)

    def _handle_table(self, token: Token, holder: SubQueryLineageHolder) -> None:
        if isinstance(token, Identifier):
            self._add_dataset_from_identifier(token, holder)
        elif isinstance(token, IdentifierList):
            # This is to support join in ANSI-89 syntax
            for identifier in token.get_sublists():
                self._add_dataset_from_identifier(identifier, holder)
        elif isinstance(token, Parenthesis):
            if is_subquery(token):
                # SELECT col1 FROM (SELECT col2 FROM tab1), the subquery will be parsed as Parenthesis
                # This syntax without alias for subquery is invalid in MySQL, while valid for SparkSQL
                self.tables.append(SubQuery.of(token, None))
            elif is_values_clause(token):
                # SELECT * FROM (VALUES ...), no operation needed
                pass
            else:
                # SELECT * FROM (tab2), which is valid syntax
                self._handle(token.tokens[1], holder)
        elif token.ttype == Literal.String.Single:
            self.tables.append(Path(token.value))
        elif isinstance(token, Function):
            # functions like unnest or generator can output a sequence of values as source, ignore it for now
            pass
        else:
            raise SQLLineageException(
                "An Identifier is expected, got %s[value: %s] instead."
                % (type(token).__name__, token)
            )

    def _handle_column(self, token: Token) -> None:
        column_token_types = (Identifier, Function, Operation, Case)
        if isinstance(token, column_token_types) or token.ttype is Wildcard:
            column_tokens = [token]
        elif isinstance(token, IdentifierList):
            column_tokens = [
                sub_token
                for sub_token in token.tokens
                if isinstance(sub_token, column_token_types)
            ]
        else:
            # SELECT constant value will end up here
            column_tokens = []
        for token in column_tokens:
            self.columns.append(Column.of(token))

    def end_of_query_cleanup(
        self,
        holder: SubQueryLineageHolder,
        target_table: Optional[Union[SubQuery, Table]],
    ) -> None:
        for i, tbl in enumerate(self.tables):
            holder.add_read(tbl)
        subquery_columns = self._find_subquery_columns(holder)

        # match source column qualifier based on all the table alias
        all_table_alias = self._get_alias_mapping_from_table_group(self.tables, holder)
        for column in self.columns:
            self._match_source_column_qualifier(column, all_table_alias)

        # find column lineage
        self.union_barriers.append((len(self.columns), len(self.tables)))
        for i, (col_barrier, tbl_barrier) in enumerate(self.union_barriers):
            prev_col_barrier, prev_tbl_barrier = (
                (0, 0) if i == 0 else self.union_barriers[i - 1]
            )
            col_grp = self.columns[prev_col_barrier:col_barrier]
            tbl_grp = self.tables[prev_tbl_barrier:tbl_barrier]
            if target_table:
                for tgt_col in col_grp:
                    tgt_col.parent = target_table
                    column_lineage = tgt_col.find_column_lineage(
                        self._get_alias_mapping_from_table_group(tbl_grp, holder),
                        subquery_columns,
                        self.table_metadata,
                    )
                    for source_col, target_col in column_lineage:
                        holder.add_column_lineage(source_col, target_col)

    def _add_dataset_from_identifier(
        self, identifier: Identifier, holder: SubQueryLineageHolder
    ) -> None:
        dataset: Union[Path, Table, SubQuery]
        first_token = identifier.token_first(skip_cm=True)
        if isinstance(first_token, Function):
            # function() as alias, no dataset involved
            return
        elif isinstance(first_token, Parenthesis) and is_values_clause(first_token):
            # (VALUES ...) AS alias, no dataset involved
            return
        path_match = re.match(r"(parquet|csv|json)\.`(.*)`", identifier.value)
        if path_match is not None:
            dataset = Path(path_match.groups()[1])
        else:
            read: Union[Table, SubQuery, None] = None
            subqueries = get_subquery_parentheses(identifier)
            if len(subqueries) > 0:
                # SELECT col1 FROM (SELECT col2 FROM tab1) dt, the subquery will be parsed as Identifier
                # referring https://github.com/andialbrecht/sqlparse/issues/218 for further information
                parenthesis, alias = subqueries[0]
                read = SubQuery.of(parenthesis, alias)
            else:
                if "." not in identifier.value:
                    cte_dict = {s.alias: s for s in holder.cte}
                    cte = cte_dict.get(identifier.get_real_name().lower())
                    if cte is not None:
                        # could reference CTE with or without alias
                        read = SubQuery.of(
                            cte.token,
                            (
                                identifier.get_alias() or identifier.get_real_name()
                            ).lower(),
                        )
                if read is None:
                    read = Table.of(identifier, self.table_metadata)
            dataset = read
        self.tables.append(dataset)

    @classmethod
    def _get_alias_mapping_from_table_group(
        cls,
        table_group: List[Union[Path, Table, SubQuery]],
        holder: SubQueryLineageHolder,
    ) -> Dict[str, Union[Path, Table, SubQuery]]:
        """
        A table can be referred to as alias, table name, or database_name.table_name, create the mapping here.
        For SubQuery, it's only alias then.
        """
        return {
            **{
                tgt: src
                for src, tgt, attr in holder.graph.edges(data=True)
                if attr.get("type") == EdgeType.HAS_ALIAS and src in table_group
            },
            **{
                table.raw_name: table
                for table in table_group
                if isinstance(table, Table)
            },
            **{str(table): table for table in table_group if isinstance(table, Table)},
        }

    @classmethod
    def _find_subquery_columns(
        cls,
        holder: SubQueryLineageHolder,
    ) -> Dict[SubQuery, Set[Column]]:
        """
        Finds the mapping between subqueries and their columns from the holder graph
        """
        mapping: Dict[SubQuery, Set[Column]] = {}
        for src, tgt, attr in holder.graph.edges(data=True):
            if attr.get("type") == EdgeType.HAS_COLUMN and isinstance(src, SubQuery):
                if src not in mapping:
                    mapping[src] = set()
                mapping[src].add(tgt)

        return mapping

    @staticmethod
    def _match_source_column_qualifier(
        column: Column, table_alias: Dict[str, Union[Path, Table, SubQuery]]
    ) -> None:
        """
        Best effort to match the qualifier of the source columns from their fullnames.

        If the fullname contains only one segment (no "."), then no action.
        If the fullname's prefix matches any of the table alias, then use that table as the qualifier.
        If no alias matches the fullname, treat the fullname as a nested column, with the first segment as
        the top-level column.
        """
        for i, source_col in enumerate(column.source_columns):
            col, qualifier, fullname = source_col
            if not fullname or fullname.count(".") == 0:
                break

            for alias in table_alias.keys():
                if (
                    fullname.startswith(alias)
                    and len(fullname) > len(alias)
                    and fullname[len(alias)] == "."
                ):
                    column.source_columns[i] = ColumnQualifierTuple(
                        col, alias, fullname
                    )
                    break
            else:
                top_level_column = fullname.split(".")[0]
                column.source_columns[i] = ColumnQualifierTuple(
                    top_level_column, None, fullname
                )
