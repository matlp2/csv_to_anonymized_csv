# commande: (kill -9 $(lsof -ti tcp:8080)) ; (python3 serveur.py &(sleep 0 ; chromium "http://127.0.0.1:8080/tout"))



tumult_functions = {
	'count': {
		'nb_columns_min': 0,
		'nb_columns_max': 0,
		'parameters':[],
		#'group_by_allowed': False,
		'group_by_allowed': True,
		'positive_result_default_value': True,
	},
	'count_distinct': {
		'nb_columns_min': 1,
		'nb_columns_max': 5000,#float("inf"),
		'parameters': [
			'columns'
		],
		#'group_by_allowed': False,
		'group_by_allowed': True,
		'positive_result_default_value': True,
	},
	'quantile': {
		'nb_columns_min': 1,
		'nb_columns_max': 1,
		'parameters':[
			'column',
			'quantile',
			'low',
			'high'
		],
		'group_by_allowed': True,
		'positive_result_default_value': False,
	},
	'min': {
		'nb_columns_min': 1,
		'nb_columns_max': 1,
		'parameters': [
			'column',
			'low',
			'high'
		],
		'group_by_allowed': True,
		'positive_result_default_value': False,
	},
	'max': {
		'nb_columns_min': 1,
		'nb_columns_max': 1,
		'parameters': [
			'column',
			'low',
			'high'
		],
		'group_by_allowed': True,
		'positive_result_default_value': False,
	},
	'median': {
		'nb_columns_min': 1,
		'nb_columns_max': 1,
		'parameters': [
			'column',
			'low',
			'high'
		],
		'group_by_allowed': True,
		'positive_result_default_value': False,
	},
	'sum': {
		'nb_columns_min': 1,
		'nb_columns_max': 1,
		'parameters': [
			'column',
			'low',
			'high'
		],
		'group_by_allowed': True,
		'positive_result_default_value': False,
	},
	'average': {
		'nb_columns_min': 1,
		'nb_columns_max': 1,
		'parameters': [
			'column',
			'low',
			'high'
		],
		'group_by_allowed': True,
		'positive_result_default_value': False,
	},
	'variance': {
		'nb_columns_min': 1,
		'nb_columns_max': 1,
		'parameters': [
			'column',
			'low',
			'high'
		],
		'group_by_allowed': True,
		'positive_result_default_value': False,
	},
	'stdev': {
		'nb_columns_min': 1,
		'nb_columns_max': 1,
		'parameters': [
			'column',
			'low',
			'high'
		],
		'group_by_allowed': True,
		'positive_result_default_value': False,
	},
}


def normalize_name(s, retirer_les_accents = False, to_lower_case = False):

	# from unidecode import unidecode

	r = ''

	for c in s:

		if to_lower_case:
			c = c.lower()

		o = ord(c)
	
		if ord('0') <= ord(c) <= ord('9') or ord('a') <= ord(c) <= ord('z') or ord('A') <= ord(c) <= ord('Z'):
			r += c
			continue

		if retirer_les_accents:
			if c in ('à', 'â', 'ä'):
				r += 'a'
				continue
			if c in ('À', 'Â', 'Ä'):
				r += 'A' if not to_lower_case else 'a'
				continue
			if c in ('é','è','ê'):
				r += 'e'
				continue
			if c in ('E','È','Ê'):
				r += 'E' if not to_lower_case else 'e'
				continue
			if c in ('ù','û'):
				r += 'u'
				continue
		else:
			if c in ('à','é','è','ç','ù','ê','à'):
				r += c
				continue

		r += '_'


	return r

from datetime import datetime

print('import pyspark')
from pyspark import SparkFiles
from pyspark.sql import SparkSession
from pyspark.sql import functions
import pyspark.sql.functions
import pyspark.sql.types
import pyspark as spark
import pyspark.sql.catalog


print('import analytics')
from tmlt.analytics.keyset import KeySet
from tmlt.analytics.privacy_budget import PureDPBudget
from tmlt.analytics.protected_change import AddOneRow
from tmlt.analytics.query_builder import QueryBuilder
from tmlt.analytics.session import Session

#import tmlt.analytics as tumult


import pandas as pd
import io

my_spark_session = None

#print('import matplotlib')
#import matplotlib.pyplot as plt
#print('import seaborn')
#import seaborn as sns



# import my_html
import sys
#sys.path.append('..')
from my_html import *
from prt import *
from itertools import islice
from collections import OrderedDict
import copy
import traceback
import subprocess
import pathlib
import functools


def open_folder(path):

	if sys.platform == 'darwin':
		subprocess.check_call(['open', '--', path])

	elif sys.platform == 'win32':
		subprocess.check_call(['explorer ', path])
	#elif sys.platform == 'linux2':
	else:
		subprocess.check_call(['xdg-open', path])






def get_copy_of_spark_dataframe_with_minimum_value_of_0_enforced_on_each_row(
	spark_dataframe,
	column_name
):
	return spark_dataframe.withColumn(
		column_name,
		pyspark.sql.functions.when(pyspark.sql.functions.col(column_name) < 0, 0)
			.otherwise(pyspark.sql.functions.col(column_name))
	)



def execute_sql_request_without_anonymisation(
	spark_session,
	spark_dataframe,
	table_name,
	sql_request,
):
	table_name = normalize_name(table_name, retirer_les_accents = True, to_lower_case = False)

	for field in list(map(lambda type:type[0], spark_dataframe.dtypes)):
		spark_dataframe = spark_dataframe.withColumnRenamed(field, normalize_name(field, retirer_les_accents = True, to_lower_case = False))

	spark_dataframe.createOrReplaceTempView(table_name)

	spark_dataframe_result = spark_session.sql(sql_request)

	#pyspark.sql.catalog.dropGlobalTempView(table_name)
	spark_session.catalog.dropTempView(table_name)

	return spark_dataframe_result


import math
from collections import namedtuple
class dict_dot_access(dict):
    # https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__





def drop_rows_with_null_or_NaN_values(
	spark_data_frame,
	columns,
):
	return spark_data_frame.na.drop(subset=columns)




def remove_outliers_interquartile_range(
	spark_dataframe,
	column_name
):
	# https://blog.zhaytam.com/2019/07/15/outliers-detection-in-pyspark-2-interquartile-range/

	#column = spark_dataframe[column_name]

	frac1 = .25
	frac3 = .75
	
	q1, q3 = spark_dataframe.approxQuantile(column_name, [frac1, frac3], 0)

	iqr = q3 - q1

	# 1.5 doit rester 1.5: https://math.stackexchange.com/questions/966331/why-john-tukey-set-1-5-iqr-to-detect-outliers-instead-of-1-or-2

	mini = q1 - iqr*1.5
	maxi = q3 + iqr*1.5

	return dict_dot_access({
		'frac1': frac1,
		'frac3': frac3,
		'q1': q1,
		'q3': q3,
		'bounds': [mini, maxi],
		'data_frame_result': spark_dataframe.filter(
			pyspark.sql.functions.col(column_name).between(mini, maxi)
		),
	})



def remove_outliers_standard_deviation(
	spark_dataframe,
	column_name
):
	# https://towardsdatascience.com/outlier-detection-part1-821d714524c

	#avg = spark_dataframe.select(pyspark.sql.functions.avg(column_name)).collect()
	mean = spark_dataframe.select(pyspark.sql.functions.mean(column_name)).collect()[0][0]
	stddev = spark_dataframe.select(pyspark.sql.functions.stddev(column_name)).collect()[0][0]

	lower_limit = mean - 3 * stddev
	upper_limit = mean + 3 * stddev

	return dict_dot_access({
		'lower_limit': lower_limit,
		'upper_limit': upper_limit,
		'mean': mean,
		'stddev': stddev,
		'data_frame_result': spark_dataframe.filter(
			pyspark.sql.functions.col(column_name).between(lower_limit, upper_limit)
		),
	})
	 




def remove_outliers_trim(
	spark_dataframe,
	column_name,
	min_in_percent,
	max_in_percent,
):
	
	# sort
	r = spark_dataframe.sort(column_name, ascending=True)

	# add index column
	r = r.select("*").withColumn('index', pyspark.sql.functions.monotonically_increasing_id())

	# number of lines removes
	number_of_minimum_values_removed = math.floor(r.count()*(min_in_percent/100)+.5)
	number_of_maximum_values_removed = math.floor(r.count()*(max_in_percent/100)+.5)

	# bounds infos
	table = r.collect()

	min_min = table[0][column_name] if number_of_minimum_values_removed > 0 else None
	min_max = table[number_of_minimum_values_removed-1][column_name] if number_of_minimum_values_removed > 0 else None

	max_min = table[(r.count()-1)-number_of_maximum_values_removed + 1][column_name] if number_of_maximum_values_removed > 0 else None
	max_max = table[r.count()-1][column_name] if number_of_maximum_values_removed > 0 else None

	# trim
	r = r.filter(r.index.between(number_of_minimum_values_removed, (r.count()-1)-number_of_maximum_values_removed))

	# remove index column
	r = r.drop('index')

	return dict_dot_access({
		'number_of_minimum_values_removed': number_of_minimum_values_removed,
		'number_of_maximum_values_removed': number_of_maximum_values_removed,
		'minimum_range_removed': dict_dot_access({
			'min': min_min,
			'max': min_max,
		}),
		'maximum_range_removed': dict_dot_access({
			'min': max_min,
			'max': max_max,
		}),
		'data_frame_result': r,
	})

	

