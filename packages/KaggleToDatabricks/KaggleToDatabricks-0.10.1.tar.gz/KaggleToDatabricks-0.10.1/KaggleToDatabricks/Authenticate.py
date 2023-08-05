class Authenticate:

	def authenticate_kaggle(self,KAGGLE_USERNAME,KAGGLE_KEY):
        """
        This method is used to authenticate Kaggle API using provided credentials
        :param KAGGLE_USERNAME: string - username of Kaggle account
        :param KAGGLE_KEY: string - key generated for Kaggle account
        :return: kaggle api object - used for downloading datasets
        """
		import os
		os.environ['KAGGLE_USERNAME'] = KAGGLE_USERNAME
		os.environ['KAGGLE_KEY'] = KAGGLE_KEY

		from kaggle.api.kaggle_api_extended import KaggleApi

		api = KaggleApi()
		api.authenticate()

		return api
