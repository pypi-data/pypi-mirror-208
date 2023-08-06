import sqlite3
import torch
import blackboard
import numpy
import os
import sys
import tables
import glob

from ml import length_comb_plus as length_model

model = length_model.Model()
device = 'cuda:0'
model.to(device)
model.load_state_dict(torch.load(blackboard.here('ml/best_nice_redo.pkl'), map_location=device))

blackboard.config.read('data/default.cfg')
blackboard.config.read('proteometools.cfg')
blackboard.TMP_PATH = os.path.join(blackboard.config['data']['tmpdir'], "pepidrun_all") 
blackboard.setup_constants()

ret = {}
batch = []

fname_pattern = list(filter(lambda x: len(x) > 0, blackboard.config['data']['database'].split('/')))[-1].rsplit('.', 1)[0] + "_*_pepidpart.sqlite"
fname_path = os.path.join(blackboard.TMP_PATH, fname_pattern)

files = sorted(glob.glob(fname_path))

meta = [f.replace("pepidpart.sqlite", "pepidpart_meta.sqlite") for f in files]

header = blackboard.RES_COLS

queries_file = blackboard.DB_PATH + "_q.sqlite"

tot_cnt = 0
n = 0
confusion = numpy.zeros(((length_model.GT_MAX_LGT-length_model.GT_MIN_LGT+1), (length_model.GT_MAX_LGT-length_model.GT_MIN_LGT+1)), dtype='float32')

for fi in range(len(files)):
    conn = sqlite3.connect("file:{}?cache=shared".format(files[fi]), detect_types=1, uri=True)
    conn_meta = sqlite3.connect("file:{}?cache=shared".format(meta[fi]), detect_types=1, uri=True)
    conn_query = sqlite3.connect("file:{}?cache=shared".format(queries_file), detect_types=1, uri=True)
    conn.row_factory = sqlite3.Row
    conn_meta.row_factory = sqlite3.Row
    conn_query.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur_meta = conn_meta.cursor()
    cur_query = conn_query.cursor()
    blackboard.execute(cur, "PRAGMA synchronous=OFF;")
    blackboard.execute(cur_meta, "PRAGMA synchronous=OFF;")
    blackboard.execute(cur_query, "PRAGMA synchronous=OFF;")
    blackboard.execute(cur, "PRAGMA temp_store_directory='{}';".format(blackboard.config['data']['tmpdir']))
    blackboard.execute(cur_meta, "PRAGMA temp_store_directory='{}';".format(blackboard.config['data']['tmpdir']))
    blackboard.execute(cur_query, "PRAGMA temp_store_directory='{}';".format(blackboard.config['data']['tmpdir']))

    blackboard.execute(cur, "SELECT qrow, rrow, seq FROM results;")
    fetch_batch_size = 62000 # The maximum batch size supported by the default sqlite engine is a bit more than 62000

    while True:
        print(numpy.diag(confusion).sum() / numpy.maximum(1., confusion.sum()))
        results_base = cur.fetchmany(fetch_batch_size)
        tot_cnt += len(results_base)
        results_base = [dict(r) for r in results_base]

        if len(results_base) == 0:
            break

        blackboard.execute(cur_meta, "SELECT rrow, data, qrow FROM meta WHERE rrow IN ({}) ORDER BY rrow ASC;".format(",".join([str(r['rrow']) for r in results_base])))
        blackboard.execute(cur_query, "SELECT rowid, spec, mass, meta FROM queries WHERE rowid IN ({}) ORDER BY rowid ASC;".format(",".join(numpy.unique([str(r['qrow']) for r in results_base]))))

        qmeta = cur_query.fetchall()
        qmeta = [dict(qm) for qm in qmeta]

        queries = [{k: qm[k] for k in ['spec', 'mass', 'meta', 'rowid']} for qm in qmeta]
        qmeta = {qm['rowid'] : qm['meta'] for qm in qmeta}

        for iq, query in enumerate(queries):
            spec = query['spec'].data #[:SPEC_TGT_LEN]
            spec = spec
            precmass = query['mass']

            spec_raw = numpy.zeros((length_model.SPEC_TGT_LEN,), dtype='float32')
            for mz, intens in spec:
                if mz == 0:
                    break
                if (mz * 10) >= length_model.SPEC_TGT_LEN - 0.5:
                    break
                spec_raw[int(numpy.round(mz * 10))] += intens
            max = spec_raw.max()
            if max != 0:
                spec_raw /= max

            extra = query['meta'].data

            batch.append([query['rowid'], spec_raw, precmass, extra])
            if len(batch) % 128 == 0 or (len(batch) > 0 and iq == len(queries)-1):
                spec_batch = numpy.array([b[1] for b in batch])
                precmass_batch = numpy.array([b[2] for b in batch]).reshape((-1, 1))
                lout, mout, wout, out = model(torch.FloatTensor(spec_batch).to(device), torch.FloatTensor(precmass_batch).to(device))
                preds = numpy.exp(out.view(-1, length_model.GT_MAX_LGT-length_model.GT_MIN_LGT+1).detach().cpu().numpy())
                del lout
                del mout
                del wout
                for ib in range(len(batch)):
                    ret[batch[ib][0]] = {'LgtPred': preds[ib]}
                batch = []

        results = cur_meta.fetchall()
        results = [dict(r) for r in results]

        for idata, data in enumerate(results):
            cand_lgt = len(results_base[idata]['seq'])
            #preds = numpy.asarray(qmeta[results_base[idata]['qrow']].data['LgtPred'])
            preds = ret[data['qrow']]['LgtPred']
            if length_model.GT_MIN_LGT <= cand_lgt  <= length_model.GT_MAX_LGT:
                confusion[cand_lgt-length_model.GT_MIN_LGT,preds.argmax(axis=-1)] += 1
                n += 1
            #m['LgtProb'] = preds[cand_lgt] if (length_model.GT_MIN_LGT <= cand_lgt <= length_model.GT_MAX_LGT) else 0
            #m['LgtDelta'] = m['LgtPred'] - cand_lgt
