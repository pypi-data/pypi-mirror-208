from pathlib import Path

import pandas as pd
from sarus_data_spec.config import (
    DP_TRANSFORMS,
    PEP_TRANSFORMS,
    WHITELISTED_TRANSFORMS,
)

from sarus.utils import _registered_functions, _registered_methods


def op_list() -> pd.DataFrame:
    """Return the list of ops in a pandas DataFrame."""
    global _registered_functions, _registered_methods

    methods = pd.DataFrame.from_records(_registered_methods)
    methods.columns = ["module", "class", "method", "code"]

    functions = pd.DataFrame.from_records(_registered_functions)
    functions.columns = ["module", "function", "code"]

    all_items = methods.append(functions, ignore_index=True)

    all_items["whitelisted"] = all_items.code.isin(WHITELISTED_TRANSFORMS)
    all_items["pep"] = all_items.code.isin(PEP_TRANSFORMS)
    all_items["dp"] = all_items.code.isin(DP_TRANSFORMS)
    return all_items


def to_markdown(op_list: pd.DataFrame) -> str:
    """Generate the list of registered operations and whitelisted operations.

    NB: This does not list DataspecWrappers without any operations declared.
    """
    lines = []
    for mod_name, mod_df in op_list.groupby(by="module"):
        lines.append(f"\n# {mod_name}")

        fns = (
            mod_df.loc[:, ["function", "code"]]
            .dropna()
            .sort_values(by="function")
        )

        if len(fns) > 0:
            lines.append("\n## Functions")
            lines += list(map(lambda x: f"- `{x}`", fns.function))

        for class_name, class_df in mod_df.groupby("class"):
            if class_name == "DataSpecWrapper":
                class_name = "Generic Operations"
            lines.append(f"\n## {class_name}")
            methods = (
                class_df.loc[:, ["method", "code"]]
                .dropna()
                .sort_values(by="method")
            )
            lines += list(map(lambda x: f"- `{x}`", methods.method))

    return "\n".join(lines)


def to_markdown_table(op_list: pd.DataFrame) -> str:
    """Generate the op list as a Markdown table."""
    functions = op_list[op_list["class"].isna()]
    methods = op_list[~op_list["class"].isna()]
    methods_full_name = methods[["module", "class", "method"]].apply(
        lambda x: ".".join(x), axis=1
    )
    functions_full_name = functions[["module", "function"]].apply(
        lambda x: ".".join(x), axis=1
    )
    op_list["Supported ops"] = pd.concat(
        [methods_full_name, functions_full_name]
    ).apply(lambda x: f"`{x}`")
    table_data = op_list[["Supported ops", "pep", "dp", "code"]]
    table_data["PEP condition"] = table_data.apply(
        lambda row: PEP_TRANSFORMS.get(row.code, ""), axis=1
    )
    table_data["DP condition"] = table_data.apply(
        lambda row: DP_TRANSFORMS.get(row.code, ""), axis=1
    )
    table_data = table_data.drop("code", axis=1)
    table_data.columns = [
        "Supported ops",
        "PEP",
        "DP",
        "PEP condition",
        "DP condition",
    ]
    table_data = table_data[
        ["Supported ops", "PEP", "PEP condition", "DP", "DP condition"]
    ]
    table_data = table_data.replace({True: "Yes", False: "No"})
    return table_data.to_markdown(index=False)


def to_interactive_html(op_list: pd.DataFrame) -> str:
    """The Jinja template was created using an HTML export of an itables DataFrame."""
    from jinja2 import Environment, FileSystemLoader

    environment = Environment(
        loader=FileSystemLoader(Path(__file__).parent), autoescape=True
    )
    template = environment.get_template("template.html")
    return template.render(data=op_list.astype(str).values.tolist())


if __name__ == "__main__":
    import argparse

    default_output_dir = (
        Path(__file__).parent.parent.parent / "docs" / "sdk_documentation"
    )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        "-o",
        dest="output_dir",
        default=str(default_output_dir),
    )
    args = parser.parse_args()
    output_dir = Path(args.output_dir)

    all_ops = op_list()

    # All ops as markdown
    with open(output_dir / "op_list.md", "w") as f:
        f.write(to_markdown(all_ops))

    # All ops as markdown table
    with open(output_dir / "op_table.md", "w") as f:
        f.write(to_markdown_table(all_ops))

    # Whitelisted ops as markdown
    with open(output_dir / "whitelisted_op_list.md", "w") as f:
        f.write(to_markdown(all_ops.loc[all_ops.whitelisted]))

    # All ops as interactive HTML
    with open(output_dir / "interactive_op_list.html", "w") as f:
        f.write(to_interactive_html(all_ops))
