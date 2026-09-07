#include <gz/sim/Server.hh>
#include <gz/sim/ServerConfig.hh>
#include <iostream>
#include <string>

int main(int argc, char **argv)
{
  if (argc != 3) {
    std::cerr << "Usage: garden-sim-server WORLD.sdf SEED\n";
    return 2;
  }
  try {
    gz::sim::ServerConfig config;
    if (!config.SetSdfFile(argv[1])) return 2;
    config.SetSeed(std::stoul(argv[2]));
    gz::sim::Server server(config);
    if (!server.SystemCount().has_value()) return 3;
    return server.Run(true, 0, false) ? 0 : 4;
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