'''
def remove_outliers(
	spark_session,
	spark_dataframe,
	ratio,
):
	# https://www.advancinganalytics.co.uk/blog/2020/9/2/identifying-outliers-in-spark-30
	# Median Absolute Deviation in Spark

	MADdf = spark_dataframe.agg(
				pyspark.sql.functions.expr('percentile(duration, array(0.5))'
			)[0].alias(
				'duration_median'
			)
		).join(
			spark_dataframe,
			"genre",
			"left"
		).withColumn(
			"duration_difference_median",
			pyspark.sql.functions.abs(
				pyspark.sql.functions.col('duration')-pyspark.sql.functions.col('duration_median')
			)
		).groupby('genre', 'duration_median').agg(F.expr('percentile(duration_difference_median, array(0.5))')[0].alias('median_absolute_difference'))

	outliersremoved = df.join(MADdf, "genre", "left").filter(F.abs(F.col("duration")-F.col("duration_median")) <= (F.col("mean_absolute_difference")*3))


	stddevdf = spark_dataframe.agg(
		pyspark.sql.functions.stddev_pop("duration").alias("duration_std_pop"),
		pyspark.sql.functions.avg("duration").alias("duration_avg")
	)

	outliersremoved = df.join(stddevdf, "genre", "left").filter(F.abs(F.col("duration")-F.col("duration_avg")) <= (F.col("duration_std_pop")*3))


	spark_session

	tmp_df = spark_dataframe.withColumn(
		'percentile_value', 
		pyspark.sql.functions.expr(
			f'percentile_approx(value, {ratio})'
		).over(
			pyspark.sql.Window.partitionBy('category')
		)
	)

	return tmp_df.select(
			'category',
			when(tmp_df.percentile_value >= tmp_df.value, tmp_df.value).alias('value')
		)
'''


