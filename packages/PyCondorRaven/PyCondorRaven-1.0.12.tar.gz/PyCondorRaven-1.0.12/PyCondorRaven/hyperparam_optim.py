import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from timeit import default_timer as timer
import datetime as dt
from dateutil.relativedelta import relativedelta
import os, re, csv, joblib, json, io
from scipy import stats
from PyCondorInvestmentAnalytics.utils import extract_data_s3select

def objective(params, id_model, values, scaler, n_features, n_series, lr, verbosity, model_file_name, MAX_EVALS, returns, train_size, test_size, val_size, dir='', error_type="mse", **other_params):
    """
    	Función objetivo que sirve para la optimización bayesiana, sirve para ejecutar el modelo con los parámetros recibidos, calcular el error de esta ejecución y así decidir
    	cuales parámetros son mejores.

    	Parámetros:
    	- params -- Diccionario, contien los parametros para la ejecución, estos parámetros son dados por la libreria de optimización bayesiana (bayes_opt) dentro de un espacio previamente definido
    	- id_model -- Entero, id del modelo que se va a entrenar
    	- values -- Arreglo de numpy, datos con los cuales se va a entrenar el modelo, es decir, la serie previamente preprocesada
    	- scaler -- Instancia de la clase MinMaxScaler de sklearn, sirve para el escalamiento de los datos y para revertir este escalamiento
    	- n_features -- Entero, número de *features* de la serie
    	- n_series -- Entero, número de *time steps*
    	- verbosity -- Entero, nivel de verbosidad de la ejecución
    	- model_file_name -- String, nombre del archivo donde se guardará y/o se cargará el modelo entrenado
    	- MAX_EVALS -- Entero, número máximo  de iteraciones de la optimización bayesiana, en esta función sirve para identificar el archivo de los logs

    	Retorna:
    	- [valor] -- Flotante, dicconario que retorna la "recompensa" de esta ejecución, la idea es maximizarla, por eso el "error" de la ejecución se invierte

    """
    # Keep track of evals
    global ITERATION
    from . import models

    ITERATION += 1
    out_file = dir + 'trials/gbm_trials_' + ID_TO_MODELNAME[id_model] + '_' + str(MAX_EVALS) + '.csv'
    # print(ITERATION, params)

    calc_val_error = True
    calc_test_error = True
    if(id_model == 0):
        if(model_file_name == None):
            model_file_name = dir + 'models/trials-lstm.h5'

		# Make sure parameters that need to be integers are integers
        for parameter_name in ['n_lags', 'n_epochs', 'batch_size', 'n_hidden', 'n_dense', 'n_rnn', 'activation']:
            params[parameter_name] = int(params[parameter_name])

        start = timer()
        data_train, data_test, data_val, time_train, time_test, time_val = transform_values(values, params['n_lags'], n_series, True, train_size, test_size, val_size, params['batch_size'])
        rmse, rmse_val, _, _, val_y, y_hat_val, dir_acc, _, _ = models.model_lstm(data_train, data_test, data_val, n_series, lr, params['n_epochs'], params['batch_size'], params['n_hidden'], n_features,params['n_lags'], scaler, calc_val_error, calc_test_error, verbosity, False, model_file_name, params['n_rnn'], params['n_dense'], params['activation'], other_params.get('output_activation', None), params['drop_p'], returns, error_type=error_type)
        if(returns):
        	# mean = np.mean(np.abs(val_y))
        	# std = np.std(val_y)
        	print('rmse:', rmse_val) #, 'std: ', np.std(y_hat_val))
        	# print('mean: ', mean, 'std_y: ', std)
        	# print('inputs -> error: ', np.abs(rmse_val-mean)/mean, 'deviation: ', (np.abs(std-np.std(y_hat_val)))/std)
        	rmse = rmse_val #np.abs(rmse_val-mean)/mean + (np.abs(std-np.std(y_hat_val)))/std
        else:
        	mean = np.mean(np.abs(val_y))
        	rmse = rmse_val/mean + (1 - dir_acc)
        run_time = timer() - start
		# print('no_score: ', rmse)
		# print('time: ', run_time, end='\n\n')
    elif(id_model == 1):
    	if(model_file_name == None): model_file_name = dir + 'models/trials-randomForest.joblib'

    	# Make sure parameters that need to be integers are integers
    	for parameter_name in ['n_lags', 'n_estimators', 'max_features', 'min_samples']:
    		params[parameter_name] = int(params[parameter_name])

    	start = timer()
    	train_X, test_X, val_X, train_y, test_y, val_y = transform_values(values, params['n_lags'], n_series, 0, train_size, test_size, val_size)
    	rmse, rmse_val, _, _, _, _, _, dir_acc, _, _ = models.model_random_forest(train_X, test_X, val_X, train_y, test_y, val_y, n_series, params['n_estimators'], params['max_features'], params['min_samples'],
    															n_features, params['n_lags'], scaler, calc_val_error, calc_test_error, verbosity, False, model_file_name, returns)
    	if(returns):
    		rmse = rmse_val
    	else:
    		mean = np.mean(np.abs(val_y))
    		rmse = rmse_val/mean + (1 - dir_acc)
    	run_time = timer() - start
    	# print('no_score: ', rmse)
    	# print('time: ', run_time, end='\n\n')
    elif(id_model == 2):
    	if(model_file_name == None): model_file_name = dir + 'models/trials-adaBoost.joblib'
    	# Make sure parameters that need to be integers are integers
    	for parameter_name in ['n_lags', 'n_estimators', 'max_depth']:
    		params[parameter_name] = int(params[parameter_name])

    	start = timer()
    	train_X, test_X, val_X, train_y, test_y, val_y = transform_values(values, params['n_lags'], n_series, 0, train_size, test_size, val_size)
    	rmse, rmse_val, _, _, _, _, _, dir_acc, _, _ = models.model_ada_boost(train_X, test_X, val_X, train_y, test_y, val_y, n_series, params['n_estimators'], params['lr'], params['max_depth'], n_features,
    														params['n_lags'], scaler, calc_val_error, calc_test_error, verbosity, False, model_file_name, returns)
    	if(returns):
    		rmse = rmse_val
    	else:
    		mean = np.mean(np.abs(val_y))
    		rmse = rmse_val/mean + (1 - dir_acc)
    	rmse = rmse_val/mean + (1 - dir_acc)
    	run_time = timer() - start
    	# print('no_score: ', rmse)
    	# print('time: ', run_time, end='\n\n')
    elif(id_model == 3):
    	if(model_file_name == None): model_file_name = dir + 'models/trials-svm.joblib'
    	# Make sure parameters that need to be integers are integers
    	for parameter_name in ['n_lags']:
    		params[parameter_name] = int(params[parameter_name])

    	start = timer()
    	train_X, test_X, val_X, train_y, test_y, val_y = transform_values(values, params['n_lags'], n_series, 0, train_size, test_size, val_size)
    	rmse, rmse_val, _, _, _, _, _, dir_acc, _, _ = models.model_svm(train_X, test_X, val_X, train_y, test_y, val_y, n_series, n_features, params['n_lags'], scaler, calc_val_error, calc_test_error,
    												verbosity, False, model_file_name, returns)
    	if(returns):
    		rmse = rmse_val
    	else:
    		mean = np.mean(np.abs(val_y))
    		rmse = rmse_val/mean + (1 - dir_acc)
    		rmse = rmse_val/mean + (1 - dir_acc)
    	run_time = timer() - start
    	# print('no_score: ', rmse)
    	# print('time: ', run_time, end='\n\n')
    elif(id_model == 4):
    	if(model_file_name == None): model_file_name = dir + 'models/arima.pkl'
    	# Make sure parameters that need to be integers are integers
    	for parameter_name in ['n_lags', 'd', 'q']:
    		params[parameter_name] = int(params[parameter_name])

    	start = timer()
    	wall = int(len(values)*0.6)
    	wall_val= int(len(values)*0.2)
    	train_X, test_X, val_X, last_values = values[:wall, :], values[wall:wall+wall_val,:], values[wall+wall_val:-1,:], values[-1,:]
    	train_y, test_y, val_y = values[1:wall+1,0], values[wall+1:wall+wall_val+1,0], values[wall+wall_val+1:,0]
    	start = timer()
    	rmse, rmse_val, y, y_hat, y_valset, y_hat_val, dir_acc, model, scaler = models.model_arima(train_X, test_X, val_X, train_y, test_y, val_y, n_series, params['d'], params['q'], n_features, params['n_lags'], scaler, calc_val_error,
    													calc_test_error, verbosity, False, model_file_name, returns)
    	if(returns):
    		rmse = rmse_val
    	else:
    		mean = np.mean(np.abs(val_y))
    		rmse = rmse_val/mean + (1 - dir_acc)
    	run_time = timer() - start
    	# print('no_score: ', rmse)
    	# print('time: ', run_time, end='\n\n')

    # Write to the csv file
    of_connection = open(out_file, 'a')
    writer = csv.writer(of_connection)
    writer.writerow([rmse, params, ITERATION, run_time])
    of_connection.close()

    return -1 * rmse

