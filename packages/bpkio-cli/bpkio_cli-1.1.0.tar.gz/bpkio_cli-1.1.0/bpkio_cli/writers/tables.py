import click
import tabulate

from .colorizer import Colorizer as CL


def display_table(data):
    table = None

    if isinstance(data, list):
        # list of dict
        if len(data) and isinstance(data[0], dict):
            # determine whether an index need to be shown
            showindex = True
            if len(data) and "index" in data[0]:
                showindex = False

            # data = [rows] if len(rows) == 2 else [[r] for r in rows]

            # colorize data
            colorized_data = []
            for dic in data:
                new_dic = {}
                for k, v in dic.items():
                    # colorize relative time data
                    # TODO - super-specific to the current use case, needs to be generalized
                    if k in ["relativeStartTime", "relativeEndTime"]:
                        if "(-" in v:
                            v = CL.past(v)
                        else:
                            v = CL.future(v)

                    # add to new dic, with colorized headers
                    new_dic[CL.attr(k)] = v

                colorized_data.append(new_dic)

            table = tabulate.tabulate(
                colorized_data,
                headers="keys",
                showindex=showindex,
                tablefmt="psql",
                disable_numparse=True,
            )

        # list of scalars
        elif len(data):
            # horizontal or vertical, based on number of cells
            data = [data] if len(data) == 2 else [[r] for r in data]

            table = tabulate.tabulate(
                data,
                tablefmt="psql",
            )

    if isinstance(data, dict):
        dict_items = [(CL.attr(k), v) for k, v in data.items()]

        table = tabulate.tabulate(dict_items, tablefmt="psql")

    if table:
        click.echo(table)
