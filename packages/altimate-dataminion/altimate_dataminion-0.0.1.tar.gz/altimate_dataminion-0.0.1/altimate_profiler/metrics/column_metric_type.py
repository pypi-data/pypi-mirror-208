from enum import Enum


class ColumnMetricType(Enum):
    APPROX_DISTINCTNESS = "_approx_distinctness"
    COMPLETENESS = "_completeness"
    ZERO_RATE = "_zero_rate"
    NEGATIVE_RATE = "_negative_rate"
    MEAN = "_numeric_mean"
    MIN = "_numeric_min"
    MAX = "_numeric_max"
    NUMERIC_STD = "_numeric_std"
    APPROX_DISTINCT_COUNT = "_approx_distinct_count"
    MEAN_LENGTH = "_mean_length"
    MAX_LENGTH = "_max_length"
    MIN_LENGTH = "_min_length"
    STD_LENGTH = "_std_length"
    TEXT_INT_RATE = "_text_int_rate"
    TEXT_NUMBER_RATE = "_text_number_rate"
    TEXT_UUID_RATE = "_text_uuid_rate"
    TEXT_ALL_SPACES_RATE = "_text_all_spaces_rate"
    TEXT_NULL_KEYWORD_RATE = "_text_null_keyword_rate"
    CATEGORIES = "_categories"
    FUTURE_DATES_RATE = "_future_dates_rate"
    INVALID_EMAIL_RATE = "_invalid_email_rate"
    PERCENTAGE_SELECTS = "_percentage_selects"
    PERCENTAGE_INSERTS = "_percentage_inserts"
    PERCENTAGE_WAREHOUSE_SIZE_X_SMALL = "_percentage_warehouse_size_x_small"
    PERCENTAGE_FAILURES = "_percentage_failures"
    AVERAGE_NON_NEGATIVE = "_average_non_negative"
    MAX_NON_NEGATIVE = "_max_non_negative"
    MIN_NON_NEGATIVE = "_min_non_negative"
    PERCENTAGE_WAREHOUSE_IS_XSMALL = "_percentage_warehouse_is_xsmall"
    AVG_ROWS_INSERTED_OR_UPDATED = "_avg_rows_inserted_or_updated"
    AVG_SELECT_QUERY_TIME = "_avg_select_query_time"
    CONDITIONAL_MAX = "_conditional_max"
    CONDITIONAL_MIN = "_conditional_min"
    CONDITIONAL_MEAN = "_conditional_mean"
    CONDITIONAL_COUNT = "_conditional_count"
    CONDITIONAL_PERCENTAGE = "_conditional_percentage"
    NULL_COUNT = "_null_count"
    NULL_PERCENTAGE = "_null_percentage"
    CARDINALITY = "_cardinality"
    CATEGORY_COUNT = "_cardinality"
    REGEX_MATCH_PERCENTAGE = "_regex_match_percentage"
    LIKE_PERCENTAGE = "_like_percentage"
    DATES_IN_FUTURE_PERCENTAGE = "_dates_in_future_percentage"
    ALLOWED_VALUES = "_allowed_values"
    NUMERIC_MODE = "_numeric_mode"
    NUMERIC_MEDIAN = "_numeric_median"
    PERCENTILE = "_percentile"
    NUMERIC_VARIANCE = "_numeric_variance"
