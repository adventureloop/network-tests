#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <netinet/udp.h>
#include <netinet/ip6.h>
#include <arpa/inet.h>
#include <netdb.h>

#define MAXBUFLEN 	65535

uint16_t interval = 2;
uint16_t sendsize = 64;
uint16_t sendcount = 2;
const char *dstport = "7";			//udp echo

void *get_in_addr(struct sockaddr *sa)                
{                                                     
    if (sa->sa_family == AF_INET) {                   
        return &(((struct sockaddr_in*)sa)->sin_addr);
    }                                                 
                                                      
    return &(((struct sockaddr_in6*)sa)->sin6_addr);  
}                                                     

int main(int argc, char *argv[])
{
	int sockfd;
	struct addrinfo hints, *servinfo, *p;
	struct sockaddr_storage their_addr;
	struct sockaddr_in sa;
	socklen_t addr_len;
	int numbytes, rv;
	int optval = 1;
	char buf[MAXBUFLEN];               
	char s[INET6_ADDRSTRLEN];
	struct timeval tv;

	if (argc != 2) {
		fprintf(stderr,"usage: send hostname \n");
		exit(1);
	}

	memset(&hints, 0, sizeof hints);
	hints.ai_family = AF_INET6;
	hints.ai_socktype = SOCK_DGRAM;

	if ((rv = getaddrinfo(argv[1], dstport, &hints, &servinfo)) != 0) {
		fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
		return 1;
	}

	// loop through all the results and make a socket
	for(p = servinfo; p != NULL; p = p->ai_next) {
		if ((sockfd = socket(p->ai_family, p->ai_socktype,
				p->ai_protocol)) == -1) {
			perror("send: socket");
			continue;
		}
		break;
	}

	if (p == NULL) {
		fprintf(stderr, "send: failed to create socket\n");
		return 2;
	}

	uint8_t option[] = { 0x11, 0x00, 0x3E, 0x04, 0x05, 0xDC, 0x00, 0x00};
	struct cmsghdr *hbhhdr;

	hbhhdr = calloc(1, sizeof(struct cmsghdr) + 8);

	hbhhdr->cmsg_len = sizeof(struct cmsghdr) + 8;
	hbhhdr->cmsg_level = IPPROTO_IPV6;
	hbhhdr->cmsg_type = IPV6_HOPOPTS;
	memcpy((uint8_t *)hbhhdr + sizeof(struct cmsghdr), option, 8);

#if 0
#define IPV6_PKTOPTIONS 25

	if ((setsockopt(sockfd, IPPROTO_IPV6, IPV6_PKTOPTIONS, &hbhhdr, 
		sizeof(struct cmsghdr)) != 0)) {
		perror("set PKT OPT failed");
		exit(0);
	}

	memset(buf, '4', sendsize);
	if ((numbytes = sendto(sockfd, buf, sendsize, 0, p->ai_addr, 
		p->ai_addrlen)) == -1) {
		perror("send: sendto");
		exit(1);
	}
	printf("send: sent %d bytes to %s\n", numbytes, argv[1]);
#endif

	struct msghdr msg;



	freeaddrinfo(servinfo);
	close(sockfd);

	return 0;
}
