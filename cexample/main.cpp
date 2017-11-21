#include "udp_client_server.h"

using namespace std;
int main(int argc, char* argv[])
{
	udp_client_server::udp_client* test = new udp_client_server::udp_client("127.0.0.1",5005);
	string temp = "start:30";
	const char *array = temp.c_str();
 	test->send(array, temp.size());
	return 0;	
}
