#!/usr/bin/perl
# https://github.com/legitbs/scorebot/blob/master/scripts/bookworm/availability

use IO::Socket;
use IO::Select;

if ($#ARGV+1 != 1) {
	print "usage: $0 <host> <port>\n";
	exit(0);
}
my $team_ip = $ARGV[0];
my $team_port = $ARGV[1];

# connect to the service
our $sock = new IO::Socket::INET (
        PeerAddr => $team_ip,
        PeerPort => $team_port,
        Proto => 'tcp',
        timeout => 5
);
die "Could not create socket: $!\n" unless $sock;

alarm(20);

srand(time());
my $rnd = int(rand(100));

my $select = IO::Select->new();
$select->add($sock);
my $timeout = 1;

# List available books
readit();
syswrite $sock, "1\n", 2;
my $line = readit();
my @a = split(/\n/, $line);
my $book;
foreach my $b (@a) {
	if ($b =~ /^$rnd: (.*)$/) {
		$book = $1;
	}
}

# Review the random book
my $rnd2 = int(rand(100));
syswrite $sock, "3\n$rnd\n$rnd2\n", length("3\n$book\n$rnd2\n");

# Make sure the review was accepted
#print readit();
readit();
syswrite $sock, "2\n", 2;
my $line = readit();
if ($line =~ /$book/) {
	print "PASSED SLA\n";
	exit(0);
} else {
	print "FAILED SLA\n";
	exit(-1);
}
exit;

sub readit() {
	my $retval;
	my $line;
	my @ok_to_read;
        while ( @ok_to_read = $select->can_read($timeout)) {
		foreach my $socket (@ok_to_read) {
			$socket->recv($line, 10);
			$retval .= $line;
			print $line;
		}
	}
	return $retval;
}