# returns the list of (csv_key, query_key, type, result)
def start_tumult_session():

	clear_result_folder()


	def modify_column_name(name):
		return normalize_name(name, retirer_les_accents=False, to_lower_case=True)
		#return '`'+name+'`'
		#return name.replace('.', '_')


	with prt(f'start tumult session', color = 'yellow'):

		response = []

		spark_dataframes = dict()

		csv_having_request = list(filter(lambda e: e['type']=='csv' and len(e['requests'])>0, csv_list))

		try:

			global my_spark_session

			if my_spark_session == None:
				with prt('start spark session', color = 'yellow'):
					my_spark_session = SparkSession.builder.getOrCreate()

			builder = Session.Builder()

			#builder.with_privacy_budget(PureDPBudget(epsilon=float('inf')))
			#builder.with_privacy_budget(PureDPBudget(epsilon = params_session['privacy_budget']))
			builder.with_privacy_budget(PureDPBudget(epsilon = json_global['privacy_budget']))

			for src in csv_having_request:

				#more_csv_results_indexed = (
				#	csv_list.index(src),
				#	None,
				#	more_csv_results := {
				#		'type': 'expand_able',
				#		'expanded': False,
				#		'title': 'more results',
				#		'subs': [],
				#		'must_be_removed_on_reload': True,
				#	}
				#)

				#response.append(more_csv_results_indexed)
				
				try:
					
					with prt(f'add {repr(src["tumult_source_id"])} to the spark session', color = 'blue'):




						'''
						def transform_each_timestamp_columns_to_a_date_column(dataframe):
							# car tumult supporte Date mais pas timestamp comme key-set

							columns_map = dict()
							
							print(dataframe.dtypes)
							user_defined_function = pyspark.sql.functions.udf(lambda ts:ts.to_date(), pyspark.sql.types.DateType())

							for column_name, column_type in dataframe.dtypes:
								if column_type == 'timestamp':
									#columns_map[column_name] = dataframe[column_name]
									#columns_map[column_name] = dataframe[column_name].to_date()
									#columns_map[column_name] = pyspark.sql.functions.to_date(dataframe[column_name])
									#columns_map[column_name] = pyspark.sql.functions.date_format(dataframe[column_name], '%a %D %b %Y %T')
									columns_map[column_name] = pyspark.sql.functions.date_format(dataframe[column_name], 'dd/MM/yyyy HH:mm:ss')
									#columns_map[column_name] = pyspark.sql.functions.second(dataframe[column_name])
									#columns_map[column_name] = pyspark.sql.functions.minute(dataframe[column_name])
									#columns_map[column_name] = user_defined_function(column_name)


							#breakpoint()

							return dataframe.withColumns(columns_map)
						'''






						#if src['src']['txt'] != None:
						if False: # csv as text not supported anymore !
							pass
						
						#	panda_dataframe = pd.read_csv(
						#		io.StringIO(src['src']['txt']),
						#		sep = src['delimiter']
						#	)

						#	dataframe = my_spark_session.createDataFrame(panda_dataframe)

							# clear panda_dataframe
						#	panda_dataframe.iloc[0:0]

						elif src['src']['path'] != None:

							path = os.path.abspath(src['src']['path'])

							prt(f'{path=}')

							my_spark_session.sparkContext.addFile(path)
							

							# eviter de lire timestampFormat et timestampNTZFormat car Tumult ne supporte pas timestamp (supporte Date mais pas timestamp comme clef pour un groupby)
							# ils sont considérés comme des strings string
							op = my_spark_session.read \
								.option('timestampFormat', '') \
								.option('timestampNTZFormat', '') \
								
							#if src['sample'].get('percent', None) != None:
							#	samplingRatio = src['sample']['percent']/100
							#	op = op.option('samplingRatio', samplingRatio)  NE MARCHE PAS
							#	src['sample']['result']['samplingRatio applied'] = samplingRatio

							dataframe = op \
								.csv(
									SparkFiles.get(path),
									header = True,
									inferSchema = True,
									sep = src['src']['delimiter'],
								)
							

							
							

							
							if src['sample']['random']['percent'] != 100:
								samplingRatio = src['sample']['random']['percent']/100
								#src['sample']['random']['samplingRatio applied'] = samplingRatio
								count_av = dataframe.count()
								dataframe = dataframe.sample(fraction = samplingRatio)
								#src['sample']['random']['result']['number of lines sampled'] = f'from {count_av} to {dataframe.count()}'
								

								src['sample']['random']['responses'].append({
									'type':'message',
									'message':f'sampled {src["sample"]["random"]["percent"]}% of lines from {count_av} initial lines down to {dataframe.count()} random lines',
									'must_be_removed_on_reload': True,
								})





							dataframe = dataframe.toDF(*(modify_column_name(column) for column in dataframe.columns))


							
							if len(columns := src['sample']['remove_lines_with_null_or_NaN_cells']['columns']) > 0:

							
								try:
									count_before = dataframe.count()

									#prt(tuple(modify_column_name(column) for column in dataframe.columns))
									#prt(tuple(map(modify_column_name, src['sample']['remove_lines_with_null_or_NaN_cells']['columns'])))

									#breakpoint()

									#if any(map(lambda c:'\n' in c, src['sample']['remove_lines_with_null_or_NaN_cells']['columns'])):
									if column_with_newline := next((c for c in src['sample']['remove_lines_with_null_or_NaN_cells']['columns'] if '\n' in c), False):

										prt(f'une_colonne_contient_un_new_line: colonne: [colonne={repr(column_with_newline)}]', color = 'red')

										raise Exception(f"il y a un new line '\\n' dans le nom d'une colonne [colonne={repr(column_with_newline)}]")


									dataframe = drop_rows_with_null_or_NaN_values(dataframe, tuple(map(modify_column_name, src['sample']['remove_lines_with_null_or_NaN_cells']['columns'])))

									src['sample']['remove_lines_with_null_or_NaN_cells']['responses'].append({
										'type': 'message',
										'message': f'removed {count_before - dataframe.count()} lines with null or NaN values',
										'must_be_removed_on_reload': True,
									})

								except BaseException as exception:
									src['sample']['remove_lines_with_null_or_NaN_cells']['responses'].append({
										'type':'error',
										'title':'remove_lines_with_null_or_NaN_cells error',
										'expanded': False,
										'exception': str(exception),
										'traceback': traceback.format_exc(),
										'must_be_removed_on_reload': True,
									})




							try: # trim-out max values and min values

								if src['sample']['trim']['min']['percent'] != 0 or src['sample']['trim']['max']['percent'] != 0:

									for column_name in set(src['sample']['trim']['min']['columns'] + src['sample']['trim']['max']['columns']):

										try:
											
											count_before = dataframe.count()

											min_percent = src['sample']['trim']['min']['percent'] if column_name in src['sample']['trim']['min']['columns'] else 0
											max_percent = src['sample']['trim']['max']['percent'] if column_name in src['sample']['trim']['max']['columns'] else 0

											trim_response = remove_outliers_trim(
												spark_dataframe = dataframe,
												column_name = modify_column_name(column_name),
												min_in_percent = min_percent,
												max_in_percent = max_percent,
											)
											
											dataframe = trim_response.data_frame_result
											
											#more_csv_results['subs'].append({

											def make_message(
													percent,
													number_of_values_removed,
													min_value_removed,
													max_value_removed
											):
												nonlocal column_name

												return (f"removing {percent}% maximal values of <i>{column_name}</i>:"
														+	f"<br>removed {number_of_values_removed} line{'s' if number_of_values_removed != 1 else ''}"
															+(
																(
																	' having values from'
																	if number_of_values_removed != 1
																	else ' of value'
																)
																+	f" <span style='color:rgb(181, 69, 4);'>{min_value_removed}</span>"
																+ (
																	f" to <span style='color:rgb(181, 69, 4);'>{max_value_removed}</span>"
																	if number_of_values_removed != 1
																	else ''
																)
																if number_of_values_removed > 0
																else ''
															)
												)
												
												
											
											if min_percent > 0:
											
												src['sample']['trim']['min']['responses'].append({
													'type': 'message',
													'message': make_message(min_percent, trim_response.number_of_minimum_values_removed, trim_response.minimum_range_removed.min, trim_response.minimum_range_removed.max)
													,
													'must_be_removed_on_reload': True,
												})


											if max_percent > 0:

												src['sample']['trim']['max']['responses'].append({
													'type': 'message',
													'message': make_message(max_percent, trim_response.number_of_maximum_values_removed, trim_response.maximum_range_removed.min, trim_response.maximum_range_removed.max)
													,
													'must_be_removed_on_reload': True,
												})

											'''
											src['sample']['trim']['responses'].append({
												'type':'message',
												'message':
															f"trim <i>{column_name}</i>:"
														+	(f"<br>removed {trim_response.number_of_minimum_values_removed} line{'s' if trim_response.number_of_minimum_values_removed != 1 else ''} having {'values from' if trim_response.number_of_minimum_values_removed != 1 else 'a value of'} <span style='color:rgb(181, 69, 4);'>{trim_response.minimum_range_removed.min}</span>"
		 													+(f" to <span style='color:rgb(181, 69, 4);'>{trim_response.minimum_range_removed.max}</span>," if trim_response.number_of_minimum_values_removed != 1 else '') if min_percent > 0 else '')
														
														+	(f"<br>removed {trim_response.number_of_maximum_values_removed} line{'s' if trim_response.number_of_maximum_values_removed != 1 else ''} having {'values from' if trim_response.number_of_maximum_values_removed != 1 else 'a value of'} <span style='color:rgb(181, 69, 4);'>{trim_response.maximum_range_removed.min}</span>"
		 													+(f" to <span style='color:rgb(181, 69, 4);'>{trim_response.maximum_range_removed.max}</span>" if trim_response.number_of_maximum_values_removed != 1 else '') if max_percent > 0 else '')
														+	f"<br>from {count_before} lines down to {dataframe.count()} lines",
												'must_be_removed_on_reload': True,
											})
											'''
											
											
										except BaseException as exception:
											
											#more_csv_results['subs'].append({
											src['sample']['trim']['responses'].append({
												'type':'error',
												'title':
															f"trim column <i>{column_name}</i> failed:"
														+	f"<br>can't apply sample trim of {src['sample']['trim']['max']['percent']}% of maximum values and {src['sample']['trim']['min']['percent']}% of minimum",
												'expanded': False,
												'exception': str(exception),
												'traceback': traceback.format_exc(),
												'must_be_removed_on_reload': True,
											})

							except BaseException as exception:
								prt(f"sample: trim-out max values and min values failed")
								#more_csv_results['expanded'] = True
								#more_csv_results['subs'].append({
								src['sample']['trim']['min']['responses'].append({
										'type':'error',
										'title': 'sample: trim-out max values and min values failed',
										'expanded': False,
										'exception': str(exception),
										'traceback': traceback.format_exc(),
										'must_be_removed_on_reload': True,
									}
								)


							try: # remove_outliers_interquartile_range

								for column_name in src['sample']['interquartile_range']['columns']:

									try:

										count_before = dataframe.count()

										result = remove_outliers_interquartile_range(dataframe, modify_column_name(column_name))

										dataframe = result.data_frame_result

										#more_csv_results['subs'].append({
										src['sample']['interquartile_range']['responses'].append({
											'type':'message',
											'message': f"remove outliers with the <i>interquartile range</i> method on column <i>{column_name}</i>:<br>parameters: frac1 = {result.frac1}, frac3 = {result.frac3}, q1 = {result.q1}, q3 = {result.q3}<br>values are filtered to be between {result.bounds[0]} and {result.bounds[1]}<br>from a total of {count_before} lines down to {dataframe.count()} lines ({count_before-dataframe.count()} lines removed)",
											'must_be_removed_on_reload': True,
										})

									except BaseException as exception:
										prt(f"remove_outliers with the <i>interquartile range</i> method on column <i>{column_name}</i> failed")
										#more_csv_results['expanded'] = True
										#more_csv_results['subs'].append({
										src['sample']['interquartile_range']['responses'].append({
											'type':'error',
											'title': f"remove_outliers with <i>interquartile range</i> method on column <i>{column_name}</i> failed",
											'expanded': False,
											'exception': str(exception),
											'traceback': traceback.format_exc(),
											'must_be_removed_on_reload': True,
										})


							except BaseException as exception:
								prt(f"remove_outliers_interquartile_range failed")
								#more_csv_results['expanded'] = True
								#more_csv_results['subs'].append({
								src['sample']['interquartile_range']['responses'].append({
										'type':'error',
										'title': 'remove_outliers_interquartile_range failed',
										'expanded': False,
										'exception': str(exception),
										'traceback': traceback.format_exc(),
										'must_be_removed_on_reload': True,
									}
								)


							try: # remove_outliers_standard_deviation

								for column_name in src['sample']['standard_deviation']['columns']:

									try:

										count_before = dataframe.count()

										result = remove_outliers_standard_deviation(dataframe, modify_column_name(column_name))

										dataframe = result.data_frame_result

										#more_csv_results['subs'].append({
											
										src['sample']['standard_deviation']['responses'].append({
											'type':'message',
											'message':		f"remove outliers with the <i>standard deviation</i> method on column <i>{column_name}</i>:"
														+	f"<br>infos: average = {result.mean}, standard_deviation = {result.stddev}"
														+	f"<br>values are filtered to be between {result.lower_limit} and {result.upper_limit}"
														+	f"<br>from a total of {count_before} lines down to {dataframe.count()} lines ({count_before-dataframe.count()} lines removed)",
											'must_be_removed_on_reload': True,
										})

									except BaseException as exception:
										prt(f"remove_outliers with <i>standard deviation</i> method on column <i>{column_name}</i> failed")
										#more_csv_results['expanded'] = True
										#more_csv_results['subs'].append({
										src['sample']['standard_deviation']['responses'].append({
											'type':'error',
											'title': f"remove_outliers with <i>standard deviation</i> method on column <i>{column_name}</i> failed",
											'expanded': False,
											'exception': str(exception),
											'traceback': traceback.format_exc(),
											'must_be_removed_on_reload': True,
										})


							except BaseException as exception:
								prt(f"remove_outliers_standard_deviation failed")
								#more_csv_results['expanded'] = True
								#more_csv_results['subs'].append({
								src['sample']['standard_deviation']['responses'].append({
										'type':'error',
										'title': 'remove_outliers_standard_deviation failed',
										'expanded': False,
										'exception': str(exception),
										'traceback': traceback.format_exc(),
										'must_be_removed_on_reload': True,
									}
								)
							


							spark_dataframes[src['tumult_source_id']] = dataframe
							

							
						else:
							raise Exception('csv with no source (path or text)')

						if src['private']:
							builder.with_private_dataframe(
								source_id = src['tumult_source_id'],
								dataframe =	dataframe
							)
						else:
							builder.with_public_dataframe(
								source_id = src['tumult_source_id'],
								dataframe =	dataframe
							)

						src['src']['spark_dataframe_successfully_loaded'] = True
						
				except BaseException as exception:
					src['src']['spark_dataframe_successfully_loaded'] = False
					prt(traceback.format_exc(), color = 'red')
					prt('-----------------------------------------')
					prt(exception, color = 'red')
					response.append(
						(
							csv_list.index(src),
							None,
							{
								'type':'error',
								'expanded': False,
								'exception':str(exception),
								'traceback':traceback.format_exc(),
								'must_be_removed_on_reload': True,
							}
						)
					)


			tumult_session = builder.build()

		except BaseException as exception:
			prt(traceback.format_exc(), color = 'red')
			prt('-----------------------------------------')
			prt(exception, color = 'red')
			response.append(
				(
					None,
					None,
					{
						'type':'error',
						'expanded': False,
						'exception':str(exception),
						'traceback':traceback.format_exc(),
						'must_be_removed_on_reload': True,
					}
				)
			)
		finally:
		
			#for src in (src for src in csv_having_request if src['src']['spark_dataframe_successfully_loaded']):
			for src in filter(lambda src:src['src']['spark_dataframe_successfully_loaded'], csv_having_request):

				for request in src['requests']:

					more_response_indexed = (
						csv_list.index(src),
						src['requests'].index(request),
						{
							'type': 'expand_able',
							'expanded': False,
							'title': 'more results',
							'subs': [],
							'must_be_removed_on_reload': True,
						}
					)

					more_response = more_response_indexed[2]

					try:

						spark_dataframe = spark_dataframes[src['tumult_source_id']]


						query_builder = QueryBuilder(src['tumult_source_id'])


						# APPLY FILTER
						if request['filter']:

							with prt(f"apply filter [{request['filter']}]", color = 'green'):



								try:
									query_builder = query_builder.filter(request['filter'])
									
								except BaseException as exception:
									prt(f"filter invalid : [{request['filter']}]")
									response.append(
										(
											csv_list.index(src),
											src['requests'].index(request),
											{
												'type':'error',
												'expanded': False,
												'exception': 'filter invalid\n' + str(exception),
												'traceback': traceback.format_exc(),
												'must_be_removed_on_reload': True,
											},
										)
									)
									continue

						
						if request['group_by']['column']: # None if no group_by
							
							group_by_column = modify_column_name(request['group_by']['column'])

							#query_str.group_by_columns = [column]

							#tumult_session.get_schema("my_private_data")

							#column_pandas_data_frame = dataframe.select(functions.col(column)).toPandas()

							#one_column_spark_dataframe = spark_dataframes[src['tumult_source_id']].select(functions.col(column))

							column_pandas_data_frame = spark_dataframe.select(functions.col(group_by_column)).toPandas()

							#prt(f'{column=}', color = 'green')
							#prt(f'{column_pandas_data_frame=}', color = 'red')
							#prt(f'{column_pandas_data_frame[column]=}', color = 'blue')

							
							key_set_dict = {
								group_by_column: list(
									sorted(set(map(lambda a:'None' if a == None else a,column_pandas_data_frame[group_by_column])),
										#key = functools.cmp_to_key(
										# permettre la comparaison de None avec des strings ou des nombres
										#	lambda a, b: 0 if a == None and b == None else 1 if b == None else -1 if a == None else 1 if a > b else -1 if a < b else 0
										#)
									)
								)
							}

							del group_by_column # don't keep value across loops

							prt('key_set_dict =', key_set_dict, color='blue')

							key_set = KeySet.from_dict(key_set_dict)

							query_builder = query_builder.groupby(key_set)


						assert request['function'] in tumult_functions



						postfix = (request['columns'][0] + '_' if request['columns'] else '')+request['function']
						# remove problematic chars from postfix
						postfix = ''.join(c for c in postfix if c.isalnum() or c == '_')
						result_file_path = os.path.abspath('./data/result') + '/' + src['tumult_source_id'] + '_' + postfix
						if result_file_path.endswith('_csv'): result_file_path = result_file_path[:-4]
						if request['group_by']['column']:
							result_file_path += '_by_'+modify_column_name(request['group_by']['column'])
						result_file_path += '.csv'


						


						result = None


						try:# anonymised request

							my_response = (
								csv_list.index(src),
								src['requests'].index(request),
								{
									'type': 'message',
									'message': 'anonymised request',
									'subs': [],
									'must_be_removed_on_reload': True,
								}
							)

							response.append(my_response)


							parameters = dict()


							for parameter in tumult_functions[request['function']]['parameters']:

								# pour un match statement en python3.10 doit être installé
								if parameter == 'column':
									assert len(request['columns']) == 1
									parameters['column'] = modify_column_name(request['columns'][0])

								elif parameter == 'columns':
									parameters['columns'] = list(map(modify_column_name, request['columns']))

								elif parameter == 'quantile':
									assert isinstance(request['quantile'], (int, float))
									parameters['quantile'] = request['quantile']

								elif parameter == 'low':
									assert len(request['clamp_range']) == 2
									assert isinstance(request['clamp_range'][0], (int, float))
									parameters['low'] = request['clamp_range'][0]

								elif parameter == 'high':
									assert len(request['clamp_range']) == 2
									assert isinstance(request['clamp_range'][1], (int, float))
									parameters['high'] = request['clamp_range'][1]

							prt(f'{parameters=}', color = 'blue')
							
							query = getattr(query_builder, request['function'])(**parameters)

							#nb_total_de_requêtes = sum(len(table['requests']) for table in json_global['elms'])
							budget_privacy_total_ponderation = sum(sum(req['budget_privacy_ponderation'] for req in table['requests']) for table in json_global['elms'])
							#nb_total_de_requêtes = sum(sum(req['budget_privacy_ponderation'] for req in table['requests']) for table in json_global['elms'])

							

							# EQUI-REPARTITION DU BUDGET-PRIVACY POUR CHAQUE REQUETE
							# - .000000001 pour pas que le budget soit insuffisant pour la derniere requête à cause d'imprécisions de calculs
							#privacy_budget_for_this_request = json_global['privacy_budget']/nb_total_de_requêtes - .000000001
							privacy_budget_for_this_request = json_global['privacy_budget']*(request['budget_privacy_ponderation']/budget_privacy_total_ponderation) - .000000001

							my_response[2]['subs'].append(
								#(
									#csv_list.index(src),
									#src['requests'].index(request),
									{
										#'type': 'privacy budget used',
										'type': 'message',
										#'value': privacy_budget_for_this_request,
										'message': 'privacy budget used for this request: ' + str(privacy_budget_for_this_request),
										'must_be_removed_on_reload': True,
									}
								#)
							)

							result = tumult_session.evaluate(
								query,
								privacy_budget = PureDPBudget(privacy_budget_for_this_request), 
							)

							#prt(f'{one_column_spark_dataframe=}', color='green')
							prt(f"{spark_dataframe=}", color='green')

							
							

							if request['make_result_positive']:
								result = get_copy_of_spark_dataframe_with_minimum_value_of_0_enforced_on_each_row(result, result.schema.names[-1])


							result_pandas_dataframe = result.toPandas()
							
							
							result_pandas_dataframe.to_csv(result_file_path, sep=';', index = False)


							my_response[2]['subs'].append(
								#(
								#	csv_list.index(src),
								#	src['requests'].index(request),
									{
										'type':'path',
										'expanded': True,
										'path': 'file://'+result_file_path,
										'something':str(result),
										'must_be_removed_on_reload': True,
									}
								#)
							)

							del my_response

						except BaseException as exception:

							prt(traceback.format_exc(), color = 'red')
							prt('-----------------------------------------')
							prt(exception, color = 'red')
							my_response[2]['subs'].append(
								{
									'type':'error',
									'title':f'anonymised request failed.',
									'expanded': False,
									'exception':str(exception),
									'traceback':traceback.format_exc(),
									'must_be_removed_on_reload': True,
								}
							)

							del my_response

						
						

						


						try: # non anonymised request
							

							#my_response = (
							#	csv_list.index(src),
							#	src['requests'].index(request),
							my_response = {
									'type': 'message',
									'message': 'non anonymised request',
									'subs': [],
									'must_be_removed_on_reload': True,
								}
							#)

							#response.append(my_response)
							more_response['subs'].append(my_response)

							def make_query_str(
								func,
								column,
								table,
								group_by,
								filter,
							):
								s = f'SELECT '

								func2 = {
									'average':'AVG(',
									'sum': 'SUM(',
									'min': 'MIN(',
									'max': 'MAX(',
									'variance': 'VARIANCE(',
									'count': 'COUNT(',
									'count_distinct':'COUNT( DISTINCT ',
									}.get(func, func+'(')
								
								request_is_count_all = (column == None and func == 'count')
								
								s += ', '.join(group_by + [f"{func2+(column if not request_is_count_all else '*')}) "])

								s += f'FROM {table}'

								if filter:
									s += ' WHERE '+ filter
									
								if group_by:
									s += ' GROUP BY ' + ', '.join(group_by)
								
								
								
								return s
							
							normalize_name_1 = lambda name: normalize_name(name, retirer_les_accents=True, to_lower_case=False)
						
							query_str = 'not generated'
							query_str = make_query_str(
								func = request['function'],
								column = normalize_name_1(request['columns'][0]) if request['columns'] else None,
								table = normalize_name_1(src['tumult_source_id']),
								group_by = [normalize_name_1(request['group_by']['column'])] if request['group_by']['column'] else [],
								filter = request['filter'],
							)

							prt(f"{query_str=}", color = 'green')

							

							#my_response[2]['message'] = f"non anonymised sql query: (clamp min/max are not applied)<br><br><p style = 'font-family:sans-serif,georgia,garamond,serif;margin:.5em;padding:.5em;background-Color:rgba(0,0,0,.1);'>{query_str.replace('FROM', '<br>FROM').replace('WHERE', '<br>WHERE').replace('GROUP BY', '<br>GROUP BY')}</p>"
							my_response['message'] = f"non anonymised sql query: (clamp min/max are not applied)<br><br><p style = 'font-family:sans-serif,georgia,garamond,serif;margin:.5em;padding:.5em;background-Color:rgba(0,0,0,.1);'>{query_str.replace('FROM', '<br>FROM').replace('WHERE', '<br>WHERE').replace('GROUP BY', '<br>GROUP BY')}</p>"
							

							result_non_anonymised = execute_sql_request_without_anonymisation(
								my_spark_session,
								spark_dataframe,
								src['tumult_source_id'],
								query_str
							)

							prt(f'{result_non_anonymised=}')
							#prt(f'{result_non_anonymised.show(n=result_non_anonymised.count())=}')

							result_non_anonymised_file_path = result_file_path[:-len('.csv')] + '_non_anonymised.csv'

							result_non_anonymised.toPandas().to_csv(result_non_anonymised_file_path, sep=';', index = False)

							my_response['subs'].append(
								{
									'type':'path',
									'expanded': True,
									'path': 'file://'+result_non_anonymised_file_path,
									'must_be_removed_on_reload': True,
								}
							)


							# calculate the difference
							try:
								if result != None:

									if result.count() == result_non_anonymised.count():

										def calculate_the_difference_between_two_columns(
											key_column_name,
											spark_dataframe_1, column_name_1,
											spark_dataframe_2, column_name_2,
										):
											# select t1.key, t1.val1- t2.val2 from t1, t2 where t1.key == t2.key

											df1 = spark_dataframe_1.alias('df1')
											df2 = spark_dataframe_2.alias('df2')

											diff_expr = pyspark.sql.functions.col('df1.' + column_name_1) - pyspark.sql.functions.col('df2.' + column_name_2)

											if key_column_name != None:
												return df1.join(
													df2,
													pyspark.sql.functions.col('df1.'+key_column_name) == pyspark.sql.functions.col('df2.'+key_column_name)
												).select('df1.' + key_column_name, diff_expr)

											else:
												return df1.join(df2).select(diff_expr)
										
										
										difference = calculate_the_difference_between_two_columns(
											result.schema.names[0] if len(result.schema.names) > 1 else None,
											result, result.schema.names[-1],
											result_non_anonymised, result_non_anonymised.schema.names[-1],
										)

										difference_path = result_file_path[:-len('.csv')] + '_difference_anonymised_minus_non_anonymised.csv'

										difference.toPandas().to_csv(difference_path, sep=';', index = False)

										my_response['subs'].append(
											{
												'type':'path',
												'expanded': True,
												'path': 'file://'+difference_path,
												'must_be_removed_on_reload': True,
											}
										)

									else:
										my_response['subs'].append(
											{
												'type':'error',
												'title':f'error during difference calculation: anonymised result and non anonymised result have different length',
												'expanded': False,
												'exception':'',
												'traceback':'',
												'must_be_removed_on_reload': True,
											}
										)

							except BaseException as exception:
								my_response['subs'].append(
									{
										'type':'error',
										'title':f'failed to calculate the différence between anonymised result and non anonymised result',
										'expanded': False,
										'exception':str(exception),
										'traceback':traceback.format_exc(),
										'must_be_removed_on_reload': True,
									}
								)


						
						except BaseException as exception:
							prt(traceback.format_exc(), color = 'red')
							prt('-----------------------------------------')
							prt(exception, color = 'red')
							#my_response[2]['subs'].append(
							my_response['subs'].append(
								{
									'type':'error',
									'title':f'non anonymised request failed (if you don\'t care about the non-anonymised result, this error does not matter).',
									'expanded': False,
									'exception':str(exception),
									'traceback':traceback.format_exc(),
									'must_be_removed_on_reload': True,
								}
							)


						


						

						#if len(request['columns']) > 0:

						#	result_column_name = request['columns'][0]+'_'+request['function']

						#	sns.set_theme(style="whitegrid")
						#	g = sns.barplot(
								#x = "education_level",
						#		x = request['columns'][0],
								#y = "age_average",
						#		y = result_column_name,
								#data = edu_average_ages.toPandas().sort_values("age_average"),
						#		data = result.toPandas().sort_values(result_column_name),
						#		color = "#1f77b4",
						#	)
						#	g.set_xticklabels(g.get_xticklabels(), rotation=45, horizontalalignment="right")
						#	plt.title("Average age of library members, by education level")
						#	plt.xlabel("Education level")
						#	plt.ylabel("Average age")
						#	plt.tight_layout()
						#	plt.show()

						#	result.sort(result_column_name).show(truncate=False)


					except BaseException as exception:
						prt(traceback.format_exc(), color = 'red')
						prt('-----------------------------------------')
						prt(exception, color = 'red')
						response.append(
							(
								csv_list.index(src),
								src['requests'].index(request),
								{
									'type':'error',
									'expanded': False,
									'exception':str(exception),
									'traceback':traceback.format_exc(),
									'must_be_removed_on_reload': True,
								}
							)
						)
					finally:
						response.append(more_response_indexed)

				# free ram memory
				del spark_dataframes[src['tumult_source_id']]

	#prt(f'{response=}')

	return response