def bayes_optimization(id_model, MAX_EVALS, values, scaler, n_features, n_series, lr, original, verbosity, model_file_name, returns, train_size, test_size, val_size, dir='', error_type="mse", **other_params):
	"""
		Función para encontrar los parámetros óptimos para un modelo

		Parámetros:
		- id_model -- Entero, id del modelo que se va a entrenar
            [0 (neural network)]
		- MAX_EVALS -- Entero, número máximo  de iteraciones de la optimización bayesiana
		- values -- Arreglo de numpy, datos con los cuales se va a entrenar el modelo, es decir, la serie previamente preprocesada
		- scaler -- Instancia de la clase MinMaxScaler de sklearn, sirve para el escalamiento de los datos y para revertir este escalamiento
		- n_features -- Entero, número de *features* de la serie
		- n_series -- Entero, número de *time steps*
		- original -- Booleano, denota si se van a usar los *features* originales de la serie o los *features* seleccionados, en esta función serviría para identificar el archivo de salida
		- verbosity -- Entero, nivel de verbosidad de la ejecución
		- model_file_name -- String, nombre del archivo donde se guardará y/o se cargará el modelo entrenado

		Retorna:
		- best -- Diccionario, diccionario con los mejores parámetros encontrados en la optimización bayesiana
	"""
	from bayes_opt import BayesianOptimization

	global ITERATION
	ITERATION = 0

	if(id_model == 0):
		if(n_series == 1):
			space = {'batch_size': (5, 20), # depende del número de obsevaciones
					'drop_p': (0.05, 0.3),
					'n_dense': (1, 1),
					'n_epochs': (100, 200),
					'n_hidden': (5, 16),
					'n_lags': (3, 12),
					'n_rnn': (1, 1)}
		elif(n_series > 1):
			space = {'batch_size': (5, 20),
					'drop_p': (0.05, 0.3),
					'n_dense': (1, 1),
					'n_epochs': (100, 200),
					'n_hidden': (5, 16),
					'n_lags': (3, 12),
					'n_rnn': (1, 1)}
		func = lambda batch_size, drop_p, n_dense, n_epochs, n_hidden, n_lags, n_rnn: objective({'batch_size':batch_size, 'drop_p':drop_p, 'n_dense':n_dense, 'n_epochs':n_epochs, 'n_hidden':n_hidden, 'n_lags':n_lags, 'n_rnn':n_rnn}, id_model, values, scaler, n_features, n_series, lr, verbosity, model_file_name, MAX_EVALS, returns, train_size, test_size, val_size, dir, error_type, output_activation=other_params.get('output_activation', None))
	elif(id_model == 1):
		space = {'max_features': (1, n_features),
				'min_samples': (1, 20),
				'n_estimators': (10, 1000),
				'n_lags': (1, 4)}
		func = lambda max_features, min_samples, n_estimators, n_lags: objective({'max_features': max_features, 'min_samples': min_samples, 'n_estimators': n_estimators, 'n_lags': n_lags}, id_model, values, scaler, n_features, n_series, lr, verbosity, model_file_name, MAX_EVALS, returns, train_size, test_size, val_size, dir)
	elif(id_model == 2):
		space = {'lr': (0.00001, 1.0),
				'max_depth': (2, 10),
				'n_estimators': (10, 1000),
				'n_lags': (1, min(50, int(len(values)/2)))}
		func = lambda lr, max_depth, n_estimators, n_lags: objective({'lr':lr, 'max_depth': max_depth, 'n_estimators': n_estimators, 'n_lags': n_lags}, id_model, values, scaler, n_features, n_series, lr, verbosity, model_file_name, MAX_EVALS, returns, train_size, test_size, val_size, dir)
	elif(id_model == 3):
		space = {'n_lags': (1, min(50, int(len(values)/2)))}
		func = lambda  n_lags: objective({'n_lags': n_lags}, id_model, values, scaler, n_features, n_series, lr, verbosity, model_file_name, MAX_EVALS, returns, train_size, test_size, val_size, dir)
	elif(id_model == 4):
		diff_level = calculate_diff_level_for_stationarity(values, scaler, 5)
		space={'n_lags': (1, 12),
				'q': (1, 12)}
		func = lambda  n_lags, q: objective({'d': diff_level, 'n_lags': n_lags, 'q': q}, id_model, values, scaler, n_features, n_series, lr, verbosity, model_file_name, MAX_EVALS, returns, train_size, test_size, val_size, dir)

	# File to save results
	out_file = dir + 'trials/gbm_trials_' + ID_TO_MODELNAME[id_model] + '_' + str(MAX_EVALS) + '.csv'
	of_connection = open(out_file, 'w')
	writer = csv.writer(of_connection)

	# Write the headers to the file
	writer.writerow(['id_model: ' + str(id_model), 'original: ' + str(original), 'returns: ' + str(returns), 'time_steps: ' + str(n_series)])
	writer.writerow(['rmse', 'params', 'iteration', 'train_time'])
	of_connection.close()

	optimizer = BayesianOptimization(f=func, pbounds=space, verbose=2, random_state=np.random.randint(np.random.randint(100)))
	# if(id_model == 0):
	# 	#optimizer.probe(params={'activation':1.0, 'batch_size':10.0, 'drop_p':0.0, 'n_dense':0.0, 'n_epochs':300.0, 'n_hidden':50.0, 'n_lags':10.0, 'n_rnn':0.0})
	# 	#optimizer.probe(params={'activation':1.0, 'batch_size':81.0, 'drop_p':0.0, 'n_dense':0.0, 'n_epochs':200.0, 'n_hidden':250.0, 'n_lags':15.0, 'n_rnn':0.0})
	# 	#optimizer.probe(params={'activation':1.0, 'batch_size':81.0, 'drop_p':0.0, 'n_dense':0.0, 'n_epochs':200.0, 'n_hidden':269.0, 'n_lags':9.0, 'n_rnn':0.0})
	# 	#optimizer.probe(params={'activation':1.0, 'batch_size':81.0, 'drop_p':0.0, 'n_dense':0.0, 'n_epochs':200.0, 'n_hidden':269.0, 'n_lags':25.0, 'n_rnn':0.0})
	# 	optimizer.probe(params={'activation':0.0, 'batch_size':47.0, 'drop_p':0.069, 'n_dense':0.0, 'n_epochs':382.0, 'n_hidden':130.0, 'n_lags':5.0, 'n_rnn':1.0})
	# 	optimizer.probe(params={'activation':0.0, 'batch_size':47.0, 'drop_p':0.3, 'n_dense':0.0, 'n_epochs':382.0, 'n_hidden':130.0, 'n_lags':5.0, 'n_rnn':1.0})
	# 	optimizer.probe(params={'activation':0.0, 'batch_size':47.0, 'drop_p':0.5, 'n_dense':0.0, 'n_epochs':382.0, 'n_hidden':130.0, 'n_lags':5.0, 'n_rnn':1.0})
	optimizer.maximize(init_points=10, n_iter=MAX_EVALS, acq='ucb', kappa=5, alpha=1e-3)


	# store best results
	best = optimizer.max['params']
	out_file = dir + 'trials/best_' + ID_TO_MODELNAME[id_model] + '.csv'
	of_connection = open(out_file, 'a')
	writer = csv.writer(of_connection)
	if(id_model == 0):
		writer.writerow([optimizer.max['target'], best['activation'], best['batch_size'], best['drop_p'], best['n_dense'], best['n_epochs'], best['n_hidden'], best['n_lags'], best['n_rnn'], MAX_EVALS])
	elif(id_model == 1):
		writer.writerow([optimizer.max['target'], best['n_lags'], best['n_estimators'], best['max_features'], best['min_samples'], MAX_EVALS])
	elif(id_model == 2):
		writer.writerow([optimizer.max['target'], best['n_lags'], best['n_estimators'], best['lr'], best['max_depth'], MAX_EVALS])
	elif(id_model == 3):
		writer.writerow([optimizer.max['target'], best['n_lags'], MAX_EVALS])
	elif(id_model == 4):
		best.update({'d': diff_level})
		writer.writerow([optimizer.max['target'], best['d'], best['n_lags'], best['q'], MAX_EVALS])
	of_connection.close()
	return best



if __name__=="__main__":
	pass
