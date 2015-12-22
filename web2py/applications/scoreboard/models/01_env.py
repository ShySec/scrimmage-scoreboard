def isGameActive():
	now = datetime.utcnow()
	if now < gameStartsAt(): return False
	if now > gameEndsAt(): return False
	return True

def isGameStarted():
	return gameStartsAt()<=datetime.utcnow()

def game_round_intervals():
	return timedelta(minutes=5)
