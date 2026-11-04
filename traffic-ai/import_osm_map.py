#!/usr/bin/env python3
"""
AURA OpenStreetMap (OSM) Importer and City Network Generator
Converts any downloaded OpenStreetMap XML file (.osm / .osm.xml) into a fully
signalized SUMO network with realistic multi-lane geometry and synthetic traffic demand.

Usage:
    python3 import_osm_map.py --osm path/to/city.osm --output my_city
    OR (to generate a realistic organic random urban city network):
    python3 import_osm_map.py --generate-organic --output organic_city
"""

import os
import sys
import subprocess
import argparse

def get_sumo_tools():
    if 'SUMO_HOME' in os.environ:
        return os.path.join(os.environ['SUMO_HOME'], 'tools')
    default_tools = '/usr/share/sumo/tools'
    if os.path.exists(default_tools):
        return default_tools
    sys.exit("Error: SUMO_HOME is not set and /usr/share/sumo/tools was not found.")

def convert_osm_to_sumo(osm_path, output_prefix):
    output_net = f"{output_prefix}.net.xml"
    print(f"🗺️ Converting OpenStreetMap file '{osm_path}' to SUMO network '{output_net}'...")
    
    # Run netconvert with industry-standard ITS optimization flags
    cmd = [
        "netconvert",
        "--osm-files", osm_path,
        "-o", output_net,
        "--geometry.remove", "true",
        "--roundabouts.guess", "true",
        "--ramps.guess", "true",
        "--junctions.join", "true",
        "--tls.guess-signals", "true",
        "--tls.discard-simple", "true",
        "--tls.join", "true",
        "--default.lanenumber", "2",
        "--default.speed", "13.89"
    ]
    subprocess.check_call(cmd)
    print(f"✅ Successfully generated SUMO network: {output_net}")
    generate_routes_and_config(output_net, output_prefix)

def generate_organic_network(output_prefix):
    output_net = f"{output_prefix}.net.xml"
    print(f"🏙️ Generating realistic organic urban city network '{output_net}'...")
    cmd = [
        "netgenerate",
        "--rand", "true",
        "--rand.iterations", "100",
        "--rand.max-distance", "250",
        "--rand.min-distance", "80",
        "--rand.min-angle", "45",
        "--default.lanenumber", "2",
        "--default-junction-type", "traffic_light",
        "-o", output_net
    ]
    subprocess.check_call(cmd)
    print(f"✅ Successfully generated organic city network: {output_net}")
    generate_routes_and_config(output_net, output_prefix)

def generate_routes_and_config(net_file, output_prefix):
    tools = get_sumo_tools()
    random_trips_py = os.path.join(tools, "randomTrips.py")
    routes_file = f"{output_prefix}.rou.xml"
    config_file = f"{output_prefix}.sumocfg"

    print(f"🚗 Generating synthetic realistic demand into '{routes_file}'...")
    cmd_trips = [
        sys.executable, random_trips_py,
        "-n", net_file,
        "-r", routes_file,
        "-e", "3600",
        "--period", "1.5",
        "--validate"
    ]
    subprocess.check_call(cmd_trips)
    print(f"✅ Successfully generated routes: {routes_file}")

    # Write .sumocfg file
    cfg_content = f"""<configuration>
    <input>
        <net-file value="{os.path.basename(net_file)}"/>
        <route-files value="{os.path.basename(routes_file)}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="3600"/>
    </time>
    <processing>
        <time-to-teleport value="-1"/>
    </processing>
</configuration>"""
    with open(config_file, "w") as f:
        f.write(cfg_content)
    print(f"✅ Master configuration created: {config_file}")
    print(f"\n🚀 Ready to run! Test with:")
    print(f"   sumo-gui -c {config_file}")

def main():
    parser = argparse.ArgumentParser(description="AURA Real-World Map Importer")
    parser.add_argument("--osm", type=str, help="Path to raw OpenStreetMap XML (.osm) file")
    parser.add_argument("--generate-organic", action="store_true", help="Generate an organic non-grid urban city network")
    parser.add_argument("--output", type=str, default="traffic-ai/real_city", help="Output prefix for generated files")
    args = parser.parse_args()

    if args.osm:
        convert_osm_to_sumo(args.osm, args.output)
    elif args.generate_organic:
        generate_organic_network(args.output)
    else:
        print("Please provide either --osm <file.osm> or --generate-organic.")
        print("Defaulting to --generate-organic...")
        generate_organic_network(args.output)

if __name__ == "__main__":
    main()