import shutil
import os

def clear_result_folder():

	#https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder
	folder = './data/result'

	
	for filename in os.listdir(folder):

		file_path = os.path.join(folder, filename)

		try:
			if os.path.isfile(file_path) or os.path.islink(file_path):

				os.unlink(file_path)

			elif os.path.isdir(file_path):
				shutil.rmtree(file_path)
				

			#elif os.path.isdir(file_path):
			#	shutil.rmtree(file_path)

		except BaseException as e:

			print('Failed to delete %s. Reason: %s' % (file_path, e))


	class Element:

		def __init__(me, sup, key, e):
			me.sup = sup
			me.key = key
			me.e = e

		def remove(me):
			if me.sup != None:
				if isinstance(me.sup, dict):
					del me.sup[me.key]
				elif isinstance(me.sup, list):
					me.sup.remove(me.e) # the index may not be valid anymore if the list is modified



	def iterate_all_dictionaries_recursively(elm, f):

		e = elm.e

		if isinstance(e, list):
			key = 0
			for u in e:
				iterate_all_dictionaries_recursively(Element(sup=e, key=None, e=u), f)
				key += 1
			
		elif isinstance(e, dict):
			f(elm)
			for key, u in e.items():
				iterate_all_dictionaries_recursively(Element(sup=e, key=key, e=u), f)

	elements_to_remove = []

	def remove_if_must_be_removed_on_reload(e):

		if e.e.get('must_be_removed_on_reload', False):
			elements_to_remove.append(e)
			
	iterate_all_dictionaries_recursively(Element(sup=None, key=None, e=json_global), remove_if_must_be_removed_on_reload)

	for e in elements_to_remove: # must be done at the end
		e.remove()
	

	# retirer les résultat qui pointent vers un fichier qui est supprimé
	#for elm in json_global['elms']:
	#	for request in elm['requests']:
	#		for response in (responses := request['responses']):
	#			if response['type'] in ['path', 'privacy budget used']:
	#				responses.remove(response)

	json_global.save()






