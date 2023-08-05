import sqlglot
from sqlglot import to_identifier
from sqlglot.expressions import TableAlias


def postgres_table_replacements(dataset):
    """Return a function to do table replacements for Postgres -> DuneSQL, with appropriate dataset"""

    def table_replacement_transform(table_node):
        """Replace table names in the query AST with the appropriate DuneSQL table names"""

        # We only want to do something here if we've recursed all the way to a table node in the query AST
        if not isinstance(table_node, sqlglot.exp.Table):
            return table_node

        spellbook_mapping = {
            ("erc20", "erc20_evt_transfer"): (f"erc20_{dataset}", "evt_Transfer"),
            ("bep20", "bep20_evt_transfer"): ("erc20_bnb", "evt_Transfer"),
            ("erc721", "erc721_evt_transfer"): ("erc721_ethereum", "evt_Transfer"),
            ("bep20", "tokens"): ("tokens", "erc20"),
            ("erc20", "tokens"): ("tokens", "erc20"),
            ("erc721", "tokens"): ("tokens", "nft"),
            ("prices", "layer1_usd_btc"): ("prices", "usd"),
            ("prices", "layer1_usd_eth"): ("prices", "usd"),
        }
        table = table_node.db.lower(), table_node.name.lower()
        replacement = spellbook_mapping.get(table)
        if replacement is not None:
            to_db, to_table = replacement
            return sqlglot.exp.Table(
                this=to_identifier(to_table),
                db=to_identifier(to_db),
                alias=TableAlias(this=to_identifier(table_node.alias)) if table_node.alias else None,
            )

        # if decoded table, add _{dataset} to the table name
        if any(decoded in table_node.name.lower() for decoded in ("_evt_", "_call_")):
            to_db, to_table = f"{table_node.db}_{dataset}", table_node.name
            return sqlglot.exp.Table(
                this=to_identifier(to_table),
                db=to_identifier(to_db),
                alias=TableAlias(this=to_identifier(table_node.alias)) if table_node.alias else None,
            )

        return table_node

    return table_replacement_transform
