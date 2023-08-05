from odapqi.api.functions import check_active


class SegmentApi:
    def __init__(self, *, features_table: str, segments_table: str):
        self.features_table = features_table
        self.segments_table = segments_table
        self.active = False

        if features_table and segments_table:
            self.active = True

    @check_active
    def get_columns(self):
        desc = self.spark.sql(f"DESCRIBE {self.features_table}").collect()
        return [row["col_name"] for row in desc]

    @check_active
    def get_segments(self):
        return self.spark.sql(
            f"SELECT id, name, conditions FROM {self.segments_table}"
        ).collect()

    @check_active
    def get_segment_by_id(self, id: str):
        return self.spark.sql(
            f"SELECT id, name, conditions FROM {self.segments_table} WHERE id = '{id}'"
        ).first()

    @check_active
    def calculate_conditions(self, query):
        return self.spark.sql(
            f"SELECT Count(*) FROM {self.features_table}{' WHERE '+query if query else ''}"
        ).collect()[0]["count(1)"]

    @check_active
    def save_segment_sql(self, value: str, update: str = ""):
        if update:
            self.spark.sql(f"UPDATE {self.segments_table} SET {update}")
        else:
            self.spark.sql(
                f"INSERT INTO {self.segments_table} (id, name, conditions, pyspark, total) VALUES {value};"
            )

    @check_active
    def remove_segment_sql(self, id: str):
        self.spark.sql(f"DELETE FROM {self.segments_table} WHERE id LIKE '{id}%';")