#import BaseHTTPServer
#import CGIHTTPServer
import http.server
#from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, HTTPServer
import time
import cgi
import codecs
import csv
import io
import json

#import equests_toolbelt.multipart

hostName = "127.0.0.1"
serverPort = 8080










class columns_of_query_json(list):


	def __init__(self, query_json_ins):
		assert isinstance(query_json_ins, query_json)
		self.csv_json = query_json_ins.csv_json
		self.query_json = query_json_ins


	def put(self, column):
		with prt(f'put "{column}" in query columns', color = 'blue'):
			if column not in self:
				list.append(self, column)
				self.update()
			prt('columns =', self, color = 'blue')
			self.query_json.on_columns_modified()


	def remove(self, column):
		with prt(f'remove "{column}" in query columns', color = 'blue'):
			if column in self:
				if len(self) > tumult_functions[self.query_json['function']]['nb_columns_min']:
					list.remove(self, column)
			prt('columns =', self, color = 'blue')
			self.query_json.on_columns_modified()


	def set(self, queries):
		with prt(f'columns_of_query_json.set({queries=})', color = 'blue'):
			self[:] = queries
			self.query_json.on_columns_modified()
		return self


	def update(self):

		with prt(f'update columns', color = 'blue'):

			# remove non existing column
			for non_existing_column in set(self) - set(self.csv_json['header']):
				self.remove(non_existing_column)

			nb_columns_max = tumult_functions[self.query_json['function']]['nb_columns_max']
			nb_columns_min = tumult_functions[self.query_json['function']]['nb_columns_min']

			# remove duplicates
			for i in reversed(range(len(self))):
				try:
					j = self.index(self[i], 0, i) # raise an exception if not in
					del self[j]
				except:
					pass

			# remove excess columns
			del self[:-min(nb_columns_max, len(self)) if nb_columns_max != 0 else len(self)]
			
			# add columns
			if len(self) < nb_columns_min:

				# columns that can be added
				columns = set(self.csv_json['header']) - set(self)

				# order columns that can be added in the same order as self.csv_json.header
				columns = [column for column in self.csv_json['header'] if column in columns]

				# add the correct number of columns
				for column in islice(columns, nb_columns_min - len(self)):
					list.append(self, column)

			self.query_json.on_columns_modified()

					



