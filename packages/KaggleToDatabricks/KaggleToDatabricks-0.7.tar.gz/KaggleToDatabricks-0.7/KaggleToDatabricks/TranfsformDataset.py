class TransformDataset:
    import pandas as pd
    from pyspark.sql import SparkSession

    spark = self.SparkSession.builder.appName("pandas to spark").getOrCreate()

    def df_from_dataset(self,input_path,dataset_file):
        df = self.pd.read_csv(f'{input_path}/{dataset_file}')
        return df

    def filter_dataset(self,df,dataset_file,col_list_to_drop):
        df2 = df.drop(columns=col_list_to_drop)
        return df2

    def get_max_from_dataset(self,df,col_list_to_groupby,col_get_max):
        df2 = df.groupby(col_list_to_groupby)[col_get_max].max().reset_index()
        return(df2)
    
    def write_df_to_parquet(self,df,output_path):
        sdf = self.spark.createDataFrame(df)
        sdf.write.mode("overwrite").parquet(output_path)