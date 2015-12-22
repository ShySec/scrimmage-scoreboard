grid_kwargs = dict(csv=False, create=False, deletable=False, editable=False, searchable=False, details=False)

def calc_services_field(service, field):
	results = db(db.team_services.service==service.services.id).select()
	return sum(result[field] for result in results)

def index():
	db.services.points=Field.Virtual('points',lambda row:calc_services_field(row,'score'))
	db.services.captures=Field.Virtual('captures',lambda row:calc_services_field(row,'captured'))
	db.services.offlines=Field.Virtual('offlines',lambda row:calc_services_field(row,'failed'))

	headers = {'services.name':'Service','teams.name':'Team'}
	fields = map(lambda x:db.services[x],['name','port','points','captures','offlines'])
	links = [dict(header='',body=lambda row:A(BUTTON('Details'),_href=URL('view',vars=dict(id=row.id))))]

	active = SQLFORM.grid(query=(db.services.status=='active'),fields=fields,links=links,headers=headers,orderby=db.services.port|db.services.name, **grid_kwargs)
	disabled = SQLFORM.grid(query=(db.services.status=='disabled'),fields=fields,links=links,headers=headers,orderby=db.services.port|db.services.name, **grid_kwargs)
	return dict(active=active,disabled=disabled)

def view():
	service = lookupVarID('id',db.services)
	if not service: return 'uh-uh'

	headers = {'teams.name':'Team'}
	query = ((db.team_services.service==service)&(db.team_services.team==db.teams.id)&(db.teams.status=='active')&(db.services.status=='active'))
	fields = [db.teams.name,db.team_services.score,db.team_services.scored,db.team_services.failed,db.team_services.captured]
	form = SQLFORM.grid(query=query,fields=fields,headers=headers,orderby=db.teams.name, **grid_kwargs)
	return dict(service=service,form=form)
