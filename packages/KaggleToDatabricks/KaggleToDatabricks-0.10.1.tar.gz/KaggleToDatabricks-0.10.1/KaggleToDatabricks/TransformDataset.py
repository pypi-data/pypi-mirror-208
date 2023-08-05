class TransformDataset:
    import pandas as pd
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("pandas to spark").getOrCreate()

    def df_from_dataset(self, input_path, dataset_file):
        """
        This method is accepting csv file and tranforming it into pandas dataframe
        :param input_path - string - path to csv file: 
        :param dataset_file - string - name of csv file: 
        :return: pandas dataframe
        """
        df = self.pd.read_csv(f'{input_path}/{dataset_file}')
        return df

    def filter_dataset(self, df,col_list_to_drop):
        """
        This method is removing columns from dataframe
        :param df - dataframe to remove columns from: 
        :param col_list_to_drop:  list - list of columns to drop
        :return: pandas dataframe
        """
        df2 = df.drop(columns=col_list_to_drop)
        return df2

    def get_max_from_dataset(self, df, col_list_to_groupby, col_get_max):
        """
        This method groups records in dataframe by col_list_to_groupby and gets maximum value from col_get_max column
        :param df: datframe
        :param col_list_to_groupby: list of columns
        :param col_get_max: string - column name to get max value from
        :return: pandas dataframe
        """
        df2 = df.groupby(col_list_to_groupby)[col_get_max].max().reset_index()
        return (df2)

    def write_df_to_parquet(self, df, output_path):
        """
        This method is accepting pandas dataframe and using pyspark tranform it into spark dataframe and store it in parquets in output_path
        :param df: dataframe
        :param output_path: string - path to folder with parquet files
        """
        sdf = self.spark.createDataFrame(df)
        sdf.write.mode("overwrite").parquet(output_path)