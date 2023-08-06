# Fast Multi-scale Neighbor Embedding

This project and the codes in this repository implement fast
multi-scale neighbor embedding algorithms for nonlinear dimensionality
reduction (DR).

The fast algorithms which are implemented are described in the article
[Fast Multiscale Neighbor
Embedding](https://ieeexplore.ieee.org/document/9308987), from Cyril
de Bodt, Dounia Mulders, Michel Verleysen and John A. Lee, published
in IEEE Transactions on Neural Networks and Learning Systems, in 2020.

The implementations are provided using the python programming
language, but involve some C and Cython codes for performance
purposes.

If you use the codes in this repository or the article, please cite
as:

> C. de Bodt, D. Mulders, M. Verleysen and J. A. Lee, "Fast Multiscale
> Neighbor Embedding," in IEEE Transactions on Neural Networks and
> Learning Systems, 2020, doi: 10.1109/TNNLS.2020.3042807.

BibTeX entry:
```
@article{CdB2020FMsNE,
 author={C. {de Bodt} and D. {Mulders} and M. {Verleysen} and J. A. {Lee}},
 journal={{IEEE} Trans. Neural Netw. Learn. Syst.},
 title={{F}ast {M}ultiscale {N}eighbor {E}mbedding},
 year={2020},
 volume={},
 number={},
 pages={1-15},
 doi={10.1109/TNNLS.2020.3042807}}
 ```

## Installation

```
pip install .
```

Make sure to have Cython ('https://cython.org/', last consulted on May
30, 2020) installed on your system. For instructions, check
'https://cython.readthedocs.io/en/latest/src/quickstart/install.html'
(last consulted on May 30, 2020). Note that this web link mentions
that Cython requires a C compiler to be present on the system, and
provides further information to get such a C compiler according to
your system. Note also that Cython is available from the Anaconda
Python distribution.

## Package functionality

Neighbor Embedding

- `mssne`: nonlinear dimensionality reduction through multi-scale SNE
  (Ms SNE), as presented in the reference [2] below and summarized in
  [1]. This function enables reducing the dimension of a data
  set. Given a data set with N samples, the 'mssne' function has
  O(N**2 log(N)) time complexity. It can hence run on databases with
  up to a few thousands of samples. This function is based on the
  Cython implementations in `fmsne_implem.pyx`.

- `mstsne`: nonlinear dimensionality reduction through multi-scale
  t-SNE (Ms t-SNE), as presented in the reference [6] below and
  summarized in [1]. This function enables reducing the dimension of a
  data set. Given a data set with N samples, the 'mstsne' function has
  O(N**2 log(N)) time complexity. It can hence run on databases with
  up to a few thousands of samples. This function is based on the
  Cython implementations in `fmsne_implem.pyx`.

- `fmssne`: nonlinear dimensionality reduction through fast
  multi-scale SNE (FMs SNE), as presented in the reference [1]
  below. This function enables reducing the dimension of a data
  set. Given a data set with N samples, the 'fmssne' function has O(N
  (log(N))**2) time complexity. It can hence run on very large-scale
  databases. This function is based on the Cython implementations in
  `fmsne_implem.pyx`.

- `fmstsne`: nonlinear dimensionality reduction through fast
  multi-scale t-SNE (FMs t-SNE), as presented in the reference [1]
  below. This function enables reducing the dimension of a data
  set. Given a data set with N samples, the 'fmstsne' function has O(N
  (log(N))**2) time complexity. It can hence run on very large-scale
  databases. This function is based on the Cython implementations in
  `fmsne_implem.pyx`.

Quality control

- `eval_dr_quality`: unsupervised evaluation of the quality of a
  low-dimensional embedding, as introduced in [3, 4] and employed and
  summarized in [1, 2, 5]. This function enables computing DR quality
  assessment criteria measuring the neighborhood preservation from the
  high-dimensional space to the low-dimensional one. The documentation
  of the function explains the meaning of the criteria and how to
  interpret them. Given a data set with N samples, the
  'eval_dr_quality' function has O(N**2 log(N)) time complexity. It
  can hence run using databases with up to a few thousands of
  samples. This function is not based on the Cython implementations in
  `fmsne_implem.pyx`.

- `red_rnx_auc`: this function is similar to the `eval_dr_quality`
  function, but given a data set with N samples, the `red_rnx_auc`
  function has O(N*Kup*log(N)) time complexity, where Kup is the
  maximum neighborhood size accounted when computing the quality
  criteria. This function can hence run using much larger databases
  than `eval_dr_quality`, provided that Kup is small compared to
  N. This function is based on the Cython implementations in
  `fmsne_implem.pyx`.

Visualization of a 2-D embedding and of the quality criteria.

- `viz_2d_emb`: plot a 2-D embedding.

- `viz_qa`: depict the quality criteria computed by `eval_dr_quality`
  and `red_rnx_auc`.

The documentations of the functions describe their parameters.

The `fmsne_demo.py` file, illustrates how to use to apply fast
multi-scale neighbor embedding .


## Notations

- DR: dimensionality reduction.
- HD: high-dimensional.
- LD: low-dimensional.
- HDS: HD space.
- LDS: LD space.
- SNE: stochastic neighbor embedding.
- t-SNE: t-distributed SNE.
- Ms SNE: multi-scale SNE.
- Ms t-SNE: multi-scale t-SNE.
- BH t-SNE: Barnes-Hut t-SNE.


## References

[1] C. de Bodt, D. Mulders, M. Verleysen and J. A. Lee, "Fast
Multiscale Neighbor Embedding," in IEEE Transactions on Neural
Networks and Learning Systems, 2020, doi: 10.1109/TNNLS.2020.3042807.

[2] Lee, J. A., Peluffo-Ordóñez, D. H., & Verleysen,
M. (2015). Multi-scale similarities in stochastic neighbour embedding:
Reducing dimensionality while preserving both local and global
structure. Neurocomputing, 169, 246-261.

[3] Lee, J. A., & Verleysen, M. (2009). Quality assessment of
dimensionality reduction: Rank-based criteria. Neurocomputing,
72(7-9), 1431-1443.

[4] Lee, J. A., & Verleysen, M. (2010). Scale-independent quality
criteria for dimensionality reduction. Pattern Recognition Letters,
31(14), 2248-2257.

[5] Lee, J. A., Renard, E., Bernard, G., Dupont, P., & Verleysen,
M. (2013). Type 1 and 2 mixtures of Kullback–Leibler divergences as
cost functions in dimensionality reduction based on similarity
preservation. Neurocomputing, 112, 92-108.

[6] de Bodt, C., Mulders, D., Verleysen, M., & Lee,
J. A. (2018). Perplexity-free t-SNE and twice Student tt-SNE. In ESANN
(pp. 123-128).

[7] van der Maaten, L., & Hinton, G. (2008). Visualizing data using
t-SNE. Journal of Machine Learning Research, 9(Nov), 2579-2605.

[8] van der Maaten, L. (2014). Accelerating t-SNE using tree-based
algorithms. Journal of Machine Learning Research, 15(1), 3221-3245.

## Author

Cyril de Bodt (Human Dynamics - MIT Media Lab, and ICTEAM - UCLouvain)

@email: cdebodt __at__ mit __dot__ edu, or cyril __dot__ debodt __at__ uclouvain.be

The code was packaged by [Laurent Gatto](https://lgatto.github.io/)
(Compuational Biology and Bioinformatics - UCLouvain).

## License

Copyright <2023> Université catholique de Louvain (UCLouvain), Belgium

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
“Software”), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
