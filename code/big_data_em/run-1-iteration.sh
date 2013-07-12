#!/usr/bin/env bash
input=$1
[[ -e dependencies.tar.gz ]] ||
    tar czf dependencies.tar.gz classifiers sequences util
maybe_matrices=""
if test -e initial-matrices.pkl ; then
    maybe_matrices="--file=initial-matrices.pkl"
fi

python big_data_em/parallel_em.py  \
        -r local \
        --python-archive=dependencies.tar.gz \
        --file=word_tag_dict_mapping.pkl \
        --file big_data_em/em_lib.py \
        $maybe_matrices \
        $input > tmp.pkl && mv tmp.pkl initial-matrices.pkl
