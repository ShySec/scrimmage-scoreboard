#!/usr/bin/perl
# https://github.com/legitbs/scorebot/blob/master/scripts/atmail/availability

use IO::Socket;
use IO::Select;

if ($#ARGV+1 != 2) {
	print "usage: $0 <host> <port>\n";
	exit(0);
}
my $timeout = 0.3;
my $team_ip = $ARGV[0];
my $team_port = $ARGV[1];

# connect to the service
our $sock = new IO::Socket::INET (
        PeerAddr => $team_ip,
        PeerPort => $team_port,
        Timeout => $timeout,
        Proto => 'tcp',
);
die "Could not create socket: $!\n" unless $sock;

alarm(20);

srand(time());

my $select = IO::Select->new();
$select->add($sock);
sleep 5;

# check the banner
my $line = readit();
if ($line !~ /^220 legitbs.net SMTP ready/) {
	print "no banner\n";
	exit(-1);
}

# send the HELO
my $host = randhost();
sendit("HELO $host.com\r\n");

# check the response
my $line = readit();
if ($line !~ /^250 Hello $host.com/) {
	print "no hello: $line\n";
	exit(-1);
}

# send an email
sendemail();

# try a turn
turn();

print "Everything ok\n";

exit 0;

sub sendemail() {

	my $user = randhost();
	my $host = randhost();
	sendit("MAIL FROM:<$user\@$host.com>\r\n");
	my $line = readit();
	if ($line !~ /^250 Ok/) {
		print "no OK from MAIL FROM: $line\n";
		exit(-1);
	}

	my $user = randhost();
	my $host = randhost();
	#sendit("RCPT TO:<$user\@$host.com>\r\n");
	sendit("RCPT TO:<joe\@legitbs.net>\r\n");
	my $line = readit();
	if ($line !~ /^250 Ok/) {
		print "no OK from RCPT TO: $line\n";
		exit(-1);
	}

	sendit("DATA\r\n");
	my $line = readit();
	if ($line !~ /^354 End data/) {
		print "no OK from start DATA: $data\n";
		exit(-1);
	}

	my $data = randhost();
	sendit("$data\r\n.\r\n");
	my $line = readit();
	if ($line !~ /^250 OK. Queued./) {
		print "no OK from DATA: $line\n";
		exit(-1);
	}
}

sub turn() {

	print "checking TURN\n";

	my $user = randhost();
	my $host = randhost();
	sendit("MAIL FROM:<$user\@$host.com>\r\n");
	my $line = readit();
	if ($line !~ /^250 Ok/) {
		print "no OK from MAIL FROM: $line\n";
		exit(-1);
	}

	my $user = randhost();
	my $host = randhost();
	#sendit("RCPT TO:<$user\@$host.com>\r\n");
	sendit("RCPT TO:<\@$host.com:joe\@legitbs.net>\r\n");
	my $line = readit();
	if ($line !~ /^250 Ok/) {
		print "no OK from RCPT TO: $line\n";
		exit(-1);
	}

	sendit("DATA\r\n");
	my $line = readit();
	if ($line !~ /^354 End data/) {
		print "no OK from start DATA: $data\n";
		exit(-1);
	}

	my $data = randhost();
	sendit("$data\r\n.\r\n");
	my $line = readit();
	if ($line !~ /^250 OK. Queued./) {
		print "no OK from DATA: $line\n";
		exit(-1);
	}

	sendit("TURN\r\n");
	my $line = readit();
	if ($line !~ /^250 Ok/) {
		print "no OK from DATA: $line\n";
		exit(-1);
	}

	my $data = randhost();
	sendit("220 $data.com\r\n");
	my $line = readit();
	if ($line !~ /^HELO/) {
		print "no OK from DATA: $line\n";
		exit(-1);
	}

	sendit("250 Hello\r\n");
	my $line = readit();
	if ($line !~ /^MAIL FROM/) {
		print "no OK from DATA: $line\n";
		exit(-1);
	}

	sendit("250 Ok\r\n");
	my $line = readit();
	if ($line !~ /^RCPT TO/) {
		print "no OK from DATA: $line\n";
		exit(-1);
	}

	sendit("250 Ok\r\n");
	my $line = readit();
	if ($line !~ /^DATA/) {
		print "no OK from DATA: $line\n";
		exit(-1);
	}

	sendit("354 Send data\r\n");
	my $line = readit();
#	if ($line !~ /^MAIL FROM/) {
#		print "no OK from DATA: $line\n";
#		exit(-1);
#	}

	sendit("250 Ok\r\n");
	my $line = readit();
	if ($line !~ /^TURN/) {
		print "no OK from DATA: $line\n";
		exit(-1);
	}

}

sub sendit() {
	my ($t) = @_;
	syswrite $sock, $t, length($t);
	print "> $t";
}

sub randhost() {
	my $string;
	my @chars = ("a".."z");
	$string .= $chars[rand @chars] for 1..rand(10)+5;
	return $string;
}

sub readit() {
	my $retval;
	my $line;
	my @ok_to_read;
	while ( @ok_to_read = $select->can_read($timeout)) {
		foreach my $socket (@ok_to_read) {
			$socket->recv($line, 100);
			$retval .= $line;
			if (length($line)==0) { last; }
			print "< $line\n";
		}
		if (length($retval)==0) { last; }
	}
	return $retval;
}
