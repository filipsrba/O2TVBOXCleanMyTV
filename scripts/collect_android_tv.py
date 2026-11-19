#!/usr/bin/env python3
"""Explicit-target, read-only Android TV snapshot. Python 3.9+, no dependencies."""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import time
import zipfile

BASELINE = {
    "properties": ["getprop"],
    "global": ["settings", "list", "global"],
    "secure": ["settings", "--user", "0", "list", "secure"],
    "system": ["settings", "--user", "0", "list", "system"],
    "packages": ["pm", "list", "packages", "-f", "-U", "--show-versioncode"],
    "disabled": ["pm", "list", "packages", "-d"],
    "package_details": ["dumpsys", "package"],
    "home": ["cmd", "package", "resolve-activity", "--brief", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"],
    "home_candidates": ["cmd", "package", "query-activities", "--brief", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"],
    "preferred": ["dumpsys", "package", "preferred-xml"],
    "accessibility": ["dumpsys", "accessibility"],
    "oneplay": ["dumpsys", "package", "cz.o2.o2tv"],
    "control_device": ["dumpsys", "package", "com.control.device"],
    "launcher": ["dumpsys", "package", "com.gathin.tvhome"],
    "launcher_services": ["dumpsys", "activity", "services", "com.gathin.tvhome"],
    "launcher_appops": ["cmd", "appops", "get", "com.gathin.tvhome"],
    "launcher_theme_files": ["ls", "-la", "/sdcard/Android/data/com.gathin.tvhome/files"],
    "launcher_theme_config": ["cat", "/sdcard/Android/data/com.gathin.tvhome/files/config.json"],
    "zte_watchdog": ["logcat", "-d", "-v", "threadtime", "-s", "[ZteKeyInterceptorReceiver]:D"],
}
COMMON = {
    "device_time": ["date"],
    "uptime": ["uptime"],
    "model": ["getprop", "ro.product.device"],
    "fingerprint": ["getprop", "ro.build.fingerprint"],
    "memory": ["cat", "/proc/meminfo"],
    "process_memory": ["dumpsys", "meminfo"],
    "cpu": ["dumpsys", "cpuinfo"],
    "data_space": ["df", "-k", "/data"],
    "thermal": ["dumpsys", "thermalservice"],
    "ethernet": ["dumpsys", "ethernet"],
    "network_counters": ["cat", "/proc/net/dev"],
    "activity": ["dumpsys", "activity", "activities"],
    "power": ["dumpsys", "power"],
}
STREAMING = {
    "services": ["dumpsys", "-l"],
    "media_resources": ["dumpsys", "media.resource_manager"],
    "media_metrics": ["dumpsys", "media.metrics"],
    "drm_manager": ["dumpsys", "drm.drmManager"],
    "hdmi": ["dumpsys", "hdmi_control"],
    "hdcp": ["cat", "/sys/class/amhdmitx/amhdmitx0/hdcp_mode"],
    "crash_log": ["logcat", "-b", "crash", "-d", "-v", "threadtime"],
    "recent_log": ["logcat", "-b", "main", "-b", "system", "-d", "-v", "threadtime", "-t", "3000"],
}
REQUIRED = {
    "baseline": {"model", "fingerprint", "properties", "global", "secure", "system", "packages", "disabled", "package_details", "home", "home_candidates", "preferred", "accessibility", "oneplay", "control_device"},
    "streaming": {"device_time", "uptime", "model", "fingerprint", "memory", "process_memory", "recent_log", "crash_log", "media_metrics", "media_resources"},
}
PACKAGE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+$")
SERIAL = re.compile(r"^[A-Za-z0-9\[][A-Za-z0-9_.:\[\]-]{0,250}$")


def streaming_queries(apps=()):
    queries = dict(STREAMING)
    for package in dict.fromkeys(apps or ("com.disney.disneyplus", "com.wbd.stream")):
        if not PACKAGE.fullmatch(package):
            raise ValueError("Invalid streaming app identifier")
        queries["app-exit-" + package] = ["dumpsys", "activity", "exit-info", package]
        queries["app-package-" + package] = ["dumpsys", "package", package]
    return queries


def now():
    return dt.datetime.now().astimezone().isoformat()


def digest(path):
    with path.open("rb") as stream:
        sha = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def settings_map(text):
    # Preserve empty strings and absent keys; never turn the string "null" into absence.
    return dict(line.split("=", 1) for line in text.splitlines() if "=" in line)


def apk_name(remote):
    path = pathlib.PurePosixPath(remote)
    if (not re.fullmatch(r"/(?:data/app|system|system_ext|product|vendor|odm)/[A-Za-z0-9_./~+=-]+\.apk", remote)
            or ".." in path.parts or not re.fullmatch(r"[A-Za-z0-9_.-]+\.apk", path.name)):
        raise ValueError("Unexpected APK path; refusing to copy it")
    return path.name


class Collector:
    def __init__(self, adb, serial, out, timeout=30, runner=subprocess.run):
        if not SERIAL.fullmatch(serial):
            raise ValueError("Supply one explicit ADB serial, without whitespace or shell syntax")
        if timeout < 1 or timeout > 60:
            raise ValueError("Timeout must be 1–60 seconds per read")
        self.adb = str(pathlib.Path(adb).resolve())
        self.serial, self.out, self.timeout, self.runner = serial, pathlib.Path(out).resolve(), timeout, runner
        self.failures, self.outputs = [], {}
        if not pathlib.Path(self.adb).is_file():
            raise ValueError("ADB executable path does not exist")
        self.out.mkdir(parents=True, exist_ok=False)

    def capture(self, name, args):
        argv = [self.adb, "-s", self.serial] + list(args)
        started, timer = now(), time.monotonic()
        try:
            result = self.runner(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=self.timeout, check=False)
            code, stdout, stderr = result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired as exc:
            code, stdout, stderr = 124, exc.stdout or b"", (exc.stderr or b"") + b"\nTimed out"
        except OSError as exc:
            code, stdout, stderr = 126, b"", str(exc).encode("utf-8", "replace")
        text = stdout.decode("utf-8", "replace")
        errors = stderr.decode("utf-8", "replace")
        self.outputs[name] = text
        (self.out / (name + ".txt")).write_text(text, encoding="utf-8")
        if errors:
            (self.out / (name + ".stderr.txt")).write_text(errors, encoding="utf-8")
        combined = text + "\n" + errors
        unavailable = any(marker in combined for marker in (
            "Can't find service:", "Permission denied", "Permission Denial:",
            "DUMP TIMEOUT", "No activity found"))
        if code or unavailable:
            self.failures.append({"name": name, "exit_code": code, "unavailable": unavailable})
        record = {"started": started, "elapsed_seconds": round(time.monotonic() - timer, 3), "argv": argv,
                  "exit_code": code, "unavailable": unavailable, "file": name + ".txt"}
        with (self.out / "commands.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
        return code, text

    def check_device(self):
        code, state = self.capture("adb_state", ["get-state"])
        if code or state.strip() != "device":
            raise RuntimeError("Device unavailable/unauthorized; confirm the TV prompt, do not change ADB security")
        code, identity = self.capture("shell_identity", ["shell", "id"])
        if code or not re.search(r"\buid=2000\b", identity):
            raise RuntimeError("Expected ordinary ADB shell uid 2000; this workflow does not use root")

    def copy_apk(self, package):
        if not PACKAGE.fullmatch(package):
            raise ValueError("Invalid package identifier")
        code, text = self.capture("apk-paths-" + package, ["shell", "pm", "path", package])
        paths = [line[8:].strip() for line in text.splitlines() if line.startswith("package:")]
        if code or not paths:
            raise RuntimeError("No readable APK paths for " + package)
        for index, remote in enumerate(paths):
            name = apk_name(remote)
            target = self.out / "apks" / package / name
            if target.exists() or not target.resolve().is_relative_to(self.out):
                raise RuntimeError("APK output collision or invalid destination")
            target.parent.mkdir(parents=True, exist_ok=True)
            code, _ = self.capture("apk-pull-" + package + "-" + str(index), ["pull", remote, str(target)])
            if code or not target.is_file():
                raise RuntimeError("APK copy failed: " + package)
            with zipfile.ZipFile(target) as archive:
                if archive.testzip() is not None:
                    raise RuntimeError("Corrupt APK copy: " + package)

    def finish(self, profile, fatal=None):
        if profile == "baseline":
            baseline = {key: settings_map(self.outputs.get(key, "")) for key in ("global", "secure", "system")}
            (self.out / "settings-values.json").write_text(json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8")
        missing = sorted(REQUIRED[profile] - self.outputs.keys())
        complete = not fatal and not missing and not any(f["name"] in REQUIRED[profile] for f in self.failures)
        metadata = {"created": now(), "serial": self.serial, "profile": profile, "read_only": True,
                    "fatal_error": fatal, "failures": self.failures, "required_reads_missing": missing,
                    "required_reads_complete": bool(complete),
                    "all_requested_reads_complete": bool(complete and not self.failures),
                    "mutation_preconditions_checked": False,
                    "backs_up_private_app_storage": False, "backs_up_drm_keys": False,
                    "may_contain_logged_tokens": True, "restoration_tested": False}
        (self.out / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        (self.out / "BACKUP-LIMITS.txt").write_text(
            "Local private snapshot: may contain identifiers, URLs and account-related metadata.\n"
            "Do not publish or attach unredacted to a shared skill.\n"
            "Does not back up private app storage, DRM keys, pairing secrets or a firmware image.\n"
            "Logs can contain sensitive URLs or tokens; they are not a usable login backup.\n"
            "APK copies are not app-data backups. A checksum is not a restoration test.\n"
            "Review metadata.json and command errors before relying on this snapshot.\n", encoding="utf-8")
        manifest = {p.relative_to(self.out).as_posix(): digest(p) for p in sorted(self.out.rglob("*"))
                    if p.is_file() and p.name != "manifest-sha256.json"}
        (self.out / "manifest-sha256.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return complete


def create_archive(out):
    archive_path = out.parent / (out.name + ".zip")
    checksum_path = archive_path.with_suffix(".zip.sha256.txt")
    if archive_path.exists() or checksum_path.exists():
        raise FileExistsError("Preserve existing archive/checksum; choose a new output name")
    with zipfile.ZipFile(archive_path, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(out.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(out).as_posix())
    with zipfile.ZipFile(archive_path) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("ZIP CRC verification failed")
        manifest = json.loads(archive.read("manifest-sha256.json"))
        for name, expected in manifest.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != expected:
                raise RuntimeError("Archived checksum mismatch: " + name)
    with checksum_path.open("x", encoding="ascii") as stream:
        stream.write(digest(archive_path) + "  " + archive_path.name + "\n")
    return archive_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adb", required=True, help="Explicit local adb executable")
    parser.add_argument("--serial", required=True, help="Already authorized ADB serial (IP:port or USB serial)")
    parser.add_argument("--out", required=True, help="New local snapshot directory; existing paths are refused")
    parser.add_argument("--profile", choices=("baseline", "streaming"), default="baseline")
    parser.add_argument("--copy-apk", action="append", default=[], help="Copy APK/splits for this package; no private data")
    parser.add_argument("--app", action="append", default=[], help="Streaming app package; repeat as needed (default: Disney+ and HBO)")
    parser.add_argument("--zip", action="store_true", dest="make_zip", help="Create and verify a local ZIP")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args(argv)
    if any(not PACKAGE.fullmatch(pkg) for pkg in args.copy_apk + args.app):
        parser.error("Invalid package identifier")
    if args.app and args.profile != "streaming":
        parser.error("--app is only used with --profile streaming")
    collector = None
    try:
        collector = Collector(args.adb, args.serial, args.out, args.timeout)
        collector.check_device()
        queries = {**COMMON, **(BASELINE if args.profile == "baseline" else streaming_queries(args.app))}
        for name, command in queries.items():
            code, _ = collector.capture(name, ["shell"] + command)
            print(name + ": " + str(code))
        for package in dict.fromkeys(args.copy_apk):
            collector.copy_apk(package)
        complete = collector.finish(args.profile)
        if args.make_zip:
            print("Verified archive: " + str(create_archive(collector.out)))
        print("Snapshot: " + str(collector.out))
        return 0 if complete else 2
    except (ValueError, OSError, RuntimeError, zipfile.BadZipFile) as exc:
        if collector is not None:
            collector.finish(args.profile, fatal=str(exc))
        print("Stopped: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
