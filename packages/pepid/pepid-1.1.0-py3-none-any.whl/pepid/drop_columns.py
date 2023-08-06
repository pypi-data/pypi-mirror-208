import sqlite3
import sys
import os
import glob
import tqdm
import math
import struct

if __package__ is None or __package__ == '':
    import blackboard
else:
    from . import blackboard

if len(sys.argv) != 4:
    sys.stderr.write("USAGE: {} cfg {results|queries|cands}  column_name".format(sys.argv[0]))
    sys.exit(-1)

cfg = sys.argv[1]

blackboard.config.read(blackboard.here("data/default.cfg"))
blackboard.config.read(cfg)

blackboard.setup_constants()

which = sys.argv[2].lower()
col = sys.argv[3]

if which == 'results':
    import pepid_mp
    batch_size = 80 #blackboard.config['postsearch'].getint('batch size')
    log_level = blackboard.config['logging']['level'].lower()

    all_files = glob.glob(os.path.join(blackboard.config['data']['workdir'], blackboard.config['data']['database'].split('/')[-1].rsplit('.', 1)[0] + "*pepidpart*.sqlite"))

    n_total = len(all_files)

    n_batches = math.ceil(n_total / batch_size)
    nworkers = blackboard.config['postsearch'].getint('workers')
    spec = [(blackboard.here("drop_node.py"), nworkers, n_batches,
                    [struct.pack("!cI{}sc".format(len(blackboard.TMP_PATH)), bytes([0x00]), len(blackboard.TMP_PATH), blackboard.TMP_PATH.encode("utf-8"), "$".encode("utf-8")) for _ in range(nworkers)],
                    [struct.pack("!cQQI{}sc".format(len(col)), bytes([0x01]), b * batch_size, min((b+1) * batch_size, n_total), len(col), col.encode('utf-8'), "$".encode("utf-8")) for b in range(n_batches)],
                    [struct.pack("!cc", bytes([0x7f]), "$".encode("utf-8")) for _ in range(nworkers)])]

    pepid_mp.handle_nodes("Drop Column", spec, cfg_file=cfg, tqdm_silence=log_level in ['fatal', 'error', 'warning'])

elif which == 'queries':
    db = os.path.join(blackboard.config['data']['workdir'], blackboard.config['data']['database'].split('/')[-1].rsplit('.', 1)[0] + "_q.sqlite")
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE queries DROP COLUMN  {};".format(col))
    except:
        pass
    finally:
        cur.close()
        conn.close()
elif which == 'cands':
    db = os.path.join(blackboard.config['data']['workdir'], blackboard.config['data']['database'].split('/')[-1].rsplit('.', 1)[0] + "_cands.sqlite")
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE candidates DROP COLUMN  {};".format(col))
        conn.commit()
    except:
        pass
    finally:
        cur.close()
        conn.close()
else:
    blackboard.LOG.fatal("Wrong argument to {}: '{}'".format(sys.argv[0], which))
    sys.exit(-1)
