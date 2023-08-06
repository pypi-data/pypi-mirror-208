from datetime import datetime
from fabric import Connection


def td_format(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
        ("year", 60 * 60 * 24 * 365),
        ("month", 60 * 60 * 24 * 30),
        ("day", 60 * 60 * 24),
        ("hour", 60 * 60),
        ("minute", 60),
        ("second", 1),
    ]

    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            has_s = "s" if period_value != 1 else ""
            return "%s %s%s" % (period_value, period_name, has_s)
    return "0 seconds"


def generate_ssh_config(api, credentials):
    """Print an SSH config file with all the Steinwurf VPN clients."""

    config = []
    devices = api.list()
    if not devices:
        print("Not devices available.")
        return
    for device in devices:
        config.append("Host ")
        config.append(device.name)
        config.append("\n")
        config.append("    HostName ")
        config.append(device.addresses[0])
        config.append("\n")
        config.append("    User ")
        config.append(credentials.user)
        config.append("\n\n")
    return "".join(config)


def list(api, all_devices):
    devices = api.list(all_devices)
    if not devices:
        return "No devices available."

    rows = []
    for device in devices:
        rows.append(
            [
                device.name,
                device.os,
                ", ".join(device.addresses),
                "Yes" if device.online else "No",
                "Yes" if device.updateAvailable else "No",
                td_format(datetime.now() - device.lastSeen),
            ]
        )
    print(rows)
    header = ["Name", "OS", "Addresses", "Online", "Update Available", "Last Seen"]

    rows.insert(0, [""] * len(rows[0]))
    rows.insert(1, header)
    rows.insert(2, rows[0])
    format_str = []
    for i, _ in enumerate(rows[0]):
        max_col = max([len(row[i]) for row in rows]) + 1
        rows[0][i] = "-" * max_col
        format_str.append(f"{{:<{max_col}}}")
    format_str = "".join(format_str)
    output = []
    for row in rows:
        output.append(format_str.format(*row))

    output.append(f"\nShowing a total of {len(devices)} devices.")
    return "\n".join(output)


def update_tailscale(api, credentials):
    devices = api.list()
    if not devices:
        print("Not devices available.")
    for device in devices:
        if not device.online:
            print(f"Skipping {device.name} - not online.")
            continue

        if not device.self.updateAvailable:
            print(f"Skipping {device.name} - no update available.")
            continue

        if device.os == "linux":
            print(f"buildbot@{device.addresses[0]}")

            connection = Connection(
                host=device.addresses[0],
                user=credentials.user,
                connect_kwargs={"password": credentials.password},
            )

            def run_su(conn, cmd):
                conn.run(f"su - root <<!\n{credentials.password}\n{cmd}")

            run_su(connection, "apt update")
            run_su(connection, "apt install tailscale")
