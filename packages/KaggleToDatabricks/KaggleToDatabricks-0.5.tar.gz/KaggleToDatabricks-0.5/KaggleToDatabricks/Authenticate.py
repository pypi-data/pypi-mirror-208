class Authenticate:

	def authenticate_kaggle(KAGGLE_USERNAME,KAGGLE_KEY):
		import os
		os.environ['KAGGLE_USERNAME'] = KAGGLE_USERNAME
		os.environ['KAGGLE_KEY'] = KAGGLE_KEY

		from kaggle.api.kaggle_api_extended import KaggleApi

		api = KaggleApi()
		api.authenticate()

		return api