class query_json(dict):


	def __init__(self, csv_data):

		assert isinstance(csv_data, csv_json)

		self.csv_json = csv_data

		dict.__init__(self, {
			'group_by': {
				#'enabled': False,
				#'enabled_prev': True,
				#'column': header[0] if header else '',
				'column': None,
			},
			'function': 'count',
			'function_infos': copy.deepcopy(tumult_functions['count']),
			'columns': columns_of_query_json(self),
			'clamp_range': None,
			'clamp_range_prev': None,
			'quantile': None,
			'quantile_prev': None,
			'make_result_positive': tumult_functions['count']['positive_result_default_value'],
			'make_result_positive_set_by_user': False,
			'budget_privacy_ponderation': 1,
			'filter': None,
			'more_options_expanded': False,
			'responses': [],
		})

		


	def set(self, json):
		for key in list(self):
			if key in json:
				if key == 'columns':
					self[key] = columns_of_query_json(self).set(json[key])
				else:
					self[key] = copy.deepcopy(json[key])
		return self


	def __setitem__(self, key, value):

		with prt(f'modify query: query[{key}] from <{self[key]}> to <{value}>', color = 'yellow'):

			if key == 'make_result_positive':
				self['make_result_positive_set_by_user'] = value

			if key == 'function':

				if value not in tumult_functions:
					return # non existing function
				
				# if make_result_positive default value for this function is false give the value set bey the user
				# using dict.__setitem__ to not call query_json.__setitem__ that sets positive_result_default_value
				dict.__setitem__(
					self,
					'make_result_positive',
					True if tumult_functions[value]['positive_result_default_value'] else self['make_result_positive_set_by_user']
				)
				
				if value in ('count', 'count_distinct'):

					# count and count_distinct don't have clamp range
					if self['clamp_range'] != None:
						self['clamp_range_prev'] = self['clamp_range']
						self['clamp_range'] = None

					
					#if self['function'] not in ('count', 'count_distinct'):
						# save previous value for other functions (other than count and count_distinct)
						#self['group_by']['enabled_prev'] = self['group_by']['enabled']

					# doesn't make sense to group with count and count_distinct
					#self['group_by']['enabled'] = False

				else:

					# all the function other than count and count_distinct have clamp range
					if self['clamp_range'] == None:
						if self['clamp_range_prev'] == None:
							#self['clamp_range'] = [0, 500]

							

							#self['clamp_range'] = self.get_min_max_pair()
							self['clamp_range'] = [0, 500]

						else:
							self['clamp_range'] = self['clamp_range_prev']
					
					#if self['function'] in ('count', 'count_distinct'):
						# restore previous value
						#self['group_by']['enabled'] = self['group_by']['enabled_prev']


				if value == 'quantile':
					if self['quantile'] == None:
						# save previous quatile
						if self['quantile_prev'] == None:
							self['quantile_prev'] = 0

						self['quantile'] = self['quantile_prev']

				if value != 'quantile' and self['function'] == 'quantile':
					self['quantile_prev'] = self['quantile']
					self['quantile'] = None
						
			if key == 'columns':
				# convert to columns_of_query_json if not an instance of that type
				if not isinstance(value, columns_of_query_json):
					value = columns_of_query_json(self).set(value)
					value.csv_json = self.csv_json
					value.csv_query = self.csv_query
					

		
			dict.__setitem__(self, key, value)


			# updates
			if key == 'function':
				self['columns'].update()
				self['function_infos'] = copy.deepcopy(tumult_functions[value])

			if key == 'columns':

				#print('AAAAAAAAAAAAAAAAAAAEEEEEEEEEEEEEEEEEEEEEEEEEEEEE') 

				self['columns'].update()

				#print('AAAAAAAAAAAAAAAAAAA get_min_max_pair', self.csv_json['src']['path'])
				


	def on_columns_modified(self):
		pass
		if self.csv_json['src']['path'] != None:
			#print(f'{self.get_min_max_pair()=}')
			self['clamp_range'] = self.get_min_max_pair()
			#print(f'{self["clamp_range"]=}')


	def get_min_max_pair(self):

		try:
			df = self.csv_json['src'].get_pandas_data_frame()
		except:
			prt(f"failed to determine the min/max pair for the csv file [{self.csv_json['src']['path']}], maybe the separation token was incorrect and the user will simply change it to the correct separation token", color = 'red')
			return [-3000, 3000]

		mini = float('inf')
		maxi = float('-inf')

		for column_name in self['columns']:

			column_values = df[column_name]
			#print(f'{column_name=}')
			#print(f'{column_values=}')
			#mini_av = mini
			#maxi_av = maxi

			try:
				mini = min(mini, column_values.min())
				maxi = max(maxi, column_values.max())
			except:
				#mini = mini_av
				mini = 0
				#maxi = maxi_av
				maxi = 0
				break

		return [
			float(mini if mini != float('inf') else -3000),
			float(maxi if maxi != float('-inf') else 3000),
		]
				



class csv_src_json(dict):

	def __init__(self, csv_data):

		assert isinstance(csv_data, csv_json)

		dict.__init__(self, {
			'txt': None,
			'path': None,
			'delimiter': None,
		})
	
		self.csv_data = csv_data


	def get_pandas_data_frame(self):
		return pd.read_csv(
			self['path'],
			delimiter= self['delimiter']
		)


	def __setitem__(self, key, value):
		
		dict.__setitem__(self, key, value)

		if key == 'delimiter':
			self.csv_data.update_header()

		elif key == 'path':
			self.csv_data.update_tumult_source_id_from_src_path()


	def set(self, dict):
		for key in list(self):
			if key in dict:
				self[key] = dict[key]
		return self




class csv_json(dict):

	def __init__(self):

		with prt('csv_json.__init__', color = 'green'):

			dict.__init__(self, {
				'type': 'csv',
				'header': None,
				'private': True,
				'tumult_source_id': None,
				#'src': csv_src_json({
				#	'txt': None,
				#	'path': None,
				#	'delimiter': None,
				#}),
				'src': csv_src_json(self),
				'requests': [],
				'responses': [],
				'sample': {
					'random': {
						'percent': 100,
						'responses': [],
					},
					'result': {},
					'expanded': False,
					'remove_lines_with_null_or_NaN_cells': {
						'columns': [],
						'responses': [],
					},
					'trim': {
						'min': {
							'percent': 0,
							'columns': [],
							'responses': [],
						},
						'max': {
							'percent': 0,
							'columns': [],
							'responses': [],
						},
						'responses': [],
					},
					'interquartile_range': {
						'columns': [],
						'responses': [],
					},
					'standard_deviation': {
						'columns': [],
						'responses': [],
					},
				},
			})


	def update_tumult_source_id_from_src_path(self):
		
		with prt('update_tumult_source_id_from_src_path', color = 'yellow'):

			prt(f'{self=}', color = 'yellow')

			if name := self['src']['path']:

				name = pathlib.Path(name).name					

				self['tumult_source_id'] = normalize_name(name, retirer_les_accents = False, to_lower_case = False)


	def set(self, json):

		with prt('csv_json.set', color = 'green'):

			#if 'src' in json:
			#	self['src'] = json['src']

			for key in list(self):
				if key in json and key != 'src':
						self[key] = copy.deepcopy(json[key])

			if 'src' in json:
				self['src'] = json['src']# à la fin pour set tumult_source_id sans être overridé par dict
			

		return self
		

	def update_header(self):

		with prt(f'update_header', color = 'blue'):
			
			if self['src']['txt'] != None:

				rows = csv.reader(
					io.StringIO(self['src']['txt']),
					delimiter = self['src']['delimiter']
				)

				self['header'] = next(rows)

			elif self['src']['path'] != None:

				with open(self['src']['path'], 'r') as f:
					rows = csv.reader(
						f,
						delimiter = self['src']['delimiter']
					)

					self['header'] = next(rows)

			prt('update_header =', self['header'], color = 'blue')


	def add_request(self):
		header = self['header']
		query = query_json(self)
		query.csv_json = self
		query['columns'].query_json = query
		query['columns'].csv_json = self
		query['columns'].update()
		self['requests'].append(query)
		return self['requests'][-1]


	def __setitem__(self, key, value):

		if key == 'src':
			if not isinstance(value, csv_src_json):
				value = csv_src_json(self).set(copy.deepcopy(value))

		elif key == 'requests':
			prt('value = '+str(value))
			value2 = []
			for query in value:
				value2.append(query_json(self).set(query))
			value = value2

			prt('value2 = '+str(value2))
			#assert False
			#if not isinstance(value, query_json):
			#	value = csv_src_json(self).set(copy.deepcopy(value))

		dict.__setitem__(self, key, value)

		if key == 'src':
			self.update_header()
			self.update_tumult_source_id_from_src_path()


	#def set_src(self, src):

	#	with prt(f'csv_json.set_src', color = 'blue'):

	#		if not isinstance(src, csv_src_json):
	#			src = csv_src_json(self).set(copy.deepcopy(src))

	#		self['src'] = src

			#self['src'].csv_data = self
			







