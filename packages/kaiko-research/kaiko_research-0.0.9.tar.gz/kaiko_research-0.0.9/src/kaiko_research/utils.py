import re
from cerberus import Validator

# Validators for request parameters


def validate_time(time_field, time_value, error):
    ISO8601_REGEX = re.compile(
        "^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d{3})Z$"
    )
    if not bool(ISO8601_REGEX.match(time_value)):
        error(
            time_field,
            f"The {time_field} is not in ISO 8601 format, please refer to an example: 2023-01-01T00:00:00.000Z",
        )


def validate_bases(bases_field, bases_value, error):
    count = (
        len(bases_value)
        if isinstance(bases_value, list)
        else len(bases_value.split(","))
    )
    if count > 5:
        error(
            bases_field,
            f"The {bases_field} contains more than five exchanges, please check your query",
        )


def validate_bases_weights(weights_field, weights_value, error):
    weights = [float(_) for _ in weights_value.split(",")]
    if (sum(weights)) != 1:
        error(
            weights_field,
            f"The {weights_field} does not sum up to 1, please check the weights allocation",
        )


def validate_risk_level(risk_field, risk_value, error):
    risk = float(risk_value)
    if risk >= 1 or risk < 0.9:
        error(risk_field, f"The {risk_field} is outside of [0.9, 1) interval")


class ParamsValidator(Validator):
    def _validate_part_of_query(self, constraint, field, value):
        if not constraint:
            if len(value) < 1:
                self._error(field, "seems to be too short")


def check_nest(obj, nest=[]):
    for k in obj.keys():
        if type(obj[k]) == dict:
            nest = check_nest(obj[k], nest)
        else:
            nest += [obj[k]]
    return nest


def flatten_dataframe(df):
    row = df.loc[0, :].to_dict()
    print(check_nest(row))
    return df
