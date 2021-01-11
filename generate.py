from workout_configs import configs
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import pdb


def set_workouts(inputs):
	# TO DO:
	# add favorites
	# add ability to record notes, time, ect
	# add p90x workouts
	# add intensity levels to exercises
	# add calories to workouts
	# setup via a database
	lower_df = pd.DataFrame()
	upper_df = pd.DataFrame()
	cardio_df = pd.DataFrame()
	cardlow_df = pd.DataFrame()
	cardup_df = pd.DataFrame()
	final_dfs = []
	if inputs['include_cardio_in_workouts']:
		sample_exercises = inputs['number_of_excercies_per_workout'] - inputs['include_cardio_in_workouts']
		cardio_sample = inputs['include_cardio_in_workouts']
	else:
		sample_exercises =inputs['number_of_excercies_per_workout']
		cardio_sample=0
	for idx, row in inputs['workouts'].iterrows():
		if row['workout_type'] == 'lower':
			lower_df = inputs['lower_body'].sample(n=sample_exercises)
			if inputs['include_cardio_in_workouts']:
				cardlow_df = inputs['cardio'].sample(n=cardio_sample)
			lower_df['date_str'] = row['date_str']
			cardlow_df['date_str'] = row['date_str']
			lower_df = pd.concat([lower_df,cardlow_df])
			final_dfs.append(lower_df)
		elif row['workout_type'] == 'upper':
			upper_df = inputs['upper_body'].sample(n=sample_exercises)
			if inputs['include_cardio_in_workouts']:
				cardup_df = inputs['cardio'].sample(n=cardio_sample)
			upper_df['date_str'] = row['date_str']
			cardup_df['date_str'] = row['date_str']
			upper_df = pd.concat([upper_df,cardup_df])
			final_dfs.append(upper_df)
		elif row['workout_type'] == 'cardio':
			cardio_df = inputs['cardio'].sample(n=sample_exercises)
			cardio_df['date_str'] = row['date_str']
			final_dfs.append(cardio_df)
	final_df = pd.concat(final_dfs)
	final_df = pd.merge(inputs['workouts'],final_df, how='left', on='date_str')
	final_df['frequency'] = 'As many rounds as possible (AMRAP) - in 45 minutes'
	yoga_workouts = round(inputs['pct_days_yoga']* inputs['days_to_generate'])
	dates = np.random.choice(final_df.date_str.unique(),yoga_workouts)
	for date in dates:
		new_df = final_df.loc[final_df.date_str == date]
		new_df['Excercise'] == 'P90x Yoga'
		new_df['Reps'] = '40'
		new_df['workout_type'] = 'yoga'
		new_df['frequency'] = "Length of video - 45 mins"
		final_df.update(new_df)
	min_df = final_df.loc[final_df.do_abs=="P90x3 Ab Ripper - 15 mins"]
	min_df['frequency'] = 'As many rounds as possible (AMRAP) - in 30 minutes'
	final_df.update(min_df)
	print(final_df)
	final_df.to_csv('weekly_workout_schedule.csv')


# def replace_p90(inputs):
# 	if inputs['include_p90x_upper']:
# 		replace_an_upper = np.random.choice([0,1], 1, p=[1-inputs['p90x_probability'],inputs['p90x_probability']])
# 		if replace_an_upper:
# 			p90_upper_df_exercise = inputs['p90x_upper'].sample(n=1)['Excercise']
# 			date = np.random.choice(final_df.date_str.unique(),1)

# 	if inputs['include_p90x_lower']:
# 		replace_a_lower = random.choices([0,1], [1-inputs['p90x_probability'],inputs['p90x_probability']])
# 		if replace_a_lower:
# 			p90_lower_df_exercise = inputs['p90x_lower'].sample(n=1)['Excercise']
# 			date = np.random.choice(final_df.date_str.unique(),1)
# 			final_df.loc[final_df.date_str == date]

def read_in_workouts(inputs):
	inputs['upper_body'] = pd.read_csv('Upper Body.csv')
	inputs['lower_body'] = pd.read_csv('Lower Body.csv')
	inputs['cardio'] = pd.read_csv('Cardio.csv')
	inputs['upper_body'] = pd.read_csv('Upper Body.csv')
	inputs['p90x_lower'] = pd.read_csv('P90x Lower Body.csv')
	inputs['p90x_upper'] = pd.read_csv('P90x Upper Body.csv')
	return inputs

def get_day(day, inputs):
	if not inputs['include_today']:
		day = day +1	
	date = datetime.now() + timedelta(days=day)
	dayofweek = inputs['days_of_week'][date.weekday()]
	print(day,date.weekday(), dayofweek)
	return date, dayofweek

def set_days(inputs):
	workouts = {}
	day_of_week_dict = inputs['days_of_week']
	ab_workouts = round(inputs['pct_days_abs']* inputs['days_to_generate'])
	cardio_workouts = round(inputs['pct_days_cardio']*inputs['days_to_generate'])
	if inputs['days_to_generate'] ==1:
		workout_type = inputs['workout_override']
		if ab_workouts>0:
			do_abs = True
		else:
			do_abs = False
		date, dayofweek = get_day(0,inputs)
		workouts[0] = {'date_str':date.strftime('%m-%d-%Y'), 'day_of_week':dayofweek, 'workout_type':workout_type, 'do_abs':do_abs}
	else:
		for day in range(inputs['days_to_generate']):
			do_abs = None
			date, dayofweek = get_day(day,inputs)
			if (day % 2) == 0:
				workout_type = 'upper'
				if ab_workouts>0:
					ab_workouts +-1
					do_abs = "P90x3 Ab Ripper - 15 mins"
				else:
					do_abs = None
			else:
				workout_type = 'lower'
			workouts[day] = {'date_str':date.strftime('%m-%d-%Y'), 'day_of_week':dayofweek, 'workout_type':workout_type, 'do_abs':do_abs}
	print(workouts.keys())
	inputs['workouts'] = pd.DataFrame.from_dict(workouts, orient='index')
	print(inputs['workouts'], print(len(workouts)))
	return inputs

# read in configs
if __name__ == "__main__":
	try:
		cmdline_inputs  = eval(str(sys.argv[1]))
	except Exception as e:
		print("please provide user inputs")
		print(e)
		cmdline_inputs = {}
		inputs = {**cmdline_inputs,**configs}
	# read in the workouts
	inputs = read_in_workouts(inputs) 
	inputs = set_days(inputs)
	# get days and set as upper/lower/cardio/ab/yoga
	set_workouts(inputs)
	# generate upper body workouts

	# generate lower body workouts

	# generate cardio workouts

	# replace p90x upper

	# replace p90x lower

# 