class element_list_json(list):


	def __init__(self):
		list.__init__(self)
		#self.load_from_file()


	def read_all_csv(self, dir):
		with prt(f'read_all_csv at {dir}'):
			for f in os.listdir(os.fsencode(dir)):
				filename = os.fsdecode(f)
				if filename.endswith(".csv"): 
					#if self.add_from_csv_file(dir, filename):
					if self.add_from_csv_file(dir + filename):
						self[-1].add_request()


	#def add_from_csv_file(self, dir, filename, delimiter = ';'):
	def add_from_csv_file(self, path, delimiter = ';'):

		#with prt(f'csv_list.add_from_csv_file {repr(filename)}', color = 'magenta'):
		with prt(f'csv_list.add_from_csv_file {repr(path)}', color = 'magenta'):

			elm = csv_json()

			elm['src'] = {
				#'path':  dir + filename,
				'path':  path,
				'delimiter': delimiter
			}

			for e in self:
				if e['type'] == 'csv' and e['tumult_source_id'] == elm['tumult_source_id']:
					prt('element with tumult_source_id='+elm['tumult_source_id']+' already in list', color = 'green')
					return False# dont append elm

			self.append(elm)

			elm.add_request()

			return True


	def add_from_csv_txt(self, name, csv_txt, delimiter = ';'):
		
		with prt(f'csv_list.add_from_csv_txt {repr(name)}', color = 'magenta'):
			
			self.add_from_header(name, [])

			elm = csv_json()
			
			elm['src'] = {
				'txt': csv_txt,
				'delimiter': delimiter
			}

			for e in self:
				if e['type'] == 'csv' and e['tumult_source_id'] == elm['tumult_source_id']:
					prt('element with tumult_source_id='+elm['tumult_source_id']+' already in list', color = 'green')
					return False# dont append elm

			self.append(elm)
			return True


	#def load_from_file(self, path = './data/source/'):
	#	with prt(f'element_list_json.load_from_file {path=}', color = 'yellow'):
	#		
	#		try:
	#			if True:
	#				persist_filename = path+'persist.json' 
	#				if os.path.isfile(persist_filename):
	#					with open(path+'persist.json', 'r') as f:
	#						for e in json.load(f):
	#							new_csv_data = csv_json()
	#							new_csv_data.set(e)
	#							self.append(new_csv_data)
	#		except BaseException as ex:
	#			prt('failed to load json', color = 'red')
	#			prt('-----------------')
	#			prt(ex, color = 'red')
	#			prt('-----------------')
	#			prt(traceback.format_exc(), color = 'red')
	#			prt('-----------------')
	#
	#		self.read_all_csv(path)

	def set(self, list):
		for e in list:
			new_csv_data = csv_json()
			new_csv_data.set(e)
			self.append(new_csv_data)
		return self



	#def save(self):
	#	with open('./data/persist.json', 'w') as f:
	#		json.dump(self, f, indent=4)




class Json_global(dict):

	def __init__(self):
		dict.__init__(self)
		self['elms'] = element_list_json()
		self.load_from_file()

	def save(self):
		with open('./data/persist.json', 'w') as f:
			json.dump(self, f, indent=4)

	def load_from_file(self, path = './data/'):
		with prt(f'element_list_json.load_from_file {path=}', color = 'yellow'):
			
			try:
				persist_filename = path+'persist.json'

				# create empty file doesn't exist
				if not os.path.isfile(persist_filename):
					with open(persist_filename, 'a'):
						pass
				
				with open(path+'persist.json', 'r+') as f:
					try:
						data = json.load(f)
					except:
						prt('erreur lecture du json du fichier "data/persist.json"', color = 'red')
						data = dict()
					self['scroll_x'] = data.get('scroll_x', 0)
					self['scroll_y'] = data.get('scroll_y', 0)

					# privacy_budget:
					# valeurs protyectrices: 10**-3, 10**-2, 10**-1
					# valeur ok: 1 à 5
					# valeurs non protectrices: 10 et plus

					self['privacy_budget'] = data.get('privacy_budget', 10**-1)
					self['elms'].set(data.get('elms', []))
					self['elms'].read_all_csv('./data/source/')

			except BaseException as ex:
				prt('failed to load json', color = 'red')
				prt('-----------------')
				prt(ex, color = 'red')
				prt('-----------------')
				prt(traceback.format_exc(), color = 'red')
				prt('-----------------')




json_global = Json_global()

csv_list = json_global['elms']

import easygui # for easygui.fileopenbox()

#import tkinter
#from tkinter import filedialog
#tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing
#folder_path = filedialog.askdirectory()
#folder_path = filedialog.askopenfilename()



from pathlib import Path




def remove_prefix(s, prefix):
	#return Path(__file__).anchor + s[len(prefix):] if s.startswith(prefix) else s
	#return 'C:' + s[len(prefix):] if s.startswith(prefix) else s
	return s[len(prefix):] if s.startswith(prefix) else s

def remove_suffix(s, suffix):
	return s[:-len(suffix)] if s.endswith(suffix) else s


def see_3D(path):

	with prt('see_3D', f'{path=}'):

		for_url = f'data/result/{Path(path).stem}_3D.html'

		dst = f'../../{for_url}'
		
		json_conf = json.dumps({
			'src': {
				'path': remove_prefix(path, 'file://'),
				#'path': str(Path(path).resolve()),
				'delemiter': ';',
			},
			'dst': dst
		})

		json_conf = json_conf.replace('"','\\"')

		#commande = f'((echo "{json_conf}" | python3 convert_csv_to_html_pie_chart.py) && (chromium {dst})) &'
		commande = f'(echo "{json_conf}" | python3 convert_csv_to_html_pie_chart.py)'

		commande = f'(cd 3d/convert_csv_to_html_pie_chart/ ;({commande}))'

		prt('commande =', commande)

		os.system(commande)

		return for_url



class ctx_add_sys_path:

	def __init__(me, path):
		me.path = path
		

	def __enter__(me):
		sys.path.append(me.path)
	
	def __exit__(me, *args):
		sys.path.remove(me.path)




def see_2D_pie(path):

	with prt('see_2D_pie', f'{path=}'):

		path = remove_prefix(path, 'file://')
		file_path = 'data/result/'+Path(path).stem+'_2D_pie.html'

		df = pd.read_csv(
			path,
			index_col=False,
			sep=';'
		)

		with ctx_add_sys_path('plot_2D_with_bokeh/'):

			import make_html_pie

			with open(file_path, 'w') as f:
				f.write(
					make_html_pie.html_of_pie(
						data_frame = df,
						#x = {
						#	df.iloc[k,0]: int(df.iloc[k, 1]) for k in range(len(df))
						#},
						args_figure = {
							'title': Path(path).stem.replace('_csv_','_').replace('_', ' ')
						},
						args_wedge = dict()
					)
				)

		#os.system(f'chromium "{file_path}" &')

		return file_path






def see_2D_bars(path):

	with prt('see_2D_bars', f'{path=}'):

		path = remove_prefix(path, 'file://')
		file_path = 'data/result/'+Path(path).stem+'_2D_bars.html'

		df = pd.read_csv(
			path,
			index_col=False,
			sep=';'
		)

		with ctx_add_sys_path('plot_2D_with_bokeh/'):

			import make_html_bars

			with open(file_path, 'w') as f:
				f.write(
					make_html_bars.html_of_bars(
						data_frame = df,
						#x = {
						#	df.iloc[k,0]: int(df.iloc[k, 1]) for k in range(len(df))
						#},
						args_figure = {
							'title': Path(path).stem.replace('_csv_','_').replace('_', ' ')
						},
						args_vbar = dict()
					)
				)

		os.system(f'chromium "{file_path}" &')

		return file_path




