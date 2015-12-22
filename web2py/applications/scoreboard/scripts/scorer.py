#!/bin/env python
# crontab ~/scoreboard/settings/ctf_crontab
# python web2py.py -M -S scoreboard -R applications/scoreboard/scripts/scorer.py -A DEBUG
import os
import sys
import logging

DEBUG=False

def score_team_service(game_round,team_service):
	if team_service.team.simulated_server:
		return score_passed_team_service(game_round,team_service)

	dts_captures = db.team_service_captures
	captures = db(dts_captures.game_round==game_round)(dts_captures.defender==team_service).select(dts_captures.attacker,distinct=True)
	if len(captures) > 0: return score_captured_team_service(game_round,team_service, captures)

	results = db.team_service_test_results
	failed_tests = db(results.game_round==game_round)(results.team_service==team_service)(results.status_code!=0).count()
	if failed_tests > 0: return score_failed_team_service(game_round,team_service)

	service_tokens = db(db.team_service_tokens.team_service == team_service)
	service_tokens = service_tokens(db.team_service_tokens.expires >= game_round.starts_at)
	service_tokens = service_tokens(db.team_service_tokens.created_on <= game_round.expires_at)
	service_tokens = service_tokens(db.team_service_tokens.status != 'invalid')
	if not service_tokens.count(): return score_invalid_team_service(game_round,team_service)

	return score_passed_team_service(game_round,team_service)

def score_passed_team_service(game_round, team_service):
	db.team_service_round_result.insert(game_round=game_round,service=team_service.service,team=team_service.team,result='passed')
	logger.debug('%-15s: %s passed SLA',team_service.service.name,team_service.team.name)
	team_service.update_record(scored=team_service.scored+1)
	game_round.update_record(passed=game_round.passed+1)
	websocket_pass(team_service.team)

def score_failed_team_service(game_round, team_service):
	game_round_service = db.game_round_services(game_round=game_round,service=team_service.service)
	if not game_round_service: return

	lost_points = min(team_service.score,game_round.teams-1)
	total_points = max(0,team_service.score - lost_points)
	point_pool = game_round_service.point_pool + lost_points
	logger.debug('%-15s: %s failed SLA for %d points (%d remain, %d pooled)',team_service.service.name,team_service.team.name,lost_points,total_points,point_pool)
	db.team_service_round_result.insert(game_round=game_round,service=team_service.service,team=team_service.team,result='failed')
	team_service.update_record(failed=team_service.failed+1,score=total_points)
	game_round_service.update_record(point_pool=point_pool)
	game_round.update_record(failed=game_round.failed+1)
	websocket_fail(team_service.team)

def score_captured_team_service(game_round, team_service, team_service_captures):
	service = team_service.service
	available_points = min(game_round.teams-1+team_service.remnants, team_service.score)
	remnants = available_points % len(team_service_captures)
	per_team_points = available_points / len(team_service_captures)
	remaining_points = team_service.score - available_points + remnants

	logger.debug('%-15s: %s flag captured by %d attackers (%d points each, %d remnants)',team_service.service.name,team_service.team.name,len(team_service_captures),per_team_points,remnants)
	for capture in team_service_captures:
		attacker_service = db.team_services(team=capture.attacker,service=service)
		if not attacker_service:
			logUserError('failed to find attacker: team=%s, service=%s',capture.attacker.name,service.name)
			continue
		attacker_service.update_record(score=attacker_service.score+per_team_points)

	db.team_service_round_result.insert(game_round=game_round,service=team_service.service,team=team_service.team,result='captured')
	team_service.update_record(captured=team_service.captured+1,score=remaining_points,remnants=remnants)
	game_round.update_record(captured=game_round.captured+1)

def score_invalid_team_service(game_round, team_service):
	logger.debug('%-15s: %s failed SLA due to expired tokens',team_service.service.name,team_service.team.name)
	return score_failed_team_service(game_round, team_service)

def distribute_point_pools(game_round):
	for game_round_service in db(db.game_round_services.game_round==game_round).select():
		if not game_round_service.point_pool: continue
		distribute_service_point_pool(game_round_service)

def distribute_service_point_pool(game_service):
	if not game_service.point_pool: return
	team_results = db.team_service_round_result
	winners = db(team_results.game_round==game_service.game_round)
	winners = winners(team_results.service==game_service.service)
	winners = winners(team_results.result=='passed').select()
	if not len(winners): return

	point_pool = game_service.point_pool
	remnant_pool = point_pool % len(winners)
	per_team_points = point_pool / len(winners)
	logger.debug('%-15s: distributing %d points to %d teams (%d each, %d remain)',game_service.service.name,point_pool,len(winners),per_team_points,remnant_pool)
	for winner in winners:
		team_service = db.team_services(service=winner.service,team=winner.team)
		team_service.update_record(score=team_service.score+per_team_points)
	game_service.update_record(point_pool=remnant_pool)

if __name__ == '__main__':
	if 'logger' not in globals():
		logger = logging.getLogger()
		logformat = "%(levelname)5s:%(module)15s.%(funcName)-20s:%(lineno)4d: %(message)s'"
		logging.basicConfig(level=logging.DEBUG,format=logformat)
	if len(sys.argv)==2: DEBUG = (sys.argv[1]=='DEBUG')
	if not DEBUG:
		if os.path.exists('.pause.services') or os.path.exists('.pause.services.scorer'):
			logger.info('skipping poll due to .pause file')
			sys.exit(0)
	unscored_rounds = db(db.game_rounds.status=='polled')(db.game_rounds.expires_at<=datetime.utcnow()).select(orderby=db.game_rounds.id)
	if not len(unscored_rounds): logger.debug('no unscored rounds')
	for game_round in unscored_rounds:
		game_round.update_record(status='scoring'); db.commit()

		logger.debug('scoring round %d',game_round.id)
		active_query = db(db.game_round_services.game_round==game_round)(db.game_round_services.service==db.team_services.service)
		active_query = active_query(db.game_round_teams.game_round==game_round)(db.game_round_teams.team==db.team_services.team)
		active_query = active_query(db.game_round_services.service==db.services.id)
		for team_service in active_query.select(db.team_services.ALL):
			score_team_service(game_round,team_service)
		distribute_point_pools(game_round)

		logger.info('scoring complete for round %d',game_round.id)
		game_round.update_record(status='scored')
	logger.info('scoring execution complete')
	db.commit()
