# Copyright (c) 2022 Paul Irofti <paul@irofti.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import numpy as np
from tensorflow.keras.models import load_model

from graphomaly.models.autoencoder import Autoencoder

fname = "AE_save_test.dmp"
X = np.random.randn(32, 52)
y = np.zeros((32,))
y[-1] = 1

encoder_neurons = [32, 16, 8, 4]
decoder_neurons = [8, 16, 32, 52]
optimizer = "adam"
verbose = 0
epochs = 200
clf = Autoencoder(encoder_neurons, decoder_neurons, optimizer=optimizer)

# XXX: fix required kwargs in fit!
clf.fit(X, verbose=verbose, epochs=epochs)

clf.save(fname)
clf_saved = load_model(fname)

# this should work
Y = super(Autoencoder, clf).predict(X)
scores_1 = Autoencoder._compute_scores(X, Y)
scores_2 = clf.decision_function(X)
if sum(scores_1 - scores_2) != 0:
    print("SCORES MISSMATCH")

# this should work also
y = clf_saved.predict(X)
try:
    scores = clf_saved.decision_function(X)
except AttributeError:
    print("EXCEPTION RAISED")
    Y = clf_saved.predict(X)
    scores = Autoencoder._compute_scores(X, Y)
