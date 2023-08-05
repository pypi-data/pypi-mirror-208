from ..utils import packages_are_installed
import logging
if not packages_are_installed(["s3fs", "minio"]): 
    message = "Please install pysparkutilities (https://pypi.org/project/pyspark-utilities/), pyspark and a Java virtual machine if you want to use datasets contained in Hive DB."
    logging.error(message)
    exit(1)

else:
    import glob
    import os
    from pysparkutilities import ds_initializer
    from pysparkutilities.spark_initializer import spark_initializer
    from bdaserviceutils import get_args


    def from_spark_to_pandas_df_using_disk(df, path='/tmp/tmp_csv_df'):

        df = df.to_pandas_on_spark()
        df.to_csv(path, header=True, num_files=1, mode="overwrite")

        extension = 'csv'
        os.chdir(path)
        result = glob.glob('*.{}'.format(extension))[0]

        return result

    def init_spark():
        return spark_initializer("Ds-io", get_args(), additional_config=[('spark.sql.execution.arrow.enabled', True)])


    def get_path(name):
        df = ds_initializer.load_dataset(sc=init_spark(), name=name, read_all=False)
        return from_spark_to_pandas_df_using_disk(df)

