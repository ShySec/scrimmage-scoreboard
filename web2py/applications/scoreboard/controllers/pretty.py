def index():
	width = 1152
	element_width = 100 + 80
	element_height = 100 + 100
	per_row = max(5,width / (element_width+2))

	teams = []
	for team in db(db.teams.status=='active').select(orderby=db.teams.name):
		element = dict(teamname=team['name'],type='table',shorthand=team['name'])
		element['x'] = ((len(teams)%per_row)) * element_width + 60
		element['y'] = ((len(teams)/per_row)) * element_height + 100
		teams.append(element)
	return dict(teamlist=teams)
