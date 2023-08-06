import numpy
import sys
import os
import tqdm
import math

import blackboard

def tda_fdr(rescored=False):
    fname, fext = blackboard.config['data']['output'].rsplit(".", 1)
    full_fname = (fname + "." + fext) if not rescored else (fname + blackboard.config['rescoring']['suffix'] + "." + fext)
    decoy_prefix = blackboard.config['processing.db']['decoy prefix']
    topN = blackboard.config['report'].getint('max scores')

    mgf = open(blackboard.config['data']['queries'], 'r')
    qdata = {}
    for l in mgf:
        l = l.strip()
        kv = l.split('=', 1) 
        if len(kv) != 2:
            continue # skip mass/intensity pairs
        elif kv[0] == 'TITLE':
            title = kv[1]
        elif kv[0] == 'SEQ':
            qdata[title] = kv[1].replace("M(ox)", "M[15.994915]").replace("C", "C[57.0215]")

    mgf.seek(0)
    ff = mgf
    gt = {}
    i = 0
    scan_type = 'title'
    for l in ff:
        if l.startswith('TITLE='):
            title = l.strip()[len('TITLE='):]
            i += 1
        elif l.startswith('SEQ='):
            seq = l.strip()[len('SEQ='):].replace("M(ox)", "M[15.994915]" if scan_type != 'comet' else "M[15.9949]").replace("C", "C[57.0215]")
            if scan_type == 'comet':
                scan = str(i)
            elif scan_type == '3dot' or scan_type == 'broken':
                scan = title.rsplit('.', 2)[-2]
            elif scan_type == 'title':
                scan = title
            elif scan_type == 'titlespace':
                scan = title.split(" ", 1)[0]

            gt[scan] = seq

    for k in gt:
        assert(gt[k] == qdata[k])
    for k in qdata:
        assert(gt[k] == qdata[k])

    data = []

    f = open(full_fname, 'r')
    for li, l in enumerate(f):
        if li == 0:
            header = l.strip().split("\t")
        else:
            fields = l.strip().split("\t")

            score = float(fields[header.index('score')])
            title = fields[header.index('title')]
            desc = fields[header.index('desc')]
            qrow = fields[header.index('qrow')]
            candrow = fields[header.index('candrow')]
            charge = int(fields[header.index('query_charge')])
            mass = float(fields[header.index('query_mass')])
            seq = fields[header.index('seq')]
            modseq = fields[header.index('modseq')]
            if not math.isinf(score):
                th = qdata[title] != modseq
                dec = "DECOY_" in desc
                data.append((title, score, dec, not dec, th, not th, qrow, candrow, len(seq), charge, mass))

    if len(data) == 0:
        import sys # despite top-level import, this is required... wtf???
        blackboard.LOG.error("FATAL: No entries in {}!\n".format(full_fname))
        sys.exit(-1)

    dtype = [('title', object), ('score', numpy.float64), ('decoy', bool), ('not decoy', bool), ('true hit', bool), ('not true hit', bool), ('qrow', numpy.int64), ('candrow', numpy.int64), ('lgt', numpy.int32), ('charge', numpy.int32), ('mass', numpy.float32)]
    ndata = numpy.array(data, dtype=dtype)
    ndata.sort(order=['score', 'not decoy', 'true hit'])
    ndata = ndata[::-1]
    keys = numpy.unique([d[0] for d in data])
    grouped_data = {k: [] for k in keys}
    for d in ndata:
        if len(grouped_data[d['title']]) >= topN:
            continue
        grouped_data[d['title']].append(d)
    data = numpy.hstack([grouped_data[group] for group in grouped_data])

    fdr = data['decoy'].sum() / numpy.logical_not(data['decoy']).sum()

    # resort the collated subdata before further processing
    data.sort(order=['score', 'not decoy', 'true hit'])
    data = data[::-1]

    fdr_index = numpy.cumsum(numpy.logical_not(data['decoy']))
    fdr_levels = numpy.cumsum(data['decoy']).astype('float32') / numpy.maximum(1, fdr_index)
    sort_idx = numpy.argsort(fdr_levels)
    fdr_index = fdr_index[sort_idx]
    fdr_levels = fdr_levels[sort_idx]
    lgts = data['lgt'][sort_idx]
    charges = data['charge'][sort_idx]
    masses = data['mass'][sort_idx]
    scores = data['score'][sort_idx]
    fmax = fdr_index[0]
    for i in range(len(fdr_index)):
        fmax = max(fmax, fdr_index[i])
        fdr_index[i] = fmax

    if len(fdr_levels) == 0:
        blackboard.LOG.warning("Empty fdr levels in fdr report")
        fdr_levels = numpy.array([0])
        fdr_index = numpy.array([0])

    best_fdr_idx = -1
    fdr_limit = float(blackboard.config['report']['fdr threshold'])
    for i, fv in enumerate(fdr_levels):
        if fv <= fdr_limit:
            best_fdr_idx = i
        else:
            break

    blackboard.LOG.info("Overall FDR: {}; FDR range: {}-{}; Peptide count over FDR range: {}-{}; PSM@{}%: {}".format(fdr, fdr_levels.min(), fdr_levels.max(), fdr_index.min(), fdr_index.max(), int(fdr_limit * 100.), best_fdr_idx+1))

    return {
            'n_data': len(grouped_data),
            'fdr': fdr,
            'level': best_fdr_idx,
            'curve': numpy.array(list(zip(fdr_levels, fdr_index))),
            'decoy scores': data['score'][data['decoy']],
            'target scores': data['score'][numpy.logical_not(data['decoy'])],
            'spectra': data['qrow'],
            'peptides': data['candrow'],
            'lgts': lgts,
            'target lgts': data['lgt'][numpy.logical_not(data['decoy'])],
            'decoy lgts': data['lgt'][data['decoy']],
            'charges': charges,
            'target charges': data['charge'][numpy.logical_not(data['decoy'])],
            'decoy charges': data['charge'][data['decoy']],
            'masses': masses,
            'target masses': data['mass'][numpy.logical_not(data['decoy'])],
            'decoy masses': data['mass'][data['decoy']],
            'scores': scores,
            }

if __name__ == "__main__":
    if len(sys.argv) != 3:
        blackboard.LOG.error("USAGE: {} config.cfg [output|rescored]\n".format(sys.argv[0]))
        sys.exit(-1)

    blackboard.config.read("data/default.cfg")
    blackboard.config.read(sys.argv[1])

    blackboard.setup_constants()

    stats = tda_fdr(sys.argv[2].strip().lower() == 'rescored')
    fname, fext = blackboard.config['data']['output'].rsplit(".", 1)

    fdr_limit = float(blackboard.config['report']['fdr threshold'])
