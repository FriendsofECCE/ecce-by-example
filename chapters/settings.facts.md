# Facts for appendix 1d: settings (not chapter text)

ECCE main e6ff4018a (9.5.3-dev), read 2026-11-14. Sources: docs/AGENTS.md
("Where the data is", "The settings files", "Data layout", "A separate state
directory"), docs/ENVIRONMENT.md (the full variable reference, 202 lines:
the appendix can follow its four sections), GETTING_STARTED.md, help/src, and
src/util/genutil/Preferences.C. UNVERIFIED = from code only.
The Preferences window itself (Organizer Edit > Preferences, its pages) is in
appendix menus-organizer (1b, already written): point there, do not repeat.

## Where things live
- `~/.ECCE` is really `$ECCE_REALUSERHOME/.ECCE`; the launchers set
  ECCE_REALUSERHOME to $HOME (AGENTS.md "A separate state directory"). Holds
  settings, machine registrations and per-user service state.
- Local data: the folder `ecce-localdata` prints, default `~/.ECCE-local`;
  layout `<data folder>/users/local/<project>/<calculation>/`; a calculation is
  a folder with `.ecce-meta` (AGENTS.md "Local data"). ECCE_LOCAL_DATA or
  Edit > Preferences > Data folder chooses it (variable wins).
- Data server mode: same layout under the server's root, reached over
  HTTP/WebDAV; URLs `http://<server>:<port>/<root>/users/<user>/<project>/<calculation>`.
- Experiment safely: `export ECCE_REALUSERHOME=$(mktemp -d); export
  ECCE_LOCAL_DATA=$ECCE_REALUSERHOME/data; ecce &` (AGENTS.md; commands need
  the same two variables).

## Preference files (per user, in ~/.ECCE, one file per program)
Every `Preferences("<Name>")` in the source is a file `<Name>` in
realUserPrefPath(), i.e. ~/.ECCE (Preferences.C). Names found:
Builder, CalcImport, CalcMgr, GromacsInputs, GromacsPrepare, MachineBrowser,
MachineRegister, MyAppColors, Organizer, PerTable, Shapes, StyleChooser,
WxFFDataConfig. What each holds (window geometry, last choices, remembered
values such as the Select Within Distance and hydrogen-bond settings): UNVERIFIED
in detail. Rule from AGENTS.md for the machine files: a user setting
REPLACES the site setting for that key, it is not added.

## Machine and code settings (AGENTS.md table, documented)
| File | Holds |
|---|---|
| MyMachines | one line per machine: name, host, procs:nodes, ssh, codes, capabilities (queues, account, limits) |
| CONFIG.<name> | code paths (`<Code>: /full/path`), modules, `<Code>Environment { }`, `<Code>Command { }`, scheduler header block |
| Queues | machines with queues; queue manager name/version; prefFile |
| <name>.Q | queues with min/max processors, runLimit (min), memLimit (MB), scratchLimit; 0 = no limit |
| MachPrefs, MachProfiles | launch defaults and allocation profiles; written by the window, not to be hand-edited |
Edit order and safety: create the machine in Register Machines first; Job
script > Advanced: edit file... opens CONFIG.<name> with a Check button; a
machine named in Queues but not registered stops ECCE from starting.
Placeholders: $nodes, $totalprocs, $ppn, $wallTime, $memory/$memoryM,
$account, $queue, $scratchDir (empty placeholder drops the request line; not
in environment variables). Help: register-machines pages (name to confirm).

