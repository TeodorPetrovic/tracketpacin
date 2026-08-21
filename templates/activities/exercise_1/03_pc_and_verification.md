# Exercise 1 — PCs and verification

Open each PC and configure the desktop IPv4 settings manually:

- PC1: IP `192.168.10.10`, mask `255.255.255.0`, gateway `192.168.10.1`.
- PC2: IP `192.168.20.10`, mask `255.255.255.0`, gateway `192.168.20.1`.

Test in this order:

1. From PC1, ping `192.168.10.1`.
2. From PC2, ping `192.168.20.1`.
3. From PC1, ping PC2 at `192.168.20.10`.
4. From PC2, ping PC1 at `192.168.10.10`.

Use **Check Results** in Packet Tracer to see the assessment score. The activity checks the device models, router CLI configuration, the PC IPv4 settings, and the required static routes. A fully correct configuration should reach 100% after the checks refresh.
