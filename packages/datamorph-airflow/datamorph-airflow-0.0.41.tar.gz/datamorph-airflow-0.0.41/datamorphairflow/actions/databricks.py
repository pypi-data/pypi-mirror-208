from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator


class DMDatabricksRunNowJobOperator(DatabricksRunNowOperator):
    """
    Extension of databricks run now operator with custom status push to xcom
    """

    def __init__(
            self, *args, **kwargs
    ):
        super().__init__(do_xcom_push=True, *args, **kwargs)
        # self.databricks_conn_id = databricks_conn_id

    def execute(self, context):
        super(DMDatabricksRunNowJobOperator, self).execute(context)
        run_id = context["task_instance"].xcom_pull(self.task_id, key="run_id")
        self.log.info(run_id)
        self.log.info(self.run_id)


class DMDatabricksPythonRunNowJobOperator(DatabricksRunNowOperator):
    """
    Extension of databricks run now operator with custom status push to xcom
    """

    def __init__(
            self, *args, **kwargs
    ):
        super().__init__(do_xcom_push=True, *args, **kwargs)
        # self.databricks_conn_id = databricks_conn_id

    def execute(self, context):
        super(DMDatabricksPythonRunNowJobOperator, self).execute(context)
        run_id = context["task_instance"].xcom_pull(self.task_id, key="run_id")
        self.log.info(run_id)
        self.log.info(self.run_id)
