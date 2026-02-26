# Chandy-Lamport Snapshot Simulation

class Channel:
    def init(self, src, dst):
        self.src = src
        self.dst = dst
        self.buffer = []

    def send(self, msg):
        self.buffer.append(msg)

    def receive_all(self):
        msgs = list(self.buffer)
        self.buffer.clear()
        return msgs


class Process:
    def init(self, name):
        self.name = name
        self.local_state = None
        self.recording = False
        self.incoming_channels = {}
        self.channel_states = {}
        self.received_marker_from = set()

    def attach_incoming(self, other, channel):
        self.incoming_channels[other] = channel
        self.channel_states[other] = []

    def record_local_state(self):
        self.local_state = f"Local State of {self.name}"

    def receive_marker(self, sender):
        if not self.recording:
            self.recording = True
            self.record_local_state()
            print(f"{self.name} records its local state.")

            # Start recording on all other incoming channels
            for p in self.incoming_channels:
                if p != sender:
                    self.channel_states[p] = []
            return True
        else:
            self.received_marker_from.add(sender)
            return False

    def receive_message(self, sender, msg):
        if self.recording and sender not in self.received_marker_from:
            self.channel_states[sender].append(msg)


def run_simulation():
    # Create processes
    P1 = Process("P1")
    P2 = Process("P2")
    P3 = Process("P3")

    # Create channels
    C12 = Channel("P1", "P2")
    C23 = Channel("P2", "P3")
    C31 = Channel("P3", "P1")

    # Attach incoming channels
    P2.attach_incoming("P1", C12)
    P3.attach_incoming("P2", C23)
    P1.attach_incoming("P3", C31)

    # Normal message passing before snapshot
    C12.send("M1")
    C23.send("M2")

    # Snapshot initiated at P1
    print("Snapshot initiated at P1\n")
    P1.receive_marker("P1")

    # Send marker forward
    C12.send("MARKER")
    C23.send("MARKER")
    C31.send("MARKER")

    # Deliver all messages
    for (src, dst, chan) in [
        ("P1", P2, C12),
        ("P2", P3, C23),
        ("P3", P1, C31)
    ]:
        msgs = chan.receive_all()
        for m in msgs:
            if m == "MARKER":
                dst.receive_marker(src)
            else:
                dst.receive_message(src, m)

    return P1, P2, P3


# Run simulation
P1, P2, P3 = run_simulation()

print("\n===== SNAPSHOT RESULT =====")
print("P1:", P1.local_state, P1.channel_states)
print("P2:", P2.local_state, P2.channel_states)
print("P3:", P3.local_state, P3.channel_states)