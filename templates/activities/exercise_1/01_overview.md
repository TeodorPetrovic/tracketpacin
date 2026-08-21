# Exercise 1 — Topology and addressing

Configure a small routed network with two routers and two PCs. PC1 is connected directly to R1, and PC2 is connected directly to R2.

Use these networks:

- R1 LAN: `192.168.10.0/24`
- R2 LAN: `192.168.20.0/24`
- Router-to-router link: `10.0.0.0/30`

The learner configuration is intentionally blank when the activity opens. Use the addressing table below as your target:

| Device | Interface | Address |
|---|---|---|
| R1 | G0/0/0 | 192.168.10.1 /24 |
| R1 | G0/0/1 | 10.0.0.1 /30 |
| R2 | G0/0/0 | 192.168.20.1 /24 |
| R2 | G0/0/1 | 10.0.0.2 /30 |
| PC1 | FastEthernet0 | 192.168.10.10 /24, gateway 192.168.10.1 |
| PC2 | FastEthernet0 | 192.168.20.10 /24, gateway 192.168.20.1 |

Keep all interfaces used by the topology enabled with `no shutdown`.