import urllib.parse


#class MyServer(http.server.BaseHTTPRequestHandler):
class MyServer(http.server.SimpleHTTPRequestHandler):
	def do_GET(self):
		with prt('do_GET', color = 'green'):
			
			path = urllib.parse.unquote(self.path) # retire les % causé par les espaces et les accents

			prt(self.path, '->', path)
			if self.path == f"/tout":
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				
				with Html() as html:
					with block('html'):
						with block('head'):
							with block('title'):
								html += 'anonymiser des csv'
						#with block('p'):
						#	html += "Request: %s" % self.path
				self.wfile.write(bytes(html.s, "utf-8"))


				with open('result2.html','r') as f:
					self.wfile.write(bytes(f.read(), "utf-8"))

			elif self.path == '/all_csv':
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				#output = json.dumps([{k:v for k,v in csv.items() if k != 'txt'} for csv in csv_list])
				
				# if the file is dropped on the web page, the source is a text and we don't want to resend the entire text of the data base each time
				get_all_src_csv = lambda: filter(lambda e: e['type'] == 'csv', csv_list)
				src_txt = [e['src']['txt'] for e in get_all_src_csv()] # save
				for e in get_all_src_csv(): e['src']['txt'] = None # remove

				output = json.dumps(json_global)

				for e, txt in zip(get_all_src_csv(), src_txt): e['src']['txt'] = txt # restore

				self.wfile.write(output.encode(encoding = "utf_8"))

			#o = urllib.parse.urlparse(self.path)
			#prt(o, color = 'red')
			#breakpoint()

			elif Path(path).suffix == '.html' and path.startswith('/data/result/') and '\r' not in path and '..' not in path:
				# ajouté car demandé de servir les résultats
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				with open(f'.{path}','r') as f:
					self.wfile.write(bytes(f.read(), "utf-8"))
				

	def do_DELETE(self):
		with prt('do_DELETE', color = 'green'):
			self.send_response(200)
			self.send_header('Content-type', 'application/json; charset=utf-16')
			self.end_headers()
			ctype, pdict = cgi.parse_header(self.headers['Content-Type'])

			if ctype == 'multipart/form-data':
				pdict['boundary'] = bytes(pdict['boundary'], 'utf-16')
				fields = cgi.parse_multipart(self.rfile, pdict)
				prt('DELETE fields =', fields)
				if 'index' in fields:
					try:
						del csv_list[int(fields['index'][0])]
					except:
						prt("can't 'del csv_list[int(fields['index'][0])]'", color = 'red')
						assert False
				
				for csv_key, query_key in map(json.loads, fields.get('delete_query',[])):
					del csv_list[csv_key]['requests'][query_key]
				
			else:
				assert False


	def do_POST(self):
		with prt('do_POST', color = 'green'):

			global csv_list

			self.send_response(200)
			self.send_header('Content-type', 'application/json')
			self.end_headers()

			ctype, pdict = cgi.parse_header(self.headers['Content-Type'])

			prt('type =', ctype, color = 'cyan')
			prt('data =', pdict, color = 'cyan')

			output = ''

			if ctype == 'multipart/form-data':
				pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
				fields = cgi.parse_multipart(self.rfile, pdict)
				prt('fields =', fields, color = 'cyan')

				for csv in fields.get('new csv',[]):
					csv = json.loads(csv)
					csv_list.add_from_csv_txt(csv['filename'], csv['txt'])

				for params in map(json.loads, fields.get('start_tumult_session',[])):

					# remove all csv_result from csv_list
					#for i in reversed(range(len(csv_list))):
					#	if csv_list[i]['type'] == 'csv_result':
					#		del csv_list[i]

					for csv in csv_list:
						#csv['response'] = []
						del csv['responses'][:]
						for query in csv['requests']:
							#query['response'] = []
							del query['responses'][:]

					for csv_key, query_key, response in start_tumult_session():
						#prt(f'{response=}')

						if csv_key != None and query_key != None:
							csv_list[csv_key]['requests'][query_key]['responses'].append(response)

						if csv_key != None and query_key == None:
							csv_list[csv_key]['responses'].append(response)
					#prt(csv_list, color = 'green')

						#csv_list.append({
						#	'type': 'csv_result',
						#	'name': repr(response),
						#})

					


				for updates in fields.get('set',[]):

					for path, val in json.loads(updates):

						d = json_global

						for i in range(len(path)):
							
							# check if you can advance in the path
							is_list_key = isinstance(d, list) and (0 <= path[i] <= len(d))
							is_dict_key = isinstance(d, dict) and path[i] in d
							if not is_list_key and not is_dict_key:
								prt('error path (',path,f') does not exist, ({path[i]} is not a key of {d})', color = 'red')
								break # dictionary path does not exist: cancel

							prt('path[i] = ', path[i], color = 'green')

							if i == len(path)-1:
								with prt('set value: (', path,' = ', repr(val), ')', color = 'green'):
									d[path[-1]] = val# set the value
							else:
								d = d[path[i]]# advance in path
				
				for csv_key in map(json.loads, fields.get('add_query',[])):
					csv_list[csv_key].add_request()

				for (csv_key, query_key), column_name in map(json.loads, fields.get('add_column',[])):
					csv_list[csv_key]['requests'][query_key]['columns'].put(column_name)
				
				for (csv_key, query_key), column_name in map(json.loads, fields.get('remove_column',[])):
					csv_list[csv_key]['requests'][query_key]['columns'].remove(column_name)


				for path_to_list, new_element in map(json.loads, fields.get('add_element_to_list',[])):

					with prt(f'add_element_to_list: {path_to_list=}, {new_element=}', color = 'green'):

						list_to_modify = json_global

						for key in path_to_list:
							list_to_modify = list_to_modify[key]

						list_to_modify.append(new_element)



				for path_to_list, element in map(json.loads, fields.get('remove_element_from_list',[])):

					with prt(f'remove_element_from_list: {path_to_list=}, {element=}', color = 'green'):

						list_to_modify = json_global

						for key in path_to_list:
							list_to_modify = list_to_modify[key]

						list_to_modify.remove(element)



				for path in map(json.loads, fields.get('open_in_file_explorer',[])):
					if path.startswith('file://'):
						path = path[len('file://'):]
					open_folder(str(pathlib.Path(path)))

				for _ in map(json.loads, fields.get('open_result_folder',[])):
					open_folder('./data/result/')
					

				for files in map(json.loads, fields.get('select_new_csv_files',[])):

					if file := easygui.fileopenbox(filetypes='*.csv'):
						prt(file)
						json_global['elms'].add_from_csv_file(file)
					else:
						prt('no file selected')
					#for file in files:
					#	with prt(f'open file {file}'):
					#		json_global['elms'].add_from_csv_file(file)
						#prt('non implémenté', color = 'red')

				for path in map(json.loads, fields.get('see_3D',[])):

					with prt('post see_3D', color = 'green'):
						output += json.dumps({'new_tab_url':see_3D(path)})

				for path in map(json.loads, fields.get('see_2D_pie',[])):

					with prt('post see_2D_pie', color = 'green'):
						output += json.dumps({'new_tab_url':see_2D_pie(path)})
						

				for path in map(json.loads, fields.get('see_2D_bars',[])):

					with prt('post see_2D_bars', color = 'green'):
						output += json.dumps({'new_tab_url':see_2D_bars(path)})
						

				for path in map(json.loads, fields.get('quit',[])):

					with prt('post quit', color = 'green'):

						clear_result_folder()

						#sys.exit(0)

					
					
			

			#all_csv_headers_list = []
			#for e in csv_list:
			#	all_csv_headers_list.append(e.header)

			
			#output = json.dumps(all_csv_headers_list)
			#print('output =', output.encode(encoding = "utf_8"))

			self.wfile.write(output.encode(encoding = "utf_8"))

			json_global.save()
			#print (output)


# clear results when application.py closes for data privacy.
# the user must copy the result before closing the application
#import signal
#import sys
#
#def signal_handler(signal, frame):
#	print('You pressed Ctrl+C - or killed me with -2')
#	#.... Put your logic here .....
#	sys.exit(0)
#for sig in (signal.SIGINT, signal.SIGHUP, signal.SIGTERM, signal.SIGSEGV, signal.SIGFPE):
#	signal.signal(sig, signal_handler)



if __name__ == "__main__":

	

	webServer = http.server.HTTPServer((hostName, serverPort), MyServer)

	#webServer.socket.setsockopt(webServer.socket.SOL_SOCKET, webServer.socket.SO_REUSEADDR, 1)
	#webServer.socket.TCPServer.allow_reuse_address = True

	prt("Server started at http://%s:%s" % (hostName, serverPort))



	try:
		webServer.serve_forever()
	except KeyboardInterrupt:
		pass

	clear_result_folder()

	webServer.socket.close()
	webServer.server_close()
	prt("Server stopped.")