## Per-user and per-session state in ~/.ECCE (documented)
| Path | What | Source |
|---|---|---|
| broker_<key> | the session's broker file (key = host + ECCE_SESSION_ID); Linux/macOS: socket path, user=local; Windows: host/port/user/password; removed when the broker ends | AGENTS.md |
| authcache_<key> | per-session login cache | ENVIRONMENT.md (ECCE_HOST) |
| session_<host> | newest live session of this account on this host; an ecce-<app> started without ECCE_SESSION_ID joins it | ENVIRONMENT.md (ECCE_SESSION_ID) |
| leases/ | each program's session lease (decides which programs still run; session end, reaper, Quit) | ENVIRONMENT.md (ECCE_SESSION_LIVENESS) |
| first-start-answer | the first-start choice (this computer or a server) | GETTING_STARTED.md |
| AddedServers | servers added in Edit > Preferences > Data > Servers (Add Server...), lines type TAB name TAB address; also `ecce-localdata servers list/add/remove` | GETTING_STARTED.md |
| RemoteServer/ | a user's own central-server client settings (DataServers, server.pem); ECCE_REMOTE_DIR points there | ENVIRONMENT.md, GETTING_STARTED.md |
| tls/server.pem | the server certificate a client trusts | GETTING_STARTED.md |
| dataserver/ (users, listen) | per-user data server: its accounts file (the broker checks logins against it) and the listen choice (loopback default; ECCE_DATASERVER_LISTEN wins) | GETTING_STARTED.md, ENVIRONMENT.md |
| mosquitto.server, mosquitto.log | marks a server account's Mosquitto broker; its log | GETTING_STARTED.md |
| cm | UNVERIFIED (mentioned in GETTING_STARTED.md and ENVIRONMENT.md; meaning not read) |
| activemq/server | legacy (ActiveMQ replaced by Mosquitto, #213); only in old notes |
| CONFIG.localhost | the local machine's code paths | help pages |

## Environment variables (docs/ENVIRONMENT.md, documented there)
User choices: ECCE_EDITOR (editor; order ECCE_EDITOR, Preferences, VISUAL,
EDITOR, vi), ECCE_BROWSER (help browser; then xdg-open etc.),
ECCE_XTERM_FONT, ECCE_GATEWAY_WINDOW (show the hidden Gateway window, adds a
Preferences page), ECCE_CODE_ORDER (codes first in Editors menu), 
ECCE_FILESIZE_WARNING (KB, default 10240), ECCE_WIREFRAME_LIMIT (5000 atoms),
ECCE_MAX_CACHED_MO (10 grids), ECCE_NO_VIZIMAGES, ECCE_SURFACE_COLOR1 /
ECCE_SURFACE_COLOR255, ECCE_ESP_RANGE, ECCE_NWCHEM_DFT_USE_B3LYP,
ECCE_JOB_CHECK, ECCE_SSH_BACKEND (libssh | openssh), ECCE_ASKPASS,
ECCE_SSH_FRONTEND_POOL, ECCE_SSH_FRONTEND_IDLE (120 s), ECCE_SSH_KEEPALIVE;
ECCE_TRANSPORT obsolete.
Deployment and site: ECCE_HOME (default /opt/ecce), ECCE_REALUSERHOME,
ECCE_REALUSER, ECCE_DATA, ECCE_SYSDIR, ECCE_TMPDIR (/tmp), ECCE_REMOTE_SERVER
(set by `ecce -remote`), ECCE_SITE_ADMIN_LOGIN, ECCE_LOCAL (`ecce --local`),
ECCE_LOCAL_DATA (wins over Preferences), ECCE_NO_MESSAGING,
ECCE_NO_DATASERVER, ECCE_DATASERVER_PORT (8096), ECCE_BROKER_PORT (8088,
central broker), ECCE_DATASERVER_LISTEN (loopback default), ECCE_HELP,
ECCE_NWCHEM_DATA, ECCE_HOST, ECCE_SESSION_ID (every `ecce` makes a new
session), ECCE_SESSION_LIVENESS; ECCE_BROKER=mosquitto and
ECCE_BROKER_LINGER (broker ends 10 s after the last program) from AGENTS.md.
site_runtime keys that look like variables (not environment variables):
ECCE_AUTO_ACCOUNTS, ECCE_STORE_TRAJECTORIES, ECCE_HIDE_MO_DIAGRAM.
Job monitoring tuning: ECCE_JOB_MAXCONNECTS (25), ECCE_JOB_MAXQUICKCONNECTS
(5), ECCE_JOB_MAXQUICKTIME (60 s), ECCE_JOB_RESTARTRESET,
ECCE_SUBMIT_TIMEOUT (120 s), ECCE_JOB_PARSE_TIMEOUT (5 min),
ECCE_JOB_PARSE_IGNORE, ECCE_JOB_MESSAGE_BODY; ECCE_JOB_COMMS obsolete.
Troubleshooting: `ecce --bug` / ECCE_BUG (bug-report folder, ECCE_BUG_DIR),
ECCE_RCOM_LOGMODE, ECCE_JOB_LOGMODE, ECCE_JOB_LOGALL, ECCE_LOG_ALL_EVENTS,
ECCE_DAV_DEBUG (writes Authorization headers to /tmp/davtraffic: warn),
ECCE_DEVELOPER (internal files, Developer menu, Builder command line and Dump
Scene Graph), ECCE_AI_DEBUG, many ECCE_DEBUG_* for one subsystem each,
ECCE_FRAME_SYNC (XWayland repaint), ECCE_NO_FIRST_START, ECCE_NO_REAP,
ECCE_REAP_QUIET; internal, do not set: ECCE_GATEWAY_LOCKED,
ECCE_INVOKE_VIEWER, ECCE_INVOKE_FROMECCE.
Capture and tests (book screenshots use them): ECCE_OPEN_PANEL=<name>,
ECCE_BUILDER_SCRIPT, ECCE_VIEWER_SCENE, ECCE_MODIAGRAM_DUMP,
ECCE_EXIT_AFTER_DUMP(_DELAY_MS), ECCE_TEST_* (suites).
Not ECCE_*: VISUAL, EDITOR, HOST, DISPLAY (only the X display, not the
session), GDK_BACKEND (=x11 under Wayland), GTK_IM_MODULE.
Not found in ENVIRONMENT.md but in CLAUDE.md/AGENTS.md: ECCE_ONE_PROCESS=1
(#983 stage 1, one GUI process; experimental), ECCE_GROMACS (UNVERIFIED
meaning).

## Command-line switches (from AGENTS.md / ENVIRONMENT.md mentions)
`ecce` (opens the Organizer), `ecce -remote` (central server), `ecce --local`,
`ecce -admin [-remote] [-l LOGIN]`, `ecce -machine` (Register Machines),
`ecce --bug`. Full list of ecce's switches: UNVERIFIED (read the `ecce`
wrapper or `ecce --help` before printing).
