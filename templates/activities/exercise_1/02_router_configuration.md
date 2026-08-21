# Exercise 1 — Router configuration

Configure R1 and R2 from the CLI.

On each router:

1. Enter privileged EXEC mode and global configuration mode.
2. Set the IPv4 address on both connected interfaces using the table in the first tab.
3. Enable both interfaces with `no shutdown`.
4. Save the running configuration to startup configuration.

Add these static routes:

- On R1, route `192.168.20.0 255.255.255.0` through next hop `10.0.0.2`.
- On R2, route `192.168.10.0 255.255.255.0` through next hop `10.0.0.1`.

Useful verification commands:

- `show ip interface brief`
- `show ip route`
- `show running-config`

The route must point to the other router’s transit address, not directly to the remote PC.
