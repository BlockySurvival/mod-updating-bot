#!/usr/bin/env python3
#
# A very quick script to update BlS mods when requested
#

import collections, datetime, io, itertools, miniirc_discord, os, re, \
       subprocess, threading, time

# I am too lazy to do config files
CHANNELS = ('#<channel-id-here>',)
DISALLOWED = ('lurklite#1029',)
TOKEN = '(Discord token)'
CRASH_LOGS_DIR = '/path/to/logs/directory'

irc = miniirc_discord.Discord(TOKEN, auto_connect=False, stateless_mode=True)

lock = threading.Lock()
_logs_re = re.compile(
    r'^(?:show|give) me (?:(?:crash|error) logs?|what you got)(?: ([0-9]+))?$'
)

@irc.Handler('PRIVMSG', colon=False)
def handler(irc, hostmask, args):
    lmsg = args[1].lower().strip()
    match = _logs_re.fullmatch(lmsg)
    if match:
        if hostmask[1] in DISALLOWED:
            irc.msg(args[0], 'No')
            return
        try:
            logs = find_crash_logs(int(match.group(1) or 1))
        except Exception as exc:
            irc.msg(args[0], f'{exc.__class__.__name__}: {exc}')
            raise
        irc.msg(args[0], f'```\n{logs}\n```')
        return
    elif lmsg != 'do the thing':
        return

    if hostmask[1] in DISALLOWED:
        irc.msg(args[0], 'Do what? How dare you tell me what to do?')
        return

    if lock.locked():
        irc.msg(args[0], 'Please be patient! You have to wait at least 30 '
                'seconds between mod updates.')
        return

    with lock:
        irc.msg(args[0], 'Updating mods, just a moment...')
        print('Updating mods...')
        try:
            env = os.environ.copy()
            env['GIT_TERMINAL_PROMPT'] = '0'
            subprocess.check_call(('bash', 'update-bls-mods.sh'), env=env)
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            irc.msg(args[0], f'Uh-oh, there was a problem while updating mods!'
                    f'\n> {exc}')
            print(f'Got error while updating mods: {exc!r}')
        else:
            irc.msg(args[0], 'Alright, mods updated.')
            print('Mods updated!')
            time.sleep(30)


def read_crash_logs(fn):
    # This uses grep because I'm not sure how fast this would be in Python
    try:
        return subprocess.check_output((
            'grep', '-aP', r'^[0-9\-]+ [0-9:]+ ERROR\[Main\]: '
            r'(?!The following mods could not be found)', '--', fn,
        )).decode('utf-8', 'replace')
    except subprocess.CalledProcessError:
        return ''


_minute_re = re.compile(r'^[0-9\-]+ [0-9]{2}:[0-9]{2}:')
def _lines_to_incident(incident_lines):
    logs = '\n'.join(incident_lines)
    if len(logs) > 1990:
        logs = logs[-1990:].split('\n', 1)[-1]
    return logs


def find_crash_logs_iter():
    now = datetime.datetime.now()
    not_before = now.strftime('%m%d.txt')
    files = os.listdir(CRASH_LOGS_DIR)
    files.sort(reverse=True)

    long_ago_dt = now - datetime.timedelta(days=300)
    long_ago_ts = long_ago_dt.timestamp()

    for fn in files:
        # Ignore files that have wrapped around
        if fn > not_before:
            continue

        # Ignore files more than a year old because the logs are going to wrap
        # around which will get messy
        path = os.path.join(CRASH_LOGS_DIR, fn)
        if os.path.getmtime(path) < long_ago_ts:
            continue

        # Try and read crash logs (and if there are none skip to the next file)
        raw_logs = read_crash_logs(path).strip()
        if not raw_logs:
            continue

        # Only return logs from the same incident
        all_lines = raw_logs.split('\n')
        incident_lines = collections.deque()
        prefix = _minute_re.match(all_lines[-1]).group(0)
        for line in reversed(all_lines):
            if not line.startswith(prefix):
                # Stop processing this logfile if we encounter a crash from
                # long ago.
                dt = datetime.datetime.fromisoformat(line.split(' ', 1)[0])
                if dt < long_ago_dt:
                    break

                # Yield the current incident
                yield _lines_to_incident(incident_lines)

                # New incident
                incident_lines.clear()
                prefix = _minute_re.match(line).group(0)

            incident_lines.appendleft(line)

        # Yield the last incident
        yield _lines_to_incident(incident_lines)


def find_crash_logs(num=1):
    it = find_crash_logs_iter()
    if num > 1:
        it = itertools.islice(it, num - 1, None)
    elif num != 1:
        return 'Crash log incident numbers start at 1'

    try:
        return next(it)
    except StopIteration:
        return 'No crash logs found!'


if __name__ == '__main__':
    irc.connect()
    irc.wait_until_disconnected()
