# Perplexity: MLE vs add-k smoothing (lower is better)

Trained on `data/<genre>/train.txt`, evaluated on the 10% held-out `val.txt` (every word + `</s>`).
MLE = raw counts, no backoff: any unseen n-gram gets P=0, so held-out perplexity is infinite.
Add-k backs off to a shorter context when the full one was never seen; k is tuned on val.

| genre | n | MLE train | MLE val | best k | add-k train | add-k val |
|---|--:|--:|--:|--:|--:|--:|
| mystery | 2 | 49.6 | inf (28% zero-prob) | 0.005 | 90.3 | **413.7** |
| mystery | 3 | 6.2 | inf (64% zero-prob) | 0.001 | 22.1 | **879.8** |
| horror | 2 | 48.9 | inf (36% zero-prob) | 0.005 | 111.2 | **785.1** |
| horror | 3 | 4.9 | inf (73% zero-prob) | 0.005 | 75.3 | **1,562.8** |
| scifi | 2 | 46.2 | inf (30% zero-prob) | 0.005 | 94.8 | **508.8** |
| scifi | 3 | 5.3 | inf (62% zero-prob) | 0.001 | 21.0 | **797.1** |

**Reading it.** MLE fits train well (trigram ~5) but 28-73% of held-out tokens get P=0. Add-k makes
every estimate finite. With ~200k training tokens per genre, the add-k *trigram* is worse on val than
the bigram: most trigram contexts are seen only a few times, and add-k then spreads a lot of mass
uniformly over the ~14k-word vocabulary. Interpolation or Kneser-Ney would fix that; the CLI still
uses trigrams because ranking suggestions by the longest seen context reads better.

## k sweep (validation perplexity)

| genre | n | k=1 | k=0.5 | k=0.1 | k=0.05 | k=0.01 | k=0.005 | k=0.001 | k=0.0005 | k=0.0001 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| mystery | 2 | 1,610.0 | 1,167.3 | 633.9 | 528.3 | 421.6 | 413.7 | 460.8 | 509.2 | 698.7 |
| mystery | 3 | 4,006.0 | 3,136.9 | 1,774.4 | 1,425.2 | 973.5 | 888.0 | 879.8 | 962.4 | 1,455.7 |
| horror | 2 | 2,689.7 | 2,027.1 | 1,165.5 | 984.1 | 796.8 | 785.1 | 893.6 | 1,006.2 | 1,480.1 |
| horror | 3 | 5,599.4 | 4,542.2 | 2,791.4 | 2,319.1 | 1,685.0 | 1,562.8 | 1,581.0 | 1,740.7 | 2,708.3 |
| scifi | 2 | 2,081.3 | 1,532.2 | 835.2 | 688.5 | 527.9 | 508.8 | 549.1 | 602.6 | 827.9 |
| scifi | 3 | 4,499.6 | 3,528.6 | 1,959.1 | 1,547.8 | 997.6 | 880.1 | 797.1 | 837.7 | 1,166.3 |
