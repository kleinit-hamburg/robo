#include <gz/sim/Server.hh>
#include <gz/sim/ServerConfig.hh>
#include <iostream>
int main(int argc, char **argv) {
  if (argc != 4) {std::cerr << "WORLD ITERATIONS SEED required\n"; return 2;}
  try {
    gz::sim::ServerConfig cfg;cfg.SetSdfFile(argv[1]);cfg.SetSeed(std::stoul(argv[3]));
    gz::sim::Server server(cfg);
    if(!server.SystemCount())return 3;
    return server.Run(true,std::stoull(argv[2]),false)?0:4;
  }catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}
}
