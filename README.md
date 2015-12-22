# CTF scoreboard

Service monitoring and flag redemption service. Developed to closely match Defcon22 scoring service.

## Work Flow

1. team-server setup script registers team-token with scoreboard
1. team-server cron script registers team service-token with scoreboard
1. team-server cron script rotates team service-token every 5 minutes
1. players compromise other team service-tokens and redeem at the server
1. scoreboard checks team service availability and accessibility

## Requirements

	apt-get -y install git python-pip python-dev python-requests python-dateutil python-tornado
	pip install --upgrade git+https://github.com/binjitsu/binjitsu.git
	pip install requests[security]

## Installing

    ./deploy <hostname>

## Running (via Rocket)

    cd web2py
    python web2py.py -i 0.0.0.0 -p 8080 --nogui -c config/ssl/scoreboard.server.crt -k config/ssl/scoreboard.server.key --ca-cert config/ssl/scoreboard.ca.crt

## Connecting gameboxes

1. Copy `web2py/config/ssl/scrimmage_key.pub` to gamebox: `/home/ctf/.ssh/authorized_keys`
1. Register new team through signup dialog
1. Register server as admin
1. Assign server to new team
